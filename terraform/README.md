# AWS deployment (Terraform)

Provisions the full stack on AWS:

- **ECR** — two image repositories (backend, frontend)
- **ECS Fargate** — a cluster running two services; the frontend reaches the backend
  via **Cloud Map** service discovery (`backend.stock-ai.local:8000`)
- **RDS** — managed PostgreSQL (private; reachable only from the ECS tasks)
- **Secrets Manager** — `DATABASE_URL` and the AI keys, injected into the backend
  task at runtime (never baked into the image)
- **ALB** — public entrypoint to the frontend
- **VPC** — 2 public subnets, no NAT gateway (tasks use public IPs) to keep costs low

## Prerequisites

- Terraform >= 1.5, AWS CLI configured (`aws configure`), Docker running

## Deploy

ECS can't start a task until its image exists in ECR, so create the repos first,
push images, then apply the rest:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # optional: edit region/keys

terraform init

# 1. Create just the ECR repos
terraform apply -target=aws_ecr_repository.backend -target=aws_ecr_repository.frontend

# 2. Build + push the images
./scripts/push-images.sh

# 3. Create everything else (RDS, ECS, ALB, secrets, ...)
terraform apply

# 4. Open the app (wait ~1-2 min for the frontend task to pass health checks)
terraform output app_url
```

## Updating after a code change

```bash
./scripts/push-images.sh                       # rebuild + push
# then force the services to pull the new image (command is printed by the script)
aws ecs update-service --cluster stock-ai-cluster --service stock-ai-backend  --force-new-deployment
aws ecs update-service --cluster stock-ai-cluster --service stock-ai-frontend --force-new-deployment
```

## Setting the AI keys after apply (recommended over tfvars)

```bash
aws secretsmanager put-secret-value --secret-id stock-ai/openai-api-key    --secret-string "sk-..."
aws secretsmanager put-secret-value --secret-id stock-ai/anthropic-api-key --secret-string "sk-ant-..."
aws ecs update-service --cluster stock-ai-cluster --service stock-ai-backend --force-new-deployment
```

## Tear down (stop paying)

```bash
terraform destroy
```

> Cost note: RDS `db.t3.micro` + the ALB are the main always-on charges. Run
> `terraform destroy` when you're done demoing. There is no NAT gateway by design.
