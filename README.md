# FastAPI Modular Monolith Todo & Analytics App
## Production GitOps & Kubernetes Deployment Guide

This repository contains a modular FastAPI application containerized with Docker, deployed onto Kubernetes (Minikube, k3s, or AWS EKS) via **Argo CD (GitOps)**, with zero-leak secret management powered by **Infisical**, and automated CI/CD driven by **Jenkins**.

---

## 🏗️ Architecture Overview

```
                      +-------------------+
                      |   Developer Git   |
                      +---------+---------+
                                | git push
                                v
                      +-------------------+
                      | GitHub Repository | (https://github.com/nileshyav/focusApp.git)
                      +----+---------+----+
                           |         ^
           Triggers Webhook|         | Updates k8s/deployment.yaml
                           v         | with [skip ci]
                      +----+---------+----+
                      | Jenkins CI Server |
                      +---------+---------+
                                | Builds & Pushes
                                v
                      +-------------------+
                      |    Docker Hub     | (inilesh/todoapp:<commit-hash>)
                      +---------+---------+
                                |
             +------------------+------------------+
             |                                     |
             v                                     v
+------------------------+             +------------------------+
|   Infisical Cloud EU   |             |   Argo CD Controller   |
| (Database, Supabase &  |             | (Watches focusApp/k8s) |
|  Docker Hub Secrets)   |             +-----------+------------+
+-----------+------------+                         | Auto-syncs manifests
            | Syncs via Universal Auth             |
            v                                      v
+---------------------------------------------------------------+
|                     Kubernetes Cluster                        |
|                                                               |
|  [Infisical Operator]                                         |
|    ├──> Creates: todoapp-secret (App Env: DATABASE_URL, etc.) |
|    └──> Creates: dockerhub-registry-secret (ImagePullSecrets) |
|                                                               |
|  [Deployment: todoapp-deployment]                             |
|    ├──> Pulls private image from Docker Hub                   |
|    └──> Injects environment variables from todoapp-secret     |
|                                                               |
|  [Service: todoapp-service] (LoadBalancer / NodePort 30080)   |
+---------------------------------------------------------------+
```

---

## 📋 Prerequisites

Before starting, ensure you have the following installed and configured:
1. **Kubernetes Cluster**: Running local cluster ([Minikube](https://minikube.sigs.k8s.io/) / [k3s](https://k3s.io/)) or [AWS EKS](https://aws.amazon.com/eks/).
2. **CLI Tools**:
   * `kubectl` (Configured to access your cluster)
   * `helm` (v3+)
   * `git`
   * `curl`
3. **Accounts**:
   * [Docker Hub](https://hub.docker.com/) account (e.g., `inilesh`)
   * [Infisical Cloud (EU Region)](https://eu.infisical.com) account
   * [Supabase](https://supabase.com/) account for PostgreSQL database

---

## 🚀 Step-by-Step Deployment Guide

---

### Step 1: Infisical Setup (Secret Management)

Infisical ensures that **no passwords, database URLs, or Docker tokens are ever committed to Git**.

#### 1.1 Add Secrets in Infisical Dashboard
1. Log in to **[eu.infisical.com](https://eu.infisical.com)**.
2. Open your project (e.g. `collage-project`).
3. Select your environment tab (**`dev`** or **`prod`**).
4. Add the following **6 secrets**:

| Key | Value / Format | Note |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://postgres.xpkdgysrehvjjktfbxzj:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require` | **Must use IPv4 Session Pooler host!** Direct connection is IPv6-only. |
| `SUPABASE_URL` | `https://xpkdgysrehvjjktfbxzj.supabase.co` | Project API URL |
| `SUPABASE_KEY` | `<your-anon-or-service-role-key>` | Supabase API key |
| `DOCKER_USERNAME`| `inilesh` | Your Docker Hub username |
| `DOCKER_PASSWORD`| `dckr_pat_...` | Docker Hub Personal Access Token |
| `DOCKER_EMAIL`   | `your-email@example.com` | Docker Hub account email |

> [!WARNING]
> Do **NOT** wrap values in double quotes inside the Infisical dashboard (e.g. enter `inilesh`, not `"inilesh"`).

#### 1.2 Configure Machine Identity (Universal Auth)
1. In your project, go to **Access Control** $\rightarrow$ **Machine Identities**.
2. Create an identity named `k8s-operator` (or assign an existing one) with the **Admin** or **Developer** role.
3. In the identity details, open **Universal Auth**:
   * Copy the **Client ID**.
   * Click **+ Add Client Secret** $\rightarrow$ Set TTL to `0` $\rightarrow$ Click **Create**.
   * Copy the generated **Client Secret** immediately.
4. Go to **Project Settings** $\rightarrow$ **General** and copy your **Project ID** (e.g., `4d03d8fb-7f72-473d-8cbd-c577d3fd42d1`).

#### 1.3 Install the Infisical Operator in Kubernetes
Run the following commands on your machine:

```bash
# Add Infisical Helm chart repository
helm repo add infisical-helm-charts 'https://dl.cloudsmith.io/public/infisical/helm-charts/helm/charts/'
helm repo update

# Install the operator controller
helm install infisical-operator infisical-helm-charts/infisical-standalone-operator
```

#### 1.4 Inject Machine Identity Credentials into Kubernetes
Create the bootstrap secret so the operator can authenticate with Infisical EU:

```bash
kubectl create secret generic infisical-auth-credentials \
  --from-literal=clientId="<YOUR_CLIENT_ID>" \
  --from-literal=clientSecret="<YOUR_CLIENT_SECRET>"
```

#### 1.5 Apply Infisical Secret Custom Resource
Ensure [`k8s/infisical-secret.yaml`](file:///home/nilesh/work/code_side/AI_project_1/k8s/infisical-secret.yaml) has your exact `projectId`:

```bash
kubectl apply -f k8s/infisical-secret.yaml
```

Verify that Infisical automatically created both Kubernetes secrets:
```bash
kubectl get secrets
```
You should see:
* `todoapp-secret` (Contains `DATABASE_URL` and `SUPABASE_*` keys)
* `dockerhub-registry-secret` (Type `kubernetes.io/dockerconfigjson` for pulling private images)

---

### Step 2: Argo CD Setup (GitOps Deployment)

Argo CD ensures that your Kubernetes cluster state is always synchronized with your GitHub repository.

#### 2.1 Install Argo CD in Cluster
Run the official one-step installation manifest:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait until all pods are running:
```bash
kubectl get pods -n argocd
```

#### 2.2 Access Argo CD Web UI
* **In Minikube**:
  ```bash
  minikube service argocd-server -n argocd
  ```
* **Or Port-Forwarding**:
  ```bash
  kubectl port-forward svc/argocd-server -n argocd 8080:443
  ```
  *(Then open `https://localhost:8080` in your browser)*.

#### 2.3 Retrieve the Initial Admin Password
Username is **`admin`**. Run this command to get the password:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

#### 2.4 Create the GitOps Application in Argo CD UI
1. Log in to the Argo CD Web UI.
2. Click **+ NEW APP** (top left) and configure:
   * **Application Name**: `todoapp`
   * **Project Name**: `default`
   * **Sync Policy**: `Automatic` (Check **Prune Resources** and **Self Heal**)
   * **Repository URL**: `https://github.com/nileshyav/focusApp.git`
   * **Revision**: `master`
   * **Path**: `k8s`
   * **Cluster URL**: `https://kubernetes.default.svc`
   * **Namespace**: `default`
3. Click **CREATE**.

Argo CD will immediately synchronize the manifests in `k8s/` and deploy the application.

---

### Step 3: Manual Deployment (Alternative to Argo CD)

If you are not using Argo CD and prefer to deploy manually via `kubectl`:

```bash
# 1. Apply Infisical Secret Custom Resource
kubectl apply -f k8s/infisical-secret.yaml

# 2. Deploy Application Pods
kubectl apply -f k8s/deployment.yaml

# 3. Deploy Service (LoadBalancer / NodePort)
kubectl apply -f k8s/service.yaml
```

---

### Step 4: Run Database Migrations

If deploying against a fresh Supabase database, run the Alembic migrations inside the running pod to create tables (`todos`, `checklist_items`, etc.):

```bash
kubectl exec -it deployment/todoapp-deployment -- alembic upgrade head
```

---

### Step 5: Access the Application

* **Minikube**:
  ```bash
  minikube service todoapp-service
  ```
* **AWS EKS / Cloud LoadBalancer**:
  ```bash
  kubectl get svc todoapp-service
  # Copy the EXTERNAL-IP and open it in your browser
  ```
* **NodePort**:
  Access via `http://<NODE-IP>:30080`.

---

## 🔄 Automated CI/CD Pipeline (Jenkins)

The pipeline defined in [`Jenkinsfile`](file:///home/nilesh/work/code_side/AI_project_1/Jenkinsfile) automates the entire GitOps release cycle:

```
[Stage 1: Prepare]            -> Extracts Git commit short hash (e.g. b35cabc)
[Stage 2: Build Image]        -> Builds multi-stage Docker image tagged with commit hash & latest
[Stage 3: Push to DockerHub]  -> Authenticates & pushes images to Docker Hub
[Stage 4: Update Manifest]    -> Updates k8s/deployment.yaml with commit hash and pushes to GitHub with [skip ci]
[Argo CD]                     -> Detects Git change & triggers zero-downtime rolling update
```

### Required Jenkins Credentials:
Ensure these two credentials exist in **Manage Jenkins** $\rightarrow$ **Credentials**:

1. **`dockerhub-cred`**:
   * **Kind**: `Username with password`
   * **Username**: Your Docker Hub username (`inilesh`)
   * **Password**: Your Docker Hub Personal Access Token (PAT)
2. **`github_secret`**:
   * **Kind**: `Secret text`
   * **Secret**: GitHub Personal Access Token with **`Contents: Read and write`** permissions.

---

## 🛠️ Common Pitfalls & Troubleshooting

### 1. `OperationalError: Network is unreachable`
* **Cause**: `DATABASE_URL` in Infisical uses direct connection (`db.<ref>.supabase.co`), which is IPv6-only. Minikube and standard Kubernetes networks do not route IPv6.
* **Fix**: Change `DATABASE_URL` in Infisical to use the **Session Pooler** domain:
  `aws-0-<region>.pooler.supabase.com:5432` with username `postgres.<project-ref>`.

### 2. `ImagePullBackOff: malformed HTTP Authorization header`
* **Cause**: Missing `"auth"` field in `.dockerconfigjson`, or secret values had double quotes.
* **Fix**: Ensure [`k8s/infisical-secret.yaml`](file:///home/nilesh/work/code_side/AI_project_1/k8s/infisical-secret.yaml) contains:
  ```yaml
  "auth":"{{ print .DOCKER_USERNAME.Value ":" .DOCKER_PASSWORD.Value | encodeBase64 }}"
  ```

### 3. Infisical `401 Invalid credentials`
* **Cause**: Mismatch between US Cloud (`app.infisical.com`) and EU Cloud (`eu.infisical.com`).
* **Fix**: Generate Universal Auth credentials on **`eu.infisical.com`** and ensure `hostAPI: https://eu.infisical.com/api` is set.
* Test with curl:
  ```bash
  curl -i -X POST https://eu.infisical.com/api/v1/auth/universal-auth/login \
    -H "Content-Type: application/json" \
    -d '{"clientId":"<CLIENT_ID>","clientSecret":"<CLIENT_SECRET>"}'
  ```

### 4. GitHub Push `403 Permission Denied` in Jenkins
* **Cause**: GitHub Fine-Grained Token has `Administration` permission instead of `Contents`.
* **Fix**: Edit the token in GitHub Settings $\rightarrow$ Personal Access Tokens $\rightarrow$ grant **`Contents: Read and write`**.

---

## 📁 Repository Structure

```
.
├── app/                      # FastAPI Modular Monolith application source code
│   ├── analytics/            # Analytics domain router, models, service
│   ├── core/                 # Config, Database engine, Auth dependencies
│   ├── pomodoro/             # Pomodoro timer domain
│   ├── todos/                # Todo management domain & repositories
│   └── users/                # User auth domain (Supabase integration)
├── templates/                # Jinja2 / HTMX frontend templates
├── static/                   # CSS, JavaScript, and assets
├── alembic/                  # Database migration scripts
├── k8s/                      # Kubernetes Manifests
│   ├── deployment.yaml       # FastAPI pod deployment (reads Infisical secrets)
│   ├── service.yaml          # Service definition (LoadBalancer & NodePort)
│   └── infisical-secret.yaml # InfisicalSecret CR (syncs DB & Docker credentials)
├── Dockerfile                # Multi-stage optimized Docker build using Astral uv
├── Jenkinsfile               # Declarative CI/CD pipeline script
└── README.md                 # Project & Deployment documentation
```
