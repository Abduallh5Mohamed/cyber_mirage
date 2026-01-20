# 🔒 AWS Security Group Configuration Helper
# استخدم هذا السكريبت لو عندك AWS CLI مثبت

param(
    [Parameter(Mandatory=$true)]
    [string]$SecurityGroupId,
    
    [Parameter(Mandatory=$true)]
    [string]$Region = "eu-north-1"
)

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔒 Configuring Security Group: $SecurityGroupId" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Get your current IP
Write-Host "🌐 Getting your current IP..." -ForegroundColor Green
$MyIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
Write-Host "   Your IP: $MyIP" -ForegroundColor White
Write-Host ""

# Define all required rules
$rules = @(
    @{Port=22; Protocol="tcp"; Source="$MyIP/32"; Description="SSH Management"},
    @{Port=80; Protocol="tcp"; Source="0.0.0.0/0"; Description="HTTP"},
    @{Port=443; Protocol="tcp"; Source="0.0.0.0/0"; Description="HTTPS"},
    @{Port=8501; Protocol="tcp"; Source="0.0.0.0/0"; Description="Streamlit Dashboard"},
    @{Port=3000; Protocol="tcp"; Source="0.0.0.0/0"; Description="Grafana Dashboard"},
    @{Port=445; Protocol="tcp"; Source="0.0.0.0/0"; Description="SMB Honeypot"},
    @{Port=502; Protocol="tcp"; Source="0.0.0.0/0"; Description="Modbus Honeypot"},
    @{Port=1025; Protocol="tcp"; Source="0.0.0.0/0"; Description="Custom Honeypot"},
    @{Port=2121; Protocol="tcp"; Source="0.0.0.0/0"; Description="FTP Honeypot"},
    @{Port=2222; Protocol="tcp"; Source="0.0.0.0/0"; Description="SSH Honeypot"},
    @{Port=3307; Protocol="tcp"; Source="0.0.0.0/0"; Description="MySQL Honeypot"},
    @{Port=5434; Protocol="tcp"; Source="0.0.0.0/0"; Description="PostgreSQL Honeypot"},
    @{Port=8080; Protocol="tcp"; Source="0.0.0.0/0"; Description="HTTP Honeypot"},
    @{Port=8443; Protocol="tcp"; Source="0.0.0.0/0"; Description="HTTPS Honeypot"},
    @{Port=9090; Protocol="tcp"; Source="$MyIP/32"; Description="Prometheus Monitoring"}
)

Write-Host "📝 Adding Security Group Rules..." -ForegroundColor Green
Write-Host ""

foreach ($rule in $rules) {
    $port = $rule.Port
    $protocol = $rule.Protocol
    $source = $rule.Source
    $desc = $rule.Description
    
    Write-Host "   ➜ Adding: Port $port ($desc)" -ForegroundColor Cyan
    
    try {
        aws ec2 authorize-security-group-ingress `
            --group-id $SecurityGroupId `
            --ip-permissions IpProtocol=$protocol,FromPort=$port,ToPort=$port,IpRanges="[{CidrIp=$source,Description='$desc'}]" `
            --region $Region 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "      ✅ Added successfully" -ForegroundColor Green
        } else {
            Write-Host "      ⚠️  Rule might already exist or error occurred" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "      ❌ Error: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Security Group Configuration Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Verify rules with:" -ForegroundColor Yellow
Write-Host "   aws ec2 describe-security-groups --group-ids $SecurityGroupId --region $Region" -ForegroundColor White
Write-Host ""

<#
.SYNOPSIS
    Configures AWS Security Group for Cyber Mirage production deployment

.DESCRIPTION
    This script adds all required inbound rules for Cyber Mirage honeypot system.
    Automatically detects your public IP and secures SSH/Prometheus access.

.PARAMETER SecurityGroupId
    The Security Group ID (e.g., sg-0123456789abcdef0)

.PARAMETER Region
    AWS Region (default: eu-north-1)

.EXAMPLE
    .\fix_security_group_aws.ps1 -SecurityGroupId "sg-0123456789abcdef0"
    
.EXAMPLE
    .\fix_security_group_aws.ps1 -SecurityGroupId "sg-0123456789abcdef0" -Region "us-east-1"

.NOTES
    Requires AWS CLI installed and configured
    Run: aws configure (to set up credentials)
#>
