#!/bin/bash

set -e

echo "=========================================="
echo "Secret Validator API Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Step 1: Build Docker image
echo -e "\n${GREEN}Step 1: Building Docker image...${NC}"
docker build -t secret-validator-api:latest .

echo -e "${GREEN}✓ Docker image built successfully${NC}"

# Step 2: Test Docker image locally (optional)
echo -e "\n${YELLOW}Do you want to test the Docker container locally? (y/n)${NC}"
read -r test_local

if [ "$test_local" = "y" ]; then
    echo -e "${GREEN}Starting container on port 5000...${NC}"
    docker run -d --name secret-validator-test -p 5000:5000 \
        -e SECRET_VALUE="mysecretpassword123" \
        secret-validator-api:latest
    
    echo -e "${GREEN}Container started. Testing...${NC}"
    sleep 3
    
    # Test health endpoint
    echo -e "\nTesting health endpoint:"
    curl http://localhost:5000/health
    
    echo -e "\n\nTesting validation endpoint with correct secret:"
    curl -X POST http://localhost:5000/validate \
        -H "Content-Type: application/json" \
        -d '{"secret":"mysecretpassword123"}'
    
    echo -e "\n\nTesting validation endpoint with incorrect secret:"
    curl -X POST http://localhost:5000/validate \
        -H "Content-Type: application/json" \
        -d '{"secret":"wrongsecret"}'
    
    echo -e "\n\n${YELLOW}Check logs in container:${NC}"
    docker exec secret-validator-test cat /app/logs/access.log
    
    echo -e "\n${YELLOW}Stopping and removing test container...${NC}"
    docker stop secret-validator-test
    docker rm secret-validator-test
fi

# Step 3: Check for Kubernetes
echo -e "\n${GREEN}Step 3: Checking Kubernetes setup...${NC}"

if command -v kubectl &> /dev/null; then
    echo -e "${GREEN}✓ kubectl is installed${NC}"
else
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if using minikube
if command -v minikube &> /dev/null; then
    echo -e "${YELLOW}Minikube detected. Do you want to use minikube? (y/n)${NC}"
    read -r use_minikube
    
    if [ "$use_minikube" = "y" ]; then
        # Check if minikube is running
        if ! minikube status &> /dev/null; then
            echo -e "${YELLOW}Starting minikube...${NC}"
            minikube start
        fi
        
        # Load image into minikube
        echo -e "${GREEN}Loading Docker image into minikube...${NC}"
        minikube image load secret-validator-api:latest
        
        # Set kubectl context to minikube
        kubectl config use-context minikube
    fi
fi

# Step 4: Deploy to Kubernetes
echo -e "\n${GREEN}Step 4: Deploying to Kubernetes...${NC}"

# Apply Kubernetes manifests
echo "Creating secret..."
kubectl apply -f k8s/secret.yaml

echo "Creating deployment..."
kubectl apply -f k8s/deployment.yaml

echo "Creating service..."
kubectl apply -f k8s/service.yaml

echo -e "${GREEN}✓ Deployment complete!${NC}"

# Wait for deployment to be ready
echo -e "\n${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=secret-validator --timeout=120s

# Show deployment status
echo -e "\n${GREEN}Deployment Status:${NC}"
kubectl get deployments -l app=secret-validator
kubectl get pods -l app=secret-validator
kubectl get services secret-validator-service

# Get service URL
echo -e "\n${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}"

if command -v minikube &> /dev/null && [ "$use_minikube" = "y" ]; then
    SERVICE_URL=$(minikube service secret-validator-service --url)
    echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
    echo -e "\nTest with:"
    echo -e "curl ${SERVICE_URL}/health"
    echo -e "curl -X POST ${SERVICE_URL}/validate -H 'Content-Type: application/json' -d '{\"secret\":\"mysecretpassword123\"}'"
else
    echo -e "${YELLOW}For cloud providers, get the external IP with:${NC}"
    echo "kubectl get service secret-validator-service"
    echo -e "\n${YELLOW}It may take a few minutes for the LoadBalancer to assign an external IP${NC}"
fi

echo -e "\n${YELLOW}To deploy the Ingress (Step 4 bonus):${NC}"
echo "kubectl apply -f k8s/ingress.yaml"

echo -e "\n${YELLOW}To view logs from a pod:${NC}"
echo "kubectl logs -l app=secret-validator"

echo -e "\n${YELLOW}To delete the deployment:${NC}"
echo "./cleanup.sh"
