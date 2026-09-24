# =============================================================================
# FedGuard AWS Deployment — Quick Frontend Re-deploy (PowerShell)
# Usage: .\infrastructure\aws\scripts\redeploy_frontend.ps1 -BucketName <name> -DistributionId <id>
# Requires: AWS CLI configured with: aws configure --profile fedguard
# =============================================================================
param(
    [Parameter(Mandatory=$true)]
    [string]$BucketName,

    [Parameter(Mandatory=$true)]
    [string]$DistributionId,

    [string]$Profile = "fedguard",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  FedGuard — Frontend Re-deploy" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Build frontend
Write-Host "`n[1/3] Building frontend..." -ForegroundColor Yellow
Push-Location "$PSScriptRoot\..\..\..\frontend"
npm run build
Pop-Location

# Sync to S3
Write-Host "`n[2/3] Syncing to S3..." -ForegroundColor Yellow
python -m awscli s3 sync "$PSScriptRoot\..\..\..\frontend\dist" "s3://$BucketName" `
    --profile $Profile `
    --region $Region `
    --delete

# Invalidate CloudFront
Write-Host "`n[3/3] Invalidating CloudFront cache..." -ForegroundColor Yellow
python -m awscli cloudfront create-invalidation `
    --profile $Profile `
    --distribution-id $DistributionId `
    --paths "/*"

Write-Host "`n=============================================" -ForegroundColor Green
Write-Host "  Frontend re-deployed successfully!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
