# 📋 AWS CLI Commands Generator
# Run this to get all AWS CLI commands to add Security Group rules

param(
    [Parameter(Mandatory=$true)]
    [string]$SecurityGroupId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "eu-north-1"
)

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📋 AWS Security Group Commands for: $SecurityGroupId" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Get your IP
try {
    $MyIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
    Write-Host "🌐 Your IP: $MyIP" -ForegroundColor Green
}
catch {
    $MyIP = "0.0.0.0"
    Write-Host "⚠️  Could not detect your IP. Using 0.0.0.0 for SSH (not recommended!)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Copy and paste these commands one by one:" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$rules = @(
    @{Port=22; Source="$MyIP/32"; Desc="SSH Management"},
    @{Port=80; Source="0.0.0.0/0"; Desc="HTTP"},
    @{Port=443; Source="0.0.0.0/0"; Desc="HTTPS"},
    @{Port=8501; Source="0.0.0.0/0"; Desc="Streamlit Dashboard"},
    @{Port=3000; Source="0.0.0.0/0"; Desc="Grafana Dashboard"},
    @{Port=445; Source="0.0.0.0/0"; Desc="SMB Honeypot"},
    @{Port=502; Source="0.0.0.0/0"; Desc="Modbus Honeypot"},
    @{Port=1025; Source="0.0.0.0/0"; Desc="Custom Honeypot"},
    @{Port=2121; Source="0.0.0.0/0"; Desc="FTP Honeypot"},
    @{Port=2222; Source="0.0.0.0/0"; Desc="SSH Honeypot"},
    @{Port=3307; Source="0.0.0.0/0"; Desc="MySQL Honeypot"},
    @{Port=5434; Source="0.0.0.0/0"; Desc="PostgreSQL Honeypot"},
    @{Port=8080; Source="0.0.0.0/0"; Desc="HTTP Honeypot"},
    @{Port=8443; Source="0.0.0.0/0"; Desc="HTTPS Honeypot"},
    @{Port=9090; Source="$MyIP/32"; Desc="Prometheus"}
)

$commands = @()
foreach ($rule in $rules) {
    $cmd = "aws ec2 authorize-security-group-ingress --group-id $SecurityGroupId --ip-permissions IpProtocol=tcp,FromPort=$($rule.Port),ToPort=$($rule.Port),IpRanges=`"[{CidrIp=$($rule.Source),Description='$($rule.Desc)'}]`" --region $Region"
    
    Write-Host "# $($rule.Desc) (Port $($rule.Port))" -ForegroundColor Cyan
    Write-Host $cmd -ForegroundColor White
    Write-Host ""
    
    $commands += $cmd
}

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Save to file
$outputFile = "aws_commands_$SecurityGroupId.txt"
$commands | Out-File -FilePath $outputFile -Encoding UTF8
Write-Host "✅ Commands saved to: $outputFile" -ForegroundColor Green
Write-Host ""

# Also create a batch script
$batchFile = "aws_commands_$SecurityGroupId.bat"
$batchContent = "@echo off`r`n"
$batchContent += "echo Adding Security Group Rules...`r`n"
$batchContent += "echo.`r`n"
foreach ($cmd in $commands) {
    $batchContent += "$cmd`r`n"
}
$batchContent += "echo.`r`n"
$batchContent += "echo Done!`r`n"
$batchContent += "pause`r`n"

$batchContent | Out-File -FilePath $batchFile -Encoding UTF8
Write-Host "✅ Batch script saved to: $batchFile" -ForegroundColor Green
Write-Host ""
Write-Host "📌 To run all at once (after installing AWS CLI):" -ForegroundColor Yellow
Write-Host "   $batchFile" -ForegroundColor White
Write-Host ""

<#
.SYNOPSIS
    Generates AWS CLI commands to add Security Group rules

.DESCRIPTION
    Creates a list of commands to add all required inbound rules for Cyber Mirage

.PARAMETER SecurityGroupId
    The Security Group ID (e.g., sg-0123456789abcdef0)

.PARAMETER Region
    AWS Region (default: eu-north-1)

.EXAMPLE
    .\generate_aws_commands.ps1 -SecurityGroupId "sg-xxxxx"
#>
