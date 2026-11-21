param(
    [Parameter(Mandatory)][ValidatePattern('^[a-z][a-z0-9-]{4,28}[a-z0-9]$')][string]$ProjectId,
    [ValidatePattern('^[a-z]+-[a-z]+[0-9]$')][string]$Region = 'africa-south1',
    [ValidatePattern('^\d{14}$')][string]$BuiltImageTag,
    [switch]$CreateCluster,
    [switch]$EnableOpenAI
)
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '../..')

function Invoke-Checked {
    param([string]$Tool)
    & $Tool @args
    if ($LASTEXITCODE -ne 0) { throw "$Tool a echoue (code $LASTEXITCODE)." }
}

$cluster = 'eni'
$repository = 'eni-images'
$namespace = 'eni'
$context = "gke_${ProjectId}_${Region}_${cluster}"
$tag = $BuiltImageTag
if (!$tag) { $tag = [DateTime]::UtcNow.ToString('yyyyMMddHHmmss') }
$registry = "$Region-docker.pkg.dev/$ProjectId/$repository"
$backend = "${registry}/backend:$tag"
$frontend = "${registry}/frontend:$tag"

Invoke-Checked gcloud projects describe $ProjectId
Invoke-Checked gcloud services enable container.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com --project=$ProjectId
$clusters = Invoke-Checked gcloud container clusters list --project=$ProjectId --filter="name=$cluster AND location=$Region" '--format=value(name)'
if ($clusters -notcontains $cluster) {
    if (!$CreateCluster) { throw 'Relancez avec -CreateCluster pour autoriser la creation du cluster GKE facturable.' }
    Invoke-Checked gcloud container clusters create-auto $cluster --region=$Region --project=$ProjectId
}
Invoke-Checked gcloud container clusters get-credentials $cluster --region=$Region --project=$ProjectId
$repositories = Invoke-Checked gcloud artifacts repositories list --location=$Region --project=$ProjectId --format=json | ConvertFrom-Json
if (!($repositories | Where-Object { $_.name -like "*/$repository" })) {
    Invoke-Checked gcloud artifacts repositories create $repository --repository-format=docker --location=$Region --project=$ProjectId
}

function Invoke-Kube {
    Invoke-Checked kubectl --context=$context --namespace=$namespace @args
}

function Apply-Manifest {
    param([string]$Manifest)
    $Manifest | kubectl --context=$context --namespace=$namespace apply -f -
    if ($LASTEXITCODE -ne 0) { throw 'Application du manifeste Kubernetes impossible.' }
}

function New-SecretValue {
    $bytes = New-Object byte[] 32
    $generator = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
    [Convert]::ToBase64String($bytes)
}

function Read-OpenAIKey {
    $secure = Read-Host 'Nouvelle cle OpenAI pour GKE' -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try { [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer) }
}

function Create-SecretIfMissing {
    param([string]$Name, [scriptblock]$Values)
    $existing = Invoke-Kube get secret $Name --ignore-not-found -o name
    if ($existing) { return }
    @{
        apiVersion = 'v1'; kind = 'Secret'; metadata = @{ name = $Name }
        stringData = (& $Values)
    } | ConvertTo-Json -Depth 5 -Compress | kubectl --context=$context --namespace=$namespace create -f -
    if ($LASTEXITCODE -ne 0) {
        $existing = Invoke-Kube get secret $Name --ignore-not-found -o name
        if (!$existing) { throw "Creation du secret $Name impossible." }
    }
}

if (!$BuiltImageTag) {
    Invoke-Checked gcloud builds submit . --project=$ProjectId --config=infra/gke/cloudbuild.yaml --substitutions="_REGISTRY=$registry,_TAG=$tag"
}
Apply-Manifest '{"apiVersion":"v1","kind":"Namespace","metadata":{"name":"eni"}}'
Create-SecretIfMissing eni-postgres {
    @{ POSTGRES_DB = 'gestion_univ'; POSTGRES_USER = 'eni'; POSTGRES_PASSWORD = (New-SecretValue) }
}
Create-SecretIfMissing eni-runtime {
    $values = @{ DJANGO_SECRET_KEY = (New-SecretValue) }
    if ($EnableOpenAI) {
        $key = Read-OpenAIKey
        if (!$key) { throw 'Cle OpenAI vide.' }
        $values.OPENAI_API_KEY = $key
    }
    $values
}
Apply-Manifest @"
apiVersion: v1
kind: ConfigMap
metadata:
  name: eni-runtime
data:
  DJANGO_DEBUG: "False"
  DJANGO_ALLOWED_HOSTS: "127.0.0.1,localhost,eni-fianarantsoa.com"
  DJANGO_CSRF_TRUSTED_ORIGINS: "https://eni-fianarantsoa.com"
  DJANGO_SERVE_STATIC: "true"
  DB_ENGINE: postgresql
  POSTGRES_HOST: postgres
"@
$workloads = (Get-Content -Raw infra/gke/workloads.yaml).Replace('BACKEND_IMAGE', $backend).Replace('FRONTEND_IMAGE', $frontend)
$parts = $workloads -split '(?m)^---\r?\n'
Apply-Manifest ($parts[0..1] -join "`n---`n")
Invoke-Kube rollout status statefulset/postgres --timeout=600s
$networkPolicies = $parts | Where-Object { $_ -match '(?m)^kind: NetworkPolicy\s*$' }
Apply-Manifest ($networkPolicies -join "`n---`n")
$migration = (Get-Content -Raw infra/gke/migrate.yaml).Replace('BACKEND_IMAGE', $backend).Replace('IMAGE_TAG', $tag)
Apply-Manifest $migration
try {
    Invoke-Kube wait --for=condition=complete "job/eni-migrate-$tag" --timeout=600s
} catch {
    kubectl --context=$context --namespace=$namespace logs "job/eni-migrate-$tag"
    throw
}
$remainingWorkloads = $parts[2..($parts.Count - 1)] | Where-Object { $_ -notmatch '(?m)^kind: NetworkPolicy\s*$' }
Apply-Manifest ($remainingWorkloads -join "`n---`n")
Invoke-Kube rollout status deployment/backend --timeout=600s
Invoke-Kube rollout status deployment/frontend --timeout=600s
Invoke-Kube get pods
