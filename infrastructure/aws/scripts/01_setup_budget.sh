#!/bin/bash
# =============================================================================
# FedGuard AWS Deployment — Step 1: Cost Safety & Budget
# Usage: bash infrastructure/aws/scripts/01_setup_budget.sh
# Requires: AWS CLI configured with --profile fedguard
# =============================================================================
set -e

PROFILE="fedguard"
REGION="us-east-1"
ACCOUNT_EMAIL="${1:?Usage: $0 <your-email-for-alerts>}"

echo "============================================="
echo "  FedGuard — AWS Budget Setup"
echo "============================================="

# Get account ID
ACCOUNT_ID=$(python -m awscli sts get-caller-identity --profile $PROFILE --query Account --output text)
echo "Account ID: $ACCOUNT_ID"

echo ""
echo "Creating zero-spend budget with email alert..."

python -m awscli budgets create-budget \
  --profile $PROFILE \
  --region $REGION \
  --account-id "$ACCOUNT_ID" \
  --budget '{
    "BudgetName": "FedGuard-Demo-Budget",
    "BudgetLimit": {
      "Amount": "5.0",
      "Unit": "USD"
    },
    "BudgetType": "COST",
    "TimeUnit": "MONTHLY"
  }' \
  --notifications-with-subscribers "[
    {
      \"Notification\": {
        \"NotificationType\": \"ACTUAL\",
        \"ComparisonOperator\": \"GREATER_THAN\",
        \"Threshold\": 1.0,
        \"ThresholdType\": \"ABSOLUTE_VALUE\"
      },
      \"Subscribers\": [
        {
          \"SubscriptionType\": \"EMAIL\",
          \"Address\": \"$ACCOUNT_EMAIL\"
        }
      ]
    },
    {
      \"Notification\": {
        \"NotificationType\": \"ACTUAL\",
        \"ComparisonOperator\": \"GREATER_THAN\",
        \"Threshold\": 80.0,
        \"ThresholdType\": \"PERCENTAGE\"
      },
      \"Subscribers\": [
        {
          \"SubscriptionType\": \"EMAIL\",
          \"Address\": \"$ACCOUNT_EMAIL\"
        }
      ]
    }
  ]"

echo ""
echo "Budget 'FedGuard-Demo-Budget' created with \$5/month limit."
echo "Alerts will be sent to: $ACCOUNT_EMAIL"
echo "  - When actual spend exceeds \$1.00"
echo "  - When actual spend exceeds 80% of budget"
echo ""
echo "Step 1 complete."
