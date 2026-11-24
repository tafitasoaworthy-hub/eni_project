# Déployer ENI sur Google Kubernetes Engine

Ce dossier contient les manifestes et les fichiers de construction de l'application ENI. Il utilise GKE Autopilot, Artifact Registry, Cloud Build et des disques persistants pour PostgreSQL et les fichiers déposés. L'application s'ouvre par un tunnel local Kubernetes. GKE, les builds, le registre et le stockage peuvent générer des frais.

Le projet dédié est `eni-universite-b9124bd9`. Le cluster `eni` et le registre `eni-images` sont dans la région `africa-south1`. Le domaine public est `eni-fianarantsoa.com`.

## Connexion et projet

Dans PowerShell, avec Google Cloud CLI installé :

```powershell
gcloud auth login
gcloud projects list
gcloud components install kubectl gke-gcloud-auth-plugin
```

Choisissez un projet dont la facturation est active. Le compte doit pouvoir activer les API, créer ou accéder au cluster, créer le registre et lancer Cloud Build. Le compte d'exécution de Cloud Build doit pouvoir pousser sur Artifact Registry, et le compte des nœuds GKE doit pouvoir tirer ces images. Le script laisse ces autorisations sous le contrôle de l'administrateur du projet.

## Déploiement

Depuis la racine du projet :

```powershell
.\infra\gke\deploy.ps1 -ProjectId eni-universite-b9124bd9 -Region africa-south1
kubectl -n eni exec -it deployment/backend -- python manage.py createsuperuser
kubectl -n eni port-forward service/frontend 8080:8080
```

Ouvrez http://127.0.0.1:8080 dans Chrome et laissez la commande de tunnel active. Vérifiez le contexte avec `kubectl config current-context` avant d'exécuter des commandes manuelles.

Le script construit les images, démarre PostgreSQL, exécute les migrations, puis vérifie le déploiement. Pour un projet sans cluster `eni`, ajoutez `-CreateCluster` pour autoriser sa création. Utilisez `-BuiltImageTag` pour redéployer une paire d'images ENI déjà publiée. La clé OpenAI est lue directement depuis Secret Manager via le module CSI GKE et Workload Identity, par le backend et par le job de migration. Aucun Secret Kubernetes ne contient la clé OpenAI. Le compte `eni-openai-reader` n'a l'accès qu'au secret `eni-openai-api-key`.

## Démarrer et arrêter ENI

Depuis PowerShell, utilisez `.\infra\start-eni.ps1` et `.\infra\stop-eni.ps1`. Les scripts se connectent au cluster `eni` du projet `eni-universite-b9124bd9` et ciblent le namespace `eni`. Le démarrage réapplique l'Ingress, puis démarre PostgreSQL, le backend et le frontend. L'arrêt coupe les services dans l'ordre inverse et conserve les disques persistants, les secrets et l'adresse IP réservée. `.\infra\stop-eni.ps1 -deep` supprime aussi l'Ingress pour libérer le load balancer; le démarrage le recrée. Pour simuler une action, définissez `$env:DRY_RUN = '1'` avant de lancer le script.

La base GKE démarre vide. Pour réutiliser les données WSL, prévoyez un export et une restauration PostgreSQL distincts. Cette configuration utilise une instance PostgreSQL et un disque persistant. Pour des données réelles, planifiez des sauvegardes et leur restauration.

## Déploiement automatique

Le workflow GitHub Actions `deploy-gke.yml` se déclenche à chaque push sur `main`. Il exige d'abord les scans GitGuardian, Semgrep et Checkov, construit ensuite les images et bloque leur publication si Trivy détecte une vulnérabilité haute ou critique corrigible. Après les migrations PostgreSQL et le déploiement, OWASP ZAP lance le scan dynamique du portail. Les déploiements sont exécutés l'un après l'autre. Si un commit plus récent est déjà sur `main` au moment de déployer, le workflow laisse ce commit prendre le relais.

GitHub s'authentifie auprès de Google Cloud avec Workload Identity Federation. Le compte `eni-github-deployer` peut publier dans `eni-images`, créer des tâches de migration dans l'espace Kubernetes `eni` et mettre à jour les déploiements `backend` et `frontend`. La configuration du domaine et les changements d'infrastructure se gèrent avec les commandes de ce guide.

Ajoutez la clé de scan GitGuardian dans les paramètres GitHub du dépôt, sous **Settings → Secrets and variables → Actions**, avec le nom `GITGUARDIAN_API_KEY`. Le pipeline échoue volontairement si cette clé manque ou si le scanner détecte un secret.

### Surveillance Wazuh

`infra/wazuh/agent-daemonset.yaml` déploie un agent par nœud. Créez d'abord un Secret contenant l'adresse du manager Wazuh, l'adresse du serveur d'enrôlement et le mot de passe d'enrôlement :

```sh
kubectl -n wazuh-agent create secret generic wazuh-agent-config \
  --from-literal=manager-address=ADRESSE_MANAGER \
  --from-literal=registration-address=ADRESSE_ENROLEMENT \
  --from-literal=enrollment-password='MOT_DE_PASSE'
kubectl apply -k infra/wazuh
```

Ce DaemonSet requiert les permissions d'accès aux journaux et à l'hôte recommandées par Wazuh. GKE Autopilot peut refuser ces accès privilégiés. Dans ce cas, installez l'agent sur un cluster GKE Standard ou utilisez le déploiement Wazuh Sidecar correspondant à la politique de sécurité du cluster. Semgrep, Trivy, Checkov et ZAP s'exécutent dans GitHub Actions et ne sont pas installés dans les pods applicatifs.

## Domaine public

L'IPv4 publique globale `eni-web-ip` est `34.160.139.158`. Dans la zone Cloudflare de `eni-fianarantsoa.com`, configurez un enregistrement **A** avec le nom **@**, cette adresse et le mode **DNS uniquement**. Retirez les autres enregistrements A ou AAAA du domaine racine s'ils pointent vers l'ancien serveur.

Depuis la racine, avec le contexte GKE d'ENI sélectionné :

```powershell
kubectl -n eni patch service frontend --type=merge --patch-file=infra/gke/frontend-public.yaml
kubectl -n eni apply -f infra/gke/public.yaml
kubectl -n eni get ingress,managedcertificate
```

Le manifeste configure le certificat géré par Google et la redirection HTTP vers HTTPS. Le certificat devient actif après validation du DNS public.
