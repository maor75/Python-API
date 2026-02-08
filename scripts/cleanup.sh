#!/bin/bash

echo "Cleaning up Kubernetes resources..."

kubectl delete -f k8s/ingress.yaml --ignore-not-found=true
kubectl delete -f k8s/service.yaml --ignore-not-found=true
kubectl delete -f k8s/deployment.yaml --ignore-not-found=true
kubectl delete -f k8s/secret.yaml --ignore-not-found=true

echo "Cleanup complete!"
