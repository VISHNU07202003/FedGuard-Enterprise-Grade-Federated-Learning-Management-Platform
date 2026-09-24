# FedGuard AWS Infrastructure

All scripts use `--profile fedguard`. Configure your profile first:

```bash
aws configure --profile fedguard
# or on Windows:
python -m awscli configure --profile fedguard
```

## Deployment Scripts (run in order)

| Script | Purpose |
|--------|---------|
| `01_setup_budget.sh` | Creates a $5/month AWS Budget with email alerts |
| `02_setup_secrets.sh` | Stores secrets in Parameter Store (interactive prompts) |
| `03_deploy_frontend.sh` | Creates S3 bucket, CloudFront OAC distribution, builds and uploads frontend |
| `04_launch_backend_ec2.sh` | Creates security group, IAM role, and launches EC2 instance with Docker bootstrap |
| `05_verify_deployment.sh` | Verifies `/health`, `/ready`, `/metrics`, and CloudFront reachability |

## Utility Scripts

| Script | Purpose |
|--------|---------|
| `redeploy_frontend.ps1` | PowerShell script for quick frontend re-deploys from Windows |
| `ec2_bootstrap.sh` | Manual EC2 bootstrap (Docker + Docker Compose install) |

## Cleanup

| Script | Purpose |
|--------|---------|
| `99_cleanup.sh` | **Destroys all FedGuard AWS resources** (EC2, S3, CloudFront, IAM, SSM, CloudWatch) |

> **⚠️ WARNING:** Always run `99_cleanup.sh` when you are done demoing to avoid surprise charges.

## Resource Tags

All resources are tagged with:
- `Project=FedGuard`
- `Environment=Demo`
- `Owner=Vishnu`

## IAM Policy

The `iam-policy.json` file contains the least-privilege policy for the `FedGuardRuntimeRole`. It grants only:
- SSM Parameter Store read for `/fedguard/dev/*`
- S3 read/write for the artifact bucket
- Bedrock InvokeModel
- CloudWatch Logs write

See also:
- [AWS Deployment Guide](../../docs/AWS_DEPLOYMENT.md)
- [Cost Safety Checklist](../../docs/AWS_COST_SAFETY.md)
- [Security Checklist](../../docs/DEPLOYMENT_SECURITY_CHECKLIST.md)
