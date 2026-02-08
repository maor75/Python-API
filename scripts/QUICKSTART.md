# Quick Start Guide - Secret Validator API

## 🚀 Fast Track Deployment

### Prerequisites Check
```bash
docker --version
kubectl version --client
minikube version  # if using minikube
```

### Option 1: Automated Deployment (Easiest)
```bash
# Make scripts executable
chmod +x deploy.sh cleanup.sh test.sh

# Run automated deployment
./deploy.sh

# Test the deployment (use the URL from deploy output)
./test.sh http://<your-service-url>
```

### Option 2: Step-by-Step Manual

#### Step 1: Test Locally with Docker
```bash
# Build
docker build -t secret-validator-api:latest .

# Run
docker run -d -p 5000:5000 \
  -e SECRET_VALUE="mysecretpassword123" \
  secret-validator-api:latest

# Test
curl http://localhost:5000/health
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"mysecretpassword123"}'
```

#### Step 2: Deploy to Minikube
```bash
# Start minikube
minikube start

# Load image
minikube image load secret-validator-api:latest

# Deploy
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Get URL
minikube service secret-validator-service --url

# Test
./test.sh $(minikube service secret-validator-service --url)
```

#### Step 3: Deploy to Cloud (GKE/EKS/AKS)
```bash
# Configure kubectl for your cluster
# gcloud container clusters get-credentials <cluster> --region <region>  # GKE
# aws eks update-kubeconfig --name <cluster> --region <region>           # EKS
# az aks get-credentials --resource-group <rg> --name <cluster>          # AKS

# Push image to registry (example for GCR)
docker tag secret-validator-api:latest gcr.io/YOUR-PROJECT/secret-validator-api:latest
docker push gcr.io/YOUR-PROJECT/secret-validator-api:latest

# Update k8s/deployment.yaml line 18:
# image: gcr.io/YOUR-PROJECT/secret-validator-api:latest

# Deploy
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Wait for external IP (may take 2-5 minutes)
kubectl get service secret-validator-service -w

# Test
EXTERNAL_IP=$(kubectl get service secret-validator-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
./test.sh http://$EXTERNAL_IP
```

## 📊 Verification Commands

```bash
# Check deployment
kubectl get all -l app=secret-validator

# View logs
kubectl logs -l app=secret-validator

# Check IP logs inside pod
kubectl exec -it $(kubectl get pod -l app=secret-validator -o jsonpath='{.items[0].metadata.name}') -- cat /app/logs/access.log

# Port forward for local testing
kubectl port-forward service/secret-validator-service 8080:80
```

## 🌐 Internet Exposure (Step 4 Bonus)

### Quick: Using LoadBalancer (Already configured)
```bash
# Get external IP
kubectl get service secret-validator-service

# Access at http://<EXTERNAL-IP>/validate
```

### Advanced: Using Ingress
```bash
# Install NGINX Ingress (minikube)
minikube addons enable ingress

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Get ingress IP
kubectl get ingress secret-validator-ingress
```

### Quick Testing: Using ngrok
```bash
# Port forward
kubectl port-forward service/secret-validator-service 5000:80 &

# Expose with ngrok
ngrok http 5000
```

## 🧪 Testing Examples

```bash
# Health check
curl http://<SERVICE-URL>/health

# Valid secret (should return 200)
curl -X POST http://<SERVICE-URL>/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"mysecretpassword123"}'

# Invalid secret (should return 401)
curl -X POST http://<SERVICE-URL>/validate \
  -H "Content-Type: application/json" \
  -d '{"secret":"wrongpassword"}'

# Missing field (should return 400)
curl -X POST http://<SERVICE-URL>/validate \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 🛑 Cleanup

```bash
# Remove everything
./cleanup.sh

# Or manually
kubectl delete -f k8s/
```

## 📝 Key Files

- `app.py` - Flask application
- `Dockerfile` - Container configuration
- `k8s/deployment.yaml` - K8s deployment
- `k8s/service.yaml` - K8s service (LoadBalancer)
- `k8s/secret.yaml` - K8s secret config
- `k8s/ingress.yaml` - Ingress for domain access
- `deploy.sh` - Automated deployment
- `test.sh` - API testing script
- `README.md` - Full documentation

## 🔐 Security Notes

⚠️ **Before production:**
1. Change secret in `k8s/secret.yaml`
2. Use proper secret management (Vault, etc.)
3. Enable HTTPS/TLS
4. Implement authentication
5. Add rate limiting
6. Use persistent volumes for logs

## ✅ Success Criteria

- [ ] API responds to health checks
- [ ] Valid secrets are accepted (200)
- [ ] Invalid secrets are rejected (401)
- [ ] Client IPs are logged
- [ ] Runs in Docker container
- [ ] Deployed to Kubernetes
- [ ] Accessible externally
- [ ] All tests pass

## 💡 Tips

- Use `kubectl describe pod` for troubleshooting
- Logs are in `/app/logs/access.log` inside pods
- For persistent logs, add a PersistentVolumeClaim
- Scale with: `kubectl scale deployment secret-validator-api --replicas=N`
- Update secret: `kubectl rollout restart deployment secret-validator-api`

Good luck with your homework! 🎉
