# Secret Validator API - Complete Deployment Guide

A Python Flask API that validates user-provided secrets and logs client IPs, fully containerized with Docker and deployable on Kubernetes.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Step 1: Python Web API](#step-1-python-web-api)
- [Step 2: Docker](#step-2-docker)
- [Step 3: Kubernetes Deployment](#step-3-kubernetes-deployment)
- [Step 4 (Bonus): Internet Exposure](#step-4-bonus-internet-exposure)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

- Python 3.11+
- Docker
- kubectl
- Kubernetes cluster (minikube for local, or GKE/EKS/AKS for cloud)
- (Optional) Domain name for internet exposure

## 📁 Project Structure

```
.
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── .dockerignore           # Docker ignore file
├── deploy.sh               # Automated deployment script
├── cleanup.sh              # Cleanup script
└── k8s/                    # Kubernetes manifests
    ├── deployment.yaml     # Deployment configuration
    ├── service.yaml        # Service configuration
    ├── secret.yaml         # Secret configuration
    └── ingress.yaml        # Ingress configuration
```

## 🚀 Step 1: Python Web API

### API Endpoints

**Health Check:**
```bash
GET /health
```

**Validate Secret:**
```bash
POST /validate
Content-Type: application/json

{
  "secret": "your-secret-value"
}
```

### Running Locally (Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export SECRET_VALUE="mysecretpassword123"

# Run the application
python app.py
```

Test locally:
```bash
# Health check
curl http://localhost:5000/health

# Valid secret
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"mysecretpassword123"}'

# Invalid secret
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"wrongsecret"}'
```

## 🐳 Step 2: Docker

### Build Docker Image

```bash
docker build -t secret-validator-api:latest .
```

### Run Container Locally

```bash
# Run the container
docker run -d -p 5000:5000 \
  -e SECRET_VALUE="mysecretpassword123" \
  --name secret-validator \
  secret-validator-api:latest

# Test the container
curl http://localhost:5000/health

# View logs
docker logs secret-validator

# Check IP log inside container
docker exec secret-validator cat /app/logs/access.log

# Stop and remove
docker stop secret-validator
docker rm secret-validator
```

### Push to Container Registry (Optional)

For cloud deployment, push to a container registry:

**Docker Hub:**
```bash
docker tag secret-validator-api:latest your-username/secret-validator-api:latest
docker push your-username/secret-validator-api:latest
```

**Google Container Registry (GCR):**
```bash
docker tag secret-validator-api:latest gcr.io/your-project-id/secret-validator-api:latest
docker push gcr.io/your-project-id/secret-validator-api:latest
```

**AWS ECR:**
```bash
aws ecr get-login-password --region region | docker login --username AWS --password-stdin account-id.dkr.ecr.region.amazonaws.com
docker tag secret-validator-api:latest account-id.dkr.ecr.region.amazonaws.com/secret-validator-api:latest
docker push account-id.dkr.ecr.region.amazonaws.com/secret-validator-api:latest
```

## ☸️ Step 3: Kubernetes Deployment

### Option A: Automated Deployment (Recommended)

```bash
./deploy.sh
```

This script will:
1. Build the Docker image
2. Optionally test locally
3. Load image to minikube (if using minikube)
4. Deploy to Kubernetes cluster
5. Show deployment status and URLs

### Option B: Manual Deployment

#### Using Minikube (Local)

```bash
# Start minikube
minikube start

# Build and load image
docker build -t secret-validator-api:latest .
minikube image load secret-validator-api:latest

# Deploy to Kubernetes
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=secret-validator --timeout=120s

# Get service URL
minikube service secret-validator-service --url
```

#### Using Cloud Kubernetes (GKE/EKS/AKS)

```bash
# Ensure kubectl is configured for your cluster
kubectl config current-context

# Update deployment.yaml to use your registry image
# Change: image: secret-validator-api:latest
# To: image: gcr.io/your-project/secret-validator-api:latest

# Deploy
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Wait for external IP
kubectl get service secret-validator-service -w
```

### Verify Deployment

```bash
# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=secret-validator

# Describe pod for troubleshooting
kubectl describe pod -l app=secret-validator
```

## 🌐 Step 4 (Bonus): Internet Exposure

### Option 1: Using LoadBalancer (Cloud Providers)

The service is already configured as LoadBalancer. Get the external IP:

```bash
kubectl get service secret-validator-service
```

Access via: `http://<EXTERNAL-IP>/validate`

### Option 2: Using Ingress Controller

#### Install NGINX Ingress Controller

**Minikube:**
```bash
minikube addons enable ingress
```

**Cloud (Helm):**
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx
```

#### Deploy Ingress

1. Update `k8s/ingress.yaml` with your domain
2. Apply ingress:
```bash
kubectl apply -f k8s/ingress.yaml
```

3. Get ingress IP:
```bash
kubectl get ingress secret-validator-ingress
```

4. Configure DNS to point your domain to the ingress IP

### Option 3: Using ngrok (Quick Testing)

```bash
# Get the service port
kubectl port-forward service/secret-validator-service 5000:80

# In another terminal
ngrok http 5000
```

### Option 4: Cloud-Specific Ingress

**GKE with Cloud Load Balancer:**
```yaml
# Update ingress.yaml annotations:
kubernetes.io/ingress.class: "gce"
kubernetes.io/ingress.global-static-ip-name: "your-static-ip"
```

**AWS with ALB:**
```yaml
# Update ingress.yaml annotations:
kubernetes.io/ingress.class: "alb"
alb.ingress.kubernetes.io/scheme: internet-facing
```

## 🧪 Testing

### Local Testing

```bash
# Using localhost (port-forward)
kubectl port-forward service/secret-validator-service 8080:80

# Test
curl http://localhost:8080/health
curl -X POST http://localhost:8080/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"mysecretpassword123"}'
```

### Minikube Testing

```bash
# Get URL
SERVICE_URL=$(minikube service secret-validator-service --url)

# Test
curl $SERVICE_URL/health
curl -X POST $SERVICE_URL/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"mysecretpassword123"}'
```

### Cloud/Production Testing

```bash
# Get external IP
EXTERNAL_IP=$(kubectl get service secret-validator-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test
curl http://$EXTERNAL_IP/health
curl -X POST http://$EXTERNAL_IP/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"mysecretpassword123"}'
```

### Check Logs

```bash
# View application logs
kubectl logs -l app=secret-validator

# View logs from specific pod
POD_NAME=$(kubectl get pods -l app=secret-validator -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -- cat /app/logs/access.log
```

## 🔐 Security Considerations

1. **Change the default secret:** Edit `k8s/secret.yaml` before deploying
2. **Use sealed secrets:** For production, consider using sealed-secrets or external secret managers
3. **Enable HTTPS:** Use cert-manager with Let's Encrypt for TLS certificates
4. **Network Policies:** Implement network policies to restrict traffic
5. **RBAC:** Configure proper role-based access control

## 🛠️ Troubleshooting

### Pods not starting
```bash
kubectl describe pod -l app=secret-validator
kubectl logs -l app=secret-validator
```

### Image pull errors
```bash
# For minikube, ensure image is loaded
minikube image load secret-validator-api:latest

# For cloud, check image registry access
kubectl describe pod -l app=secret-validator
```

### Service not accessible
```bash
# Check service
kubectl get service secret-validator-service

# Check endpoints
kubectl get endpoints secret-validator-service

# Port forward for testing
kubectl port-forward service/secret-validator-service 8080:80
```

### No external IP assigned (LoadBalancer)
- Cloud providers may take 2-5 minutes to provision
- Check cloud console for load balancer status
- Verify your cluster has LoadBalancer support

## 🧹 Cleanup

```bash
# Use cleanup script
./cleanup.sh

# Or manually
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/secret.yaml

# Stop minikube
minikube stop
```

## 📝 Customization

### Change the Secret Value

Edit `k8s/secret.yaml`:
```yaml
stringData:
  secret-value: "your-new-secret"
```

Reapply:
```bash
kubectl apply -f k8s/secret.yaml
kubectl rollout restart deployment secret-validator-api
```

### Scale the Deployment

```bash
kubectl scale deployment secret-validator-api --replicas=5
```

### Update the Application

```bash
# Make changes to app.py
# Rebuild image
docker build -t secret-validator-api:latest .

# For minikube
minikube image load secret-validator-api:latest

# For cloud, push to registry
# docker push your-registry/secret-validator-api:latest

# Restart deployment
kubectl rollout restart deployment secret-validator-api
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/)

## 🎯 Success Criteria

- ✅ Flask API validates secrets and logs IPs
- ✅ Application runs in Docker container
- ✅ Deployed to Kubernetes cluster
- ✅ Accessible via LoadBalancer/Ingress
- ✅ Health checks working
- ✅ Logs persisted (within pod lifetime)

---

**Note:** For production use, consider implementing persistent volume claims (PVC) for log storage, proper log aggregation (ELK, Loki), monitoring (Prometheus), and secure secret management (HashiCorp Vault, AWS Secrets Manager).
