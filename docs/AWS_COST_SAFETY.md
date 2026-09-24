# AWS Cost Safety & Billing Checklist

**⚠️ CRITICAL WARNING:** Do not leave EC2, CloudWatch logs, NAT Gateway, ECR images, or storage resources running without checking billing.

This phase sets up cloud architecture. Because AWS is not free, FedGuard uses a cost-safe deployment topology. 

## Student-Safe Deployment Checklist
- [ ] **AWS Budgets:** Ensure you have created a zero-spend or $5/month budget in the AWS Billing Dashboard.
- [ ] **Billing Alerts:** Set up CloudWatch billing alarms to send an email if projected costs exceed your limit.
- [ ] **No NAT Gateways:** NAT Gateways cost ~$32/mo minimum. Do not deploy them.
- [ ] **No RDS Defaults:** RDS databases charge hourly. We stick to our free Neon PostgreSQL tier for this deployment unless explicitly requested.
- [ ] **EC2:** Use a `t3.micro` or `t3.small`. Shut it down when not actively demoing.

## Services Used (Low Cost)
- **Amazon S3:** Frontend hosting and artifact storage (pennies per month).
- **Amazon CloudFront:** Free tier covers 1TB of data out.
- **Amazon EC2 (t3.micro/small):** Runs the Docker Compose backend (under $15/mo if left on, but turn it off).
- **AWS Systems Manager (Parameter Store):** Standard parameters are free.
- **Amazon Bedrock:** Pay-per-token. Very cheap for demo usage, but limit RAG document sizes.

## Services Intentionally Avoided (High Cost)
- Elastic Kubernetes Service (EKS) - $70/mo control plane fee.
- ECS Fargate - Expensive for constant running compared to a single EC2.
- NAT Gateway - $32/mo baseline.
- Amazon RDS - Expensive baseline compared to Neon serverless.
- SageMaker Training Jobs - High hourly GPU costs.

## Cleanup Commands
To destroy resources and stop billing, run these commands when you are done:

```bash
# Stop EC2 instance
aws ec2 stop-instances --instance-ids i-0abcd1234efgh5678

# Empty S3 bucket (if you don't need artifacts anymore)
aws s3 rm s3://your-artifact-bucket --recursive

# Delete CloudWatch Logs
aws logs delete-log-group --log-group-name /fedguard/backend
```
