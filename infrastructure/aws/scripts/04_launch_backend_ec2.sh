#!/bin/bash
# =============================================================================
# FedGuard AWS Deployment — Step 4: EC2 Backend Instance
# Usage: bash infrastructure/aws/scripts/04_launch_backend_ec2.sh
# Requires: AWS CLI configured with --profile fedguard
#
# This script:
#   1. Creates a security group
#   2. Creates an IAM instance profile
#   3. Launches a t3.small EC2 instance with user-data bootstrap
#   4. Outputs the public DNS for verification
# =============================================================================
set -e

PROFILE="fedguard"
REGION="us-east-1"
INSTANCE_TYPE="${1:-t3.small}"
KEY_NAME="${2:?Usage: $0 <instance-type> <key-pair-name>}"

echo "============================================="
echo "  FedGuard — EC2 Backend Launch"
echo "============================================="

# ---- Get default VPC ----
VPC_ID=$(python -m awscli ec2 describe-vpcs \
  --profile $PROFILE \
  --region $REGION \
  --filters "Name=is-default,Values=true" \
  --query 'Vpcs[0].VpcId' \
  --output text)
echo "Default VPC: $VPC_ID"

# ---- Create Security Group ----
echo ""
echo "[1/4] Creating security group..."

SG_ID=$(python -m awscli ec2 create-security-group \
  --profile $PROFILE \
  --region $REGION \
  --group-name "FedGuard-Backend-SG" \
  --description "FedGuard backend security group" \
  --vpc-id "$VPC_ID" \
  --query 'GroupId' \
  --output text 2>/dev/null) || \
SG_ID=$(python -m awscli ec2 describe-security-groups \
  --profile $PROFILE \
  --region $REGION \
  --filters "Name=group-name,Values=FedGuard-Backend-SG" \
  --query 'SecurityGroups[0].GroupId' \
  --output text)

echo "  Security Group: $SG_ID"

# Get caller's public IP for SSH restriction
MY_IP=$(curl -s https://checkip.amazonaws.com)/32
echo "  Your IP: $MY_IP"

# Add ingress rules (ignore errors if rules already exist)
for rule in \
  "tcp 22 22 $MY_IP SSH" \
  "tcp 8000 8000 0.0.0.0/0 FastAPI" \
  "tcp 9090 9090 $MY_IP Prometheus" \
  "tcp 3000 3000 $MY_IP Grafana"; do
  
  proto=$(echo $rule | awk '{print $1}')
  from=$(echo $rule | awk '{print $2}')
  to=$(echo $rule | awk '{print $3}')
  cidr=$(echo $rule | awk '{print $4}')
  desc=$(echo $rule | awk '{print $5}')
  
  python -m awscli ec2 authorize-security-group-ingress \
    --profile $PROFILE \
    --region $REGION \
    --group-id "$SG_ID" \
    --protocol "$proto" \
    --port "$from-$to" \
    --cidr "$cidr" 2>/dev/null || true
  echo "  ✓ Rule: $desc ($cidr -> $from)"
done

# Tag the security group
python -m awscli ec2 create-tags \
  --profile $PROFILE \
  --region $REGION \
  --resources "$SG_ID" \
  --tags Key=Project,Value=FedGuard Key=Environment,Value=Demo Key=Owner,Value=Vishnu

# ---- Create IAM Role & Instance Profile ----
echo ""
echo "[2/4] Creating IAM role and instance profile..."

TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ec2.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}'

python -m awscli iam create-role \
  --profile $PROFILE \
  --role-name FedGuardRuntimeRole \
  --assume-role-policy-document "$TRUST_POLICY" \
  --tags Key=Project,Value=FedGuard Key=Environment,Value=Demo 2>/dev/null || echo "  Role may already exist"

python -m awscli iam put-role-policy \
  --profile $PROFILE \
  --role-name FedGuardRuntimeRole \
  --policy-name FedGuardRuntimePolicy \
  --policy-document file://infrastructure/aws/iam-policy.json

python -m awscli iam create-instance-profile \
  --profile $PROFILE \
  --instance-profile-name FedGuardRuntimeProfile 2>/dev/null || echo "  Profile may already exist"

python -m awscli iam add-role-to-instance-profile \
  --profile $PROFILE \
  --instance-profile-name FedGuardRuntimeProfile \
  --role-name FedGuardRuntimeRole 2>/dev/null || echo "  Role already attached"

echo "  ✓ IAM role and instance profile ready"

# Wait for instance profile propagation
echo "  Waiting 10s for IAM propagation..."
sleep 10

# ---- Find latest Amazon Linux 2023 AMI ----
echo ""
echo "[3/4] Finding latest Amazon Linux 2023 AMI..."

AMI_ID=$(python -m awscli ec2 describe-images \
  --profile $PROFILE \
  --region $REGION \
  --owners amazon \
  --filters \
    "Name=name,Values=al2023-ami-2023*-x86_64" \
    "Name=state,Values=available" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

echo "  AMI: $AMI_ID"

# ---- Launch EC2 Instance ----
echo ""
echo "[4/4] Launching EC2 instance ($INSTANCE_TYPE)..."

USER_DATA=$(cat <<'USERDATA'
#!/bin/bash
yum update -y
yum install -y docker git
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Install Docker Compose
DOCKER_CONFIG=/usr/local/lib/docker/cli-plugins
mkdir -p $DOCKER_CONFIG
curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/docker-compose
chmod +x $DOCKER_CONFIG/docker-compose

echo "Bootstrap complete" > /tmp/bootstrap_done
USERDATA
)

USER_DATA_B64=$(echo "$USER_DATA" | base64 -w 0)

INSTANCE_ID=$(python -m awscli ec2 run-instances \
  --profile $PROFILE \
  --region $REGION \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --security-group-ids "$SG_ID" \
  --iam-instance-profile Name=FedGuardRuntimeProfile \
  --user-data "$USER_DATA_B64" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=FedGuard-Backend},{Key=Project,Value=FedGuard},{Key=Environment,Value=Demo},{Key=Owner,Value=Vishnu}]" \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "  Instance ID: $INSTANCE_ID"
echo "  Waiting for instance to be running..."

python -m awscli ec2 wait instance-running \
  --profile $PROFILE \
  --region $REGION \
  --instance-ids "$INSTANCE_ID"

PUBLIC_DNS=$(python -m awscli ec2 describe-instances \
  --profile $PROFILE \
  --region $REGION \
  --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].PublicDnsName' \
  --output text)

PUBLIC_IP=$(python -m awscli ec2 describe-instances \
  --profile $PROFILE \
  --region $REGION \
  --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo ""
echo "============================================="
echo "  EC2 Backend Launch Complete!"
echo "============================================="
echo ""
echo "  Instance ID:  $INSTANCE_ID"
echo "  Public DNS:   $PUBLIC_DNS"
echo "  Public IP:    $PUBLIC_IP"
echo ""
echo "  Next steps:"
echo "    1. SSH in:  ssh -i <your-key>.pem ec2-user@$PUBLIC_DNS"
echo "    2. Wait for bootstrap: cat /tmp/bootstrap_done"
echo "    3. Clone and deploy:"
echo "       git clone <your-repo-url>"
echo "       cd FedGuard"
echo "       docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
echo "    4. Verify: curl http://$PUBLIC_DNS:8000/health"
