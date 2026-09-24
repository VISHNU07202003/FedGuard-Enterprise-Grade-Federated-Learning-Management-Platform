#!/bin/bash
# =============================================================================
# FedGuard AWS Deployment — Step 5: Verify Live Deployment
# Usage: bash infrastructure/aws/scripts/05_verify_deployment.sh <ec2-dns> <cloudfront-domain>
# Requires: curl
# =============================================================================
set -e

EC2_DNS="${1:?Usage: $0 <ec2-public-dns> <cloudfront-domain>}"
CF_DOMAIN="${2:?Usage: $0 <ec2-public-dns> <cloudfront-domain>}"

echo "============================================="
echo "  FedGuard — Deployment Verification"
echo "============================================="

PASS=0
FAIL=0

check() {
  local label="$1"
  local url="$2"
  local expected="$3"
  
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
  
  if [ "$HTTP_CODE" = "$expected" ]; then
    echo "  ✓ $label — HTTP $HTTP_CODE"
    PASS=$((PASS + 1))
  else
    echo "  ✗ $label — HTTP $HTTP_CODE (expected $expected)"
    FAIL=$((FAIL + 1))
  fi
}

echo ""
echo "Backend checks (http://$EC2_DNS:8000):"
check "GET /health" "http://$EC2_DNS:8000/health" "200"
check "GET /ready" "http://$EC2_DNS:8000/ready" "200"
check "GET /metrics" "http://$EC2_DNS:8000/metrics" "200"
check "GET /api/v1/dashboard/ (expect 401 unauthenticated)" "http://$EC2_DNS:8000/api/v1/dashboard/" "401"

echo ""
echo "Frontend checks (https://$CF_DOMAIN):"
check "GET / (CloudFront)" "https://$CF_DOMAIN/" "200"

echo ""
echo "============================================="
echo "  Results: $PASS passed, $FAIL failed"
echo "============================================="

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "  Some checks failed. Common issues:"
  echo "    - EC2 security group not allowing port 8000"
  echo "    - Docker Compose not running on EC2"
  echo "    - CloudFront distribution still deploying (wait 5-15 min)"
  echo "    - S3 bucket policy not updated for CloudFront OAC"
  exit 1
fi
