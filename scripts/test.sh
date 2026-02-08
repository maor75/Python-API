#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo "Usage: ./test.sh <service-url>"
    echo "Example: ./test.sh http://localhost:5000"
    echo "Example: ./test.sh \$(minikube service secret-validator-service --url)"
    exit 1
fi

SERVICE_URL=$1

echo "Testing Secret Validator API at: $SERVICE_URL"
echo "============================================"

# Test 1: Health Check
echo -e "\n${YELLOW}Test 1: Health Check${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" $SERVICE_URL/health)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "Response: $BODY"
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Health check passed (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Health check failed (HTTP $HTTP_CODE)${NC}"
fi

# Test 2: Valid Secret
echo -e "\n${YELLOW}Test 2: Valid Secret${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST $SERVICE_URL/validate \
    -H "Content-Type: application/json" \
    -d '{"secret":"mysecretpassword123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "Response: $BODY"
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Valid secret accepted (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Valid secret rejected (HTTP $HTTP_CODE)${NC}"
fi

# Test 3: Invalid Secret
echo -e "\n${YELLOW}Test 3: Invalid Secret${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST $SERVICE_URL/validate \
    -H "Content-Type: application/json" \
    -d '{"secret":"wrongsecret"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "Response: $BODY"
if [ "$HTTP_CODE" -eq 401 ]; then
    echo -e "${GREEN}✓ Invalid secret rejected correctly (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Invalid secret handling failed (HTTP $HTTP_CODE)${NC}"
fi

# Test 4: Missing Secret Field
echo -e "\n${YELLOW}Test 4: Missing Secret Field${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST $SERVICE_URL/validate \
    -H "Content-Type: application/json" \
    -d '{}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "Response: $BODY"
if [ "$HTTP_CODE" -eq 400 ]; then
    echo -e "${GREEN}✓ Missing field handled correctly (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}✗ Missing field handling failed (HTTP $HTTP_CODE)${NC}"
fi

echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}Testing complete!${NC}"
