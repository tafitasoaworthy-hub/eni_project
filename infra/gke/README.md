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

Le script construit les images, démarre PostgreSQL, exécute les migrations, puis vérifie le déploiement. Pour un projet sans cluster `eni`, ajoutez `-CreateCluster` pour autoriser sa création. Utilisez `-BuiltImageTag` pour redéployer une paire d'images ENI déjà publiée. Ajoutez `-EnableOpenAI` au premier déploiement pour saisir une nouvelle clé sans l'afficher. Les secrets sont créés une seule fois. Pour intégrer OpenAI après ce premier déploiement, faites ajouter la clé au Secret Kubernetes `eni-runtime` et redémarrez le déploiement backend.

La base GKE démarre vide. Pour réutiliser les données WSL, prévoyez un export et une restauration PostgreSQL distincts. Cette configuration utilise une instance PostgreSQL et un disque persistant. Pour des données réelles, planifiez des sauvegardes et leur restauration.

## Déploiement automatique

Le workflow GitHub Actions `deploy-gke.yml` se déclenche à chaque push sur `main`. Il construit les images du commit, les publie dans Artifact Registry, exécute les migrations PostgreSQL et vérifie la mise en ligne. Les déploiements sont exécutés l'un après l'autre. Si un commit plus récent est déjà sur `main` au moment de déployer, le workflow laisse ce commit prendre le relais.

GitHub s'authentifie auprès de Google Cloud avec Workload Identity Federation. Le compte `eni-github-deployer` peut publier dans `eni-images`, créer des tâches de migration dans l'espace Kubernetes `eni` et mettre à jour les déploiements `backend` et `frontend`. La configuration du domaine et les changements d'infrastructure se gèrent avec les commandes de ce guide.

## Domaine public

L'IPv4 publique globale `eni-web-ip` est `34.160.139.158`. Dans la zone Cloudflare de `eni-fianarantsoa.com`, configurez un enregistrement **A** avec le nom **@**, cette adresse et le mode **DNS uniquement**. Retirez les autres enregistrements A ou AAAA du domaine racine s'ils pointent vers l'ancien serveur.

Depuis la racine, avec le contexte GKE d'ENI sélectionné :

```powershell
kubectl -n eni patch service frontend --type=merge --patch-file=infra/gke/frontend-public.yaml
kubectl -n eni apply -f infra/gke/public.yaml
kubectl -n eni get ingress,managedcertificate
```

Le manifeste configure le certificat géré par Google et la redirection HTTP vers HTTPS. Le certificat devient actif après validation du DNS public.
