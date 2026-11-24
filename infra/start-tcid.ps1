# Backward-compatible PowerShell wrapper for the ENI start script.
$bash = "C:\Program Files\Git\bin\bash.exe"
if (-not (Test-Path $bash)) { throw "Git Bash not found at $bash" }
& $bash "$PSScriptRoot/start-eni.sh" @args
exit $LASTEXITCODE
