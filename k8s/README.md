# Kubernetes (local, via kind)

Run the full stack — Postgres + FastAPI backend + Streamlit frontend — on a local
[kind](https://kind.sigs.k8s.io/) cluster. The same manifests deploy to EKS with two
changes (see the bottom of this file).

## Prerequisites

- Docker Desktop running
- `kind` and `kubectl` installed

## 1. Build the images

kind can't see images in your local Docker registry until you load them, so build
them with explicit tags first:

```bash
docker build -f Dockerfile.backend  -t stock-ai-backend:local  .
docker build -f Dockerfile.frontend -t stock-ai-frontend:local .
```

## 2. Create the cluster and load the images

```bash
kind create cluster --name stock-ai --config k8s/kind-config.yaml
kind load docker-image stock-ai-backend:local  --name stock-ai
kind load docker-image stock-ai-frontend:local --name stock-ai
```

## 3. (Optional) Add your AI keys

Without this, the app runs in mock-analysis mode.

```bash
kubectl -n stock-ai create secret generic app-secrets \
  --from-literal=OPENAI_API_KEY=sk-... \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-...
```

(Create the namespace first with `kubectl apply -f k8s/manifests/00-namespace.yaml`,
or just run step 4 first — the Deployment references the Secret optionally.)

## 4. Deploy

```bash
kubectl apply -f k8s/manifests/
kubectl -n stock-ai get pods -w     # wait until all are Running/Ready
```

Open the dashboard at **http://localhost:8501** (mapped from the frontend NodePort
by the kind config).

## 5. (Optional) Autoscaling

The HPA needs metrics-server. On kind it requires the insecure-kubelet flag:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl -n kube-system patch deployment metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
kubectl -n stock-ai get hpa
```

## Tear down

```bash
kind delete cluster --name stock-ai
```

## What maps to EKS

These manifests are EKS-ready; moving to a real cluster means:

1. **Images** — push to ECR and change the `image:` fields from `stock-ai-*:local`
   to the ECR URIs (drop `imagePullPolicy: IfNotPresent`).
2. **Database** — drop `01-postgres.yaml` and point `DATABASE_URL` at an RDS instance
   (injected from AWS Secrets Manager). The frontend Service becomes a `LoadBalancer`
   (or an Ingress) instead of a NodePort.
