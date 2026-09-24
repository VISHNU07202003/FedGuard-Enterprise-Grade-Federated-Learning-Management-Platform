#!/bin/bash
# =============================================================================
# FedGuard AWS Deployment — Cleanup: Destroy All AWS Resources
# Usage: bash infrastructure/aws/scripts/99_cleanup.sh
# Requires: AWS CLI configured with --profile fedguard
#
# WARNING: This will permanently delete FedGuard AWS resources.
#          Use this when you are done demoing to avoid charges.
# =============================================================================
set -e

PROFILE="fedguard"
REGION="us-east-1"
BUCKET_NAME="${1:-fedguard-frontend-demo}"

echo "============================================="
echo "  FedGuard — AWS Resource Cleanup"
echo "============================================="
echo ""
echo "  WARNING: This will delete all FedGuard resources."
echo "  Press Ctrl+C within 10 seconds to cancel."
echo ""
sleep 10

# ---- Terminate EC2 Instances ----
echo "[1/7] Terminating FedGuard EC2 instances..."
INSTANCE_IDS=$(python -m awscli ec2 describe-instances \
  --profile $PROFILE \
  --region $REGION \
  --filters "Name=tag:Project,Values=FedGuard" "Name=instance-state-name,Values=running,stopped" \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text)

if [ -n "$INSTANCE_IDS" ] && [ "$INSTANCE_IDS" != "None" ]; then
  python -m awscli ec2 terminate-instances \
    --profile $PROFILE \
    --region $REGION \
    --instance-ids $INSTANCE_IDS
  echo "  ✓ Terminated: $INSTANCE_IDS"
else
  echo "  ⊘ No running instances found"
fi

# ---- Delete CloudFront Distribution ----
echo ""
echo "[2/7] Disabling and deleting CloudFront distributions..."
DIST_IDS=$(python -m awscli cloudfront list-distributions \
  --profile $PROFILE \
  --query "DistributionList.Items[?Comment=='FedGuard Frontend Distribution'].Id" \
  --output text 2>/dev/null)

for DIST_ID in $DIST_IDS; do
  if [ -n "$DIST_ID" ] && [ "$DIST_ID" != "None" ]; then
    echo "  Disabling distribution $DIST_ID (this may take several minutes)..."
    ETAG=$(python -m awscli cloudfront get-distribution-config \
      --profile $PROFILE \
      --id "$DIST_ID" \
      --query 'ETag' --output text)
    
    # Get config, set Enabled=false
    python -m awscli cloudfront get-distribution-config \
      --profile $PROFILE \
      --id "$DIST_ID" \
      --query 'DistributionConfig' \
      --output json | python -c "
import sys, json
cfg = json.load(sys.stdin)
cfg['Enabled'] = False
print(json.dumps(cfg))
" > /tmp/cf_disable.json
    
    python -m awscli cloudfront update-distribution \
      --profile $PROFILE \
      --id "$DIST_ID" \
      --if-match "$ETAG" \
      --distribution-config file:///tmp/cf_disable.json > /dev/null
    
    echo "  ✓ Disabled $DIST_ID (delete manually after it finishes deploying)"
  fi
done

if [ -z "$DIST_IDS" ] || [ "$DIST_IDS" = "None" ]; then
  echo "  ⊘ No distributions found"
fi

# ---- Empty and Delete S3 Bucket ----
echo ""
echo "[3/7] Emptying and deleting S3 bucket: $BUCKET_NAME ..."
python -m awscli s3 rm "s3://$BUCKET_NAME" --profile $PROFILE --recursive 2>/dev/null || true
python -m awscli s3api delete-bucket --profile $PROFILE --region $REGION --bucket "$BUCKET_NAME" 2>/dev/null || true
echo "  ✓ Bucket deleted (or didn't exist)"

# ---- Delete Security Group ----
echo ""
echo "[4/7] Deleting security group..."
SG_ID=$(python -m awscli ec2 describe-security-groups \
  --profile $PROFILE \
  --region $REGION \
  --filters "Name=group-name,Values=FedGuard-Backend-SG" \
  --query 'SecurityGroups[0].GroupId' \
  --output text 2>/dev/null)

if [ -n "$SG_ID" ] && [ "$SG_ID" != "None" ]; then
  # Wait for instances to terminate
  echo "  Waiting for instances to fully terminate..."
  sleep 30
  python -m awscli ec2 delete-security-group \
    --profile $PROFILE \
    --region $REGION \
    --group-id "$SG_ID" 2>/dev/null || echo "  ⚠ Could not delete SG (instances may still be terminating)"
  echo "  ✓ Security group deleted"
else
  echo "  ⊘ No security group found"
fi

# ---- Delete IAM Resources ----
echo ""
echo "[5/7] Cleaning up IAM resources..."
python -m awscli iam remove-role-from-instance-profile \
  --profile $PROFILE \
  --instance-profile-name FedGuardRuntimeProfile \
  --role-name FedGuardRuntimeRole 2>/dev/null || true
python -m awscli iam delete-instance-profile \
  --profile $PROFILE \
  --instance-profile-name FedGuardRuntimeProfile 2>/dev/null || true
python -m awscli iam delete-role-policy \
  --profile $PROFILE \
  --role-name FedGuardRuntimeRole \
  --policy-name FedGuardRuntimePolicy 2>/dev/null || true
python -m awscli iam delete-role \
  --profile $PROFILE \
  --role-name FedGuardRuntimeRole 2>/dev/null || true
echo "  ✓ IAM role and instance profile deleted"

# ---- Delete Parameter Store Entries ----
echo ""
echo "[6/7] Deleting Parameter Store entries..."
for param in DATABASE_URL JWT_SECRET AWS_BEDROCK_MODEL_ID; do
  python -m awscli ssm delete-parameter \
    --profile $PROFILE \
    --region $REGION \
    --name "/fedguard/demo/$param" 2>/dev/null || true
done
echo "  ✓ Parameter Store entries deleted"

# ---- Delete CloudWatch Log Group ----
echo ""
echo "[7/7] Deleting CloudWatch log group..."
python -m awscli logs delete-log-group \
  --profile $PROFILE \
  --region $REGION \
  --log-group-name /fedguard/backend 2>/dev/null || true
echo "  ✓ CloudWatch log group deleted (or didn't exist)"

echo ""
echo "============================================="
echo "  Cleanup Complete!"
echo "============================================="
echo ""
echo "  NOTE: CloudFront distributions take up to 15 minutes"
echo "  to fully disable. You may need to delete them manually"
echo "  from the AWS Console after they finish deploying."
echo ""
echo "  Check your AWS Billing Dashboard to confirm zero usage."
