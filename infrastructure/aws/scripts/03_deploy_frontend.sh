#!/bin/bash
# =============================================================================
# FedGuard AWS Deployment — Step 3: S3 + CloudFront for Frontend
# Usage: bash infrastructure/aws/scripts/03_deploy_frontend.sh [bucket-name]
# Requires: AWS CLI configured with --profile fedguard
# =============================================================================
set -e

PROFILE="fedguard"
REGION="us-east-1"
BUCKET_NAME="${1:-fedguard-frontend-demo}"

echo "============================================="
echo "  FedGuard — Frontend S3 + CloudFront Deploy"
echo "============================================="

# ---- Step 3a: Create S3 Bucket ----
echo ""
echo "[1/5] Creating S3 bucket: $BUCKET_NAME ..."

python -m awscli s3api create-bucket \
  --profile $PROFILE \
  --region $REGION \
  --bucket "$BUCKET_NAME" 2>/dev/null || echo "  Bucket may already exist, continuing..."

# Block all public access
python -m awscli s3api put-public-access-block \
  --profile $PROFILE \
  --region $REGION \
  --bucket "$BUCKET_NAME" \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "  ✓ Bucket created with public access blocked"

# Tag the bucket
python -m awscli s3api put-bucket-tagging \
  --profile $PROFILE \
  --region $REGION \
  --bucket "$BUCKET_NAME" \
  --tagging 'TagSet=[{Key=Project,Value=FedGuard},{Key=Environment,Value=Demo},{Key=Owner,Value=Vishnu}]'

echo "  ✓ Bucket tagged"

# ---- Step 3b: Create CloudFront OAC ----
echo ""
echo "[2/5] Creating CloudFront Origin Access Control..."

OAC_ID=$(python -m awscli cloudfront create-origin-access-control \
  --profile $PROFILE \
  --origin-access-control-config '{
    "Name": "FedGuard-Frontend-OAC",
    "Description": "OAC for FedGuard S3 frontend bucket",
    "SigningProtocol": "sigv4",
    "SigningBehavior": "always",
    "OriginAccessControlOriginType": "s3"
  }' \
  --query 'OriginAccessControl.Id' \
  --output text 2>/dev/null) || OAC_ID="EXISTING"

echo "  ✓ OAC ID: $OAC_ID"

# ---- Step 3c: Create CloudFront Distribution ----
echo ""
echo "[3/5] Creating CloudFront distribution..."

DIST_CONFIG=$(cat <<EOF
{
  "CallerReference": "fedguard-frontend-$(date +%s)",
  "Comment": "FedGuard Frontend Distribution",
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-$BUCKET_NAME",
        "DomainName": "$BUCKET_NAME.s3.$REGION.amazonaws.com",
        "OriginAccessControlId": "$OAC_ID",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-$BUCKET_NAME",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "Compress": true
  },
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 403,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 10
      }
    ]
  },
  "PriceClass": "PriceClass_100",
  "Tags": {
    "Items": [
      {"Key": "Project", "Value": "FedGuard"},
      {"Key": "Environment", "Value": "Demo"},
      {"Key": "Owner", "Value": "Vishnu"}
    ]
  }
}
EOF
)

DIST_RESULT=$(python -m awscli cloudfront create-distribution-with-tags \
  --profile $PROFILE \
  --distribution-config-with-tags "$DIST_CONFIG" \
  --query '{Id: Distribution.Id, DomainName: Distribution.DomainName}' \
  --output json)

DIST_ID=$(echo "$DIST_RESULT" | python -c "import sys,json; print(json.load(sys.stdin)['Id'])")
DIST_DOMAIN=$(echo "$DIST_RESULT" | python -c "import sys,json; print(json.load(sys.stdin)['DomainName'])")

echo "  ✓ Distribution ID: $DIST_ID"
echo "  ✓ Domain Name: $DIST_DOMAIN"

# ---- Step 3d: Update S3 Bucket Policy for CloudFront ----
echo ""
echo "[4/5] Updating S3 bucket policy for CloudFront access..."

ACCOUNT_ID=$(python -m awscli sts get-caller-identity --profile $PROFILE --query Account --output text)

BUCKET_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::$ACCOUNT_ID:distribution/$DIST_ID"
        }
      }
    }
  ]
}
EOF
)

python -m awscli s3api put-bucket-policy \
  --profile $PROFILE \
  --region $REGION \
  --bucket "$BUCKET_NAME" \
  --policy "$BUCKET_POLICY"

echo "  ✓ Bucket policy updated"

# ---- Step 3e: Build and Upload Frontend ----
echo ""
echo "[5/5] Building and uploading frontend..."

cd "$(dirname "$0")/../../../frontend"
npm run build

python -m awscli s3 sync dist/ "s3://$BUCKET_NAME" \
  --profile $PROFILE \
  --region $REGION \
  --delete

echo "  ✓ Frontend uploaded to S3"

# Invalidate cache
python -m awscli cloudfront create-invalidation \
  --profile $PROFILE \
  --distribution-id "$DIST_ID" \
  --paths "/*" > /dev/null

echo "  ✓ CloudFront cache invalidated"

echo ""
echo "============================================="
echo "  Frontend Deployment Complete!"
echo "============================================="
echo ""
echo "  CloudFront Domain: https://$DIST_DOMAIN"
echo "  Distribution ID:   $DIST_ID"
echo "  S3 Bucket:         $BUCKET_NAME"
echo ""
echo "  NOTE: It may take 5-15 minutes for the CloudFront"
echo "  distribution to fully deploy."
echo ""
echo "  Save these values — you will need DIST_ID for future"
echo "  deployments and DIST_DOMAIN for backend CORS config."
