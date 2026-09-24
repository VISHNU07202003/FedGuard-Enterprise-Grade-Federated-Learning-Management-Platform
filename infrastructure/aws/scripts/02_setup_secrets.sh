#!/bin/bash
# =============================================================================
# FedGuard AWS Deployment — Step 2: Parameter Store Secrets
# Usage: bash infrastructure/aws/scripts/02_setup_secrets.sh
# Requires: AWS CLI configured with --profile fedguard
#
# IMPORTANT: This script prompts for secret values interactively.
#            It does NOT store secrets in files, shell history, or logs.
# =============================================================================
set -e

PROFILE="fedguard"
REGION="us-east-1"
PREFIX="/fedguard/demo"

echo "============================================="
echo "  FedGuard — Parameter Store Setup"
echo "============================================="
echo ""
echo "This will create SecureString parameters under: $PREFIX"
echo "You will be prompted for each secret value."
echo ""

# DATABASE_URL
echo -n "Enter DATABASE_URL (Neon PostgreSQL connection string): "
read -s DB_URL
echo ""
python -m awscli ssm put-parameter \
  --profile $PROFILE \
  --region $REGION \
  --name "$PREFIX/DATABASE_URL" \
  --value "$DB_URL" \
  --type SecureString \
  --overwrite \
  --tags "Key=Project,Value=FedGuard" "Key=Environment,Value=Demo"
echo "  ✓ $PREFIX/DATABASE_URL stored"

# JWT_SECRET
echo -n "Enter JWT_SECRET (strong random string): "
read -s JWT_SEC
echo ""
python -m awscli ssm put-parameter \
  --profile $PROFILE \
  --region $REGION \
  --name "$PREFIX/JWT_SECRET" \
  --value "$JWT_SEC" \
  --type SecureString \
  --overwrite \
  --tags "Key=Project,Value=FedGuard" "Key=Environment,Value=Demo"
echo "  ✓ $PREFIX/JWT_SECRET stored"

# AWS_BEDROCK_MODEL_ID (optional)
echo -n "Enter AWS_BEDROCK_MODEL_ID (or press Enter to skip): "
read BEDROCK_MODEL
if [ -n "$BEDROCK_MODEL" ]; then
  python -m awscli ssm put-parameter \
    --profile $PROFILE \
    --region $REGION \
    --name "$PREFIX/AWS_BEDROCK_MODEL_ID" \
    --value "$BEDROCK_MODEL" \
    --type String \
    --overwrite \
    --tags "Key=Project,Value=FedGuard" "Key=Environment,Value=Demo"
  echo "  ✓ $PREFIX/AWS_BEDROCK_MODEL_ID stored"
else
  echo "  ⊘ Skipped AWS_BEDROCK_MODEL_ID"
fi

echo ""
echo "Parameter Store setup complete."
echo "Verify with: python -m awscli ssm get-parameters-by-path --profile $PROFILE --region $REGION --path $PREFIX --with-decryption"
