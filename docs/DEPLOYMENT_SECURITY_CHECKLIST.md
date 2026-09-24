# Deployment Security Checklist

Before pushing FedGuard to a live AWS environment, review this checklist.

## 1. Secrets Management
- [ ] No AWS Access Keys or Secret Keys in the Git repository.
- [ ] `.env` file is excluded via `.gitignore` and never committed.
- [ ] No database URLs (e.g., Neon connection strings) are exposed in the React frontend code.
- [ ] `JWT_SECRET` is never exposed to the frontend or checked into the codebase.
- [ ] Production backend reads secrets from AWS Systems Manager Parameter Store or a securely injected `.env`.

## 2. Infrastructure Configuration
- [ ] No raw datasets are uploaded to the S3 artifact bucket.
- [ ] The S3 artifact bucket is **NOT** public. It is accessed only via backend IAM roles.
- [ ] No default admin passwords in the production database.
- [ ] Bedrock API calls happen strictly server-side.

## 3. Web & API Security
- [ ] Backend CORS (`BACKEND_CORS_ORIGINS`) is locked strictly to the CloudFront domain. No wildcards (`*`) in production.
- [ ] `/mutation` routes and training dispatch routes are protected by RBAC and valid JWTs.
- [ ] `/metrics` access is documented. If exposed on a public EC2 IP, use network firewalls or basic auth to restrict Prometheus scraping endpoints.
- [ ] No raw user prompts or PII are logged in Prometheus metrics.

## 4. IAM Roles
- [ ] EC2 instances run with an IAM Instance Profile containing least-privilege permissions.
- [ ] Deployment user has minimal policies (no `AdministratorAccess`).
