import requests
import os

# Get the secret from environment or use default
SECRET_VALUE = os.environ.get('SECRET_VALUE', 'maorsecretpassword123')

# Test health endpoint
response = requests.get('http://localhost:5000/IsAlive')
print("Health check:", response.json())

# Test validate endpoint with correct secret
response = requests.post(
    'http://localhost:5000/validate',
    json={"secret": SECRET_VALUE}  
)
print("Valid secret:", response.json())

# Test validate endpoint with wrong secret
response = requests.post(
    'http://localhost:5000/validate',
    json={"secret": "wrongpasswordtest"}
)
print("Wrong secret:", response.json())