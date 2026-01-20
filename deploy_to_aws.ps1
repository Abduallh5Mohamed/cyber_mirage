# ═══════════════════════════════════════════════════════════
# 🚀 Cyber Mirage - AWS Production Deployment Script
# ═══════════════════════════════════════════════════════════
# هذا السكريبت سيساعدك في نشر المشروع بالكامل على AWS
# ═══════════════════════════════════════════════════════════

param(
    [Parameter(Mandatory=$false)]
    [string]$EC2_IP,
    
    [Parameter(Mandatory=$false)]
    [string]$KeyPath,
    
    [Parameter(Mandatory=$false)]
    [switch]$ConfigureSecurityGroup,
    
    [Parameter(Mandatory=$false)]
    [string]$SecurityGroupId
)

$ErrorActionPreference = "Stop"

# ═══════════════════════════════════════════════════════════
# Functions
# ═══════════════════════════════════════════════════════════

function Write-Step {
    param($Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════
# Step 1: Configure Security Group (if needed)
# ═══════════════════════════════════════════════════════════

if ($ConfigureSecurityGroup -and $SecurityGroupId) {
    Write-Step "Step 1: Configuring Security Group"
    
    Write-Info "Getting your public IP..."
    try {
        $MyIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
        Write-Success "Your IP: $MyIP"
    }
    catch {
        Write-Warning "Could not detect your IP automatically. Please add rules manually."
        $MyIP = "0.0.0.0"
    }
    
    Write-Info "Adding required ports to Security Group: $SecurityGroupId"
    Write-Warning "You need AWS CLI installed and configured for this!"
    Write-Info "Run: aws configure"
    
    $rules = @(
        @{Port=22; Source="$MyIP/32"; Desc="SSH Management"},
        @{Port=8501; Source="0.0.0.0/0"; Desc="Streamlit Dashboard"},
        @{Port=3000; Source="0.0.0.0/0"; Desc="Grafana"},
        @{Port=445; Source="0.0.0.0/0"; Desc="SMB Honeypot"},
        @{Port=502; Source="0.0.0.0/0"; Desc="Modbus Honeypot"},
        @{Port=1025; Source="0.0.0.0/0"; Desc="Custom Honeypot"},
        @{Port=2121; Source="0.0.0.0/0"; Desc="FTP Honeypot"},
        @{Port=2222; Source="0.0.0.0/0"; Desc="SSH Honeypot"},
        @{Port=3307; Source="0.0.0.0/0"; Desc="MySQL Honeypot"},
        @{Port=5434; Source="0.0.0.0/0"; Desc="PostgreSQL Honeypot"},
        @{Port=8080; Source="0.0.0.0/0"; Desc="HTTP Honeypot"},
        @{Port=8443; Source="0.0.0.0/0"; Desc="HTTPS Honeypot"}
    )
    
    foreach ($rule in $rules) {
        Write-Host "  Adding Port $($rule.Port) - $($rule.Desc)..." -NoNewline
        try {
            aws ec2 authorize-security-group-ingress `
                --group-id $SecurityGroupId `
                --ip-permissions IpProtocol=tcp,FromPort=$($rule.Port),ToPort=$($rule.Port),IpRanges="[{CidrIp=$($rule.Source),Description='$($rule.Desc)'}]" `
                --region eu-north-1 2>$null
            Write-Host " ✅" -ForegroundColor Green
        }
        catch {
            Write-Host " ⚠️ (might already exist)" -ForegroundColor Yellow
        }
    }
}

# ═══════════════════════════════════════════════════════════
# Step 2: Get EC2 Information
# ═══════════════════════════════════════════════════════════

Write-Step "Step 2: EC2 Instance Information"

if (-not $EC2_IP) {
    Write-Info "Please provide the EC2 Public IP address:"
    Write-Host "You can find it in AWS Console → EC2 → Instances → Your Instance" -ForegroundColor Gray
    $EC2_IP = Read-Host "Enter EC2 Public IP"
}

Write-Success "Target Server: $EC2_IP"

# ═══════════════════════════════════════════════════════════
# Step 3: Check SSH Key
# ═══════════════════════════════════════════════════════════

Write-Step "Step 3: SSH Key Configuration"

if (-not $KeyPath) {
    Write-Info "Please provide the path to your .pem key file:"
    $KeyPath = Read-Host "Enter key path (e.g., C:\path\to\key.pem)"
}

if (-not (Test-Path $KeyPath)) {
    Write-Error-Custom "Key file not found: $KeyPath"
    Write-Info "Please download your key from AWS and try again."
    exit 1
}

Write-Success "Key file found: $KeyPath"

# Fix key permissions if needed
Write-Info "Setting correct permissions for SSH key..."
icacls $KeyPath /inheritance:r | Out-Null
icacls $KeyPath /grant:r "$($env:USERNAME):R" | Out-Null
Write-Success "Key permissions set"

# ═══════════════════════════════════════════════════════════
# Step 4: Test SSH Connection
# ═══════════════════════════════════════════════════════════

Write-Step "Step 4: Testing SSH Connection"

Write-Info "Attempting to connect to: ubuntu@$EC2_IP"
Write-Warning "This may take a moment on first connection..."

$testConnection = "echo 'Connection successful'"
$result = ssh -i $KeyPath -o StrictHostKeyChecking=no -o ConnectTimeout=10 ubuntu@$EC2_IP $testConnection 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "SSH connection successful!"
} else {
    Write-Error-Custom "Cannot connect to server. Please check:"
    Write-Host "  1. Security Group allows SSH from your IP" -ForegroundColor Yellow
    Write-Host "  2. Instance is running" -ForegroundColor Yellow
    Write-Host "  3. Key pair is correct" -ForegroundColor Yellow
    Write-Host "  4. Public IP is correct: $EC2_IP" -ForegroundColor Yellow
    exit 1
}

# ═══════════════════════════════════════════════════════════
# Step 5: Create Deployment Package
# ═══════════════════════════════════════════════════════════

Write-Step "Step 5: Creating Deployment Package"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$packageName = "cyber_mirage_$timestamp.tar.gz"

Write-Info "Packaging project files..."
Write-Warning "This may take a few minutes..."

Push-Location $PSScriptRoot

# Create tarball (excluding unnecessary files)
$excludePatterns = @(
    "*.tar.gz",
    "venv/",
    "__pycache__/",
    "*.pyc",
    ".git/",
    "*.log",
    ".env",
    "data/logs/*",
    "data/captures/*"
)

Write-Info "Compressing files..."
tar --exclude-vcs `
    --exclude="venv" `
    --exclude="__pycache__" `
    --exclude="*.pyc" `
    --exclude="*.log" `
    --exclude=".git" `
    --exclude="*.tar.gz" `
    -czf $packageName .

if (Test-Path $packageName) {
    $fileSize = [math]::Round((Get-Item $packageName).Length / 1MB, 2)
    Write-Success "Package created: $packageName ($fileSize MB)"
} else {
    Write-Error-Custom "Failed to create package"
    exit 1
}

Pop-Location

# ═══════════════════════════════════════════════════════════
# Step 6: Upload to Server
# ═══════════════════════════════════════════════════════════

Write-Step "Step 6: Uploading to Server"

Write-Info "Uploading package to $EC2_IP..."
Write-Warning "This may take several minutes depending on your connection..."

scp -i $KeyPath -o StrictHostKeyChecking=no $packageName ubuntu@$EC2_IP:~/

if ($LASTEXITCODE -eq 0) {
    Write-Success "Upload complete!"
} else {
    Write-Error-Custom "Upload failed"
    exit 1
}

# Clean up local package
Remove-Item $packageName -Force
Write-Info "Local package cleaned up"

# ═══════════════════════════════════════════════════════════
# Step 7: Server Setup Script
# ═══════════════════════════════════════════════════════════

Write-Step "Step 7: Preparing Server Setup Script"

$setupScript = @'
#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════"
echo "🚀 Cyber Mirage - Server Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Update system
echo -e "${CYAN}📦 Updating system packages...${NC}"
sudo apt update -qq
sudo apt upgrade -y -qq
echo -e "${GREEN}✅ System updated${NC}"

# Install Docker
if ! command -v docker &> /dev/null; then
    echo -e "${CYAN}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${CYAN}🐳 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

# Verify installations
echo ""
echo -e "${CYAN}📋 Verifying installations:${NC}"
docker --version
docker-compose --version

# Extract project
echo ""
echo -e "${CYAN}📂 Extracting project files...${NC}"
mkdir -p ~/cyber_mirage
tar -xzf ~/cyber_mirage_*.tar.gz -C ~/cyber_mirage/
cd ~/cyber_mirage

# Create .env file
echo ""
echo -e "${CYAN}⚙️  Creating environment configuration...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate secure passwords
    POSTGRES_PASS=$(openssl rand -base64 32 | tr -d '/+=' | head -c 32)
    REDIS_PASS=$(openssl rand -base64 32 | tr -d '/+=' | head -c 32)
    GRAFANA_PASS=$(openssl rand -base64 16 | tr -d '/+=' | head -c 16)
    
    # Update .env
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASS/" .env
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASS/" .env
    sed -i "s/GRAFANA_PASSWORD=.*/GRAFANA_PASSWORD=$GRAFANA_PASS/" .env
    sed -i "s/ENVIRONMENT=.*/ENVIRONMENT=production/" .env
    
    echo -e "${GREEN}✅ Environment file created${NC}"
    echo ""
    echo -e "${YELLOW}📝 IMPORTANT - Save these credentials:${NC}"
    echo -e "${CYAN}PostgreSQL Password: ${NC}$POSTGRES_PASS"
    echo -e "${CYAN}Redis Password: ${NC}$REDIS_PASS"
    echo -e "${CYAN}Grafana Password: ${NC}$GRAFANA_PASS"
    echo ""
    
    # Save credentials to file
    cat > ~/cyber_mirage_credentials.txt <<EOF
Cyber Mirage Production Credentials
Generated: $(date)
════════════════════════════════════

PostgreSQL Password: $POSTGRES_PASS
Redis Password: $REDIS_PASS
Grafana Password: $GRAFANA_PASS

Grafana URL: http://$(curl -s ifconfig.me):3000
Dashboard URL: http://$(curl -s ifconfig.me):8501

Important: Keep this file secure!
EOF
    
    echo -e "${GREEN}✅ Credentials saved to ~/cyber_mirage_credentials.txt${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists, skipping${NC}"
fi

# Create required directories
echo ""
echo -e "${CYAN}📁 Creating required directories...${NC}"
mkdir -p data/logs data/captures data/forensics data/models data/sessions
echo -e "${GREEN}✅ Directories created${NC}"

# Pull Docker images
echo ""
echo -e "${CYAN}🐳 Pulling Docker images...${NC}"
echo -e "${YELLOW}⏳ This may take 5-10 minutes...${NC}"
docker-compose -f docker-compose.production.yml pull

# Start services
echo ""
echo -e "${CYAN}🚀 Starting services...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Wait for services to start
echo ""
echo -e "${CYAN}⏳ Waiting for services to initialize...${NC}"
sleep 30

# Check status
echo ""
echo -e "${CYAN}📊 Service Status:${NC}"
docker-compose -f docker-compose.production.yml ps

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${CYAN}🌐 Access Your Application:${NC}"
echo ""
echo -e "  📊 Main Dashboard:  ${YELLOW}http://$PUBLIC_IP:8501${NC}"
echo -e "  📈 Grafana:         ${YELLOW}http://$PUBLIC_IP:3000${NC}"
echo -e "  📡 Prometheus:      ${YELLOW}http://$PUBLIC_IP:9090${NC}"
echo ""
echo -e "${CYAN}🔐 Default Credentials:${NC}"
echo -e "  Grafana: admin / (check ~/cyber_mirage_credentials.txt)"
echo ""
echo -e "${CYAN}📝 Useful Commands:${NC}"
echo -e "  View logs:    ${YELLOW}docker-compose -f docker-compose.production.yml logs -f${NC}"
echo -e "  Stop all:     ${YELLOW}docker-compose -f docker-compose.production.yml down${NC}"
echo -e "  Restart all:  ${YELLOW}docker-compose -f docker-compose.production.yml restart${NC}"
echo -e "  Check status: ${YELLOW}docker ps${NC}"
echo ""
echo -e "${GREEN}🎉 Your Cyber Mirage system is now live!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
'@

# Save setup script
$setupScriptPath = Join-Path $PSScriptRoot "server_setup.sh"
$setupScript | Out-File -FilePath $setupScriptPath -Encoding UTF8 -NoNewline

Write-Success "Setup script created"

# Upload setup script
Write-Info "Uploading setup script..."
scp -i $KeyPath -o StrictHostKeyChecking=no $setupScriptPath ubuntu@$EC2_IP:~/setup.sh

if ($LASTEXITCODE -eq 0) {
    Write-Success "Setup script uploaded"
} else {
    Write-Error-Custom "Failed to upload setup script"
    exit 1
}

# Clean up local script
Remove-Item $setupScriptPath -Force

# ═══════════════════════════════════════════════════════════
# Step 8: Execute Remote Setup
# ═══════════════════════════════════════════════════════════

Write-Step "Step 8: Executing Remote Setup"

Write-Info "Starting automated server setup..."
Write-Warning "This will take 10-15 minutes. Do not close this window!"
Write-Host ""

# Execute setup script
ssh -i $KeyPath -o StrictHostKeyChecking=no ubuntu@$EC2_IP "chmod +x ~/setup.sh && ~/setup.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Success "Remote setup completed successfully!"
} else {
    Write-Warning "Setup completed with warnings. Check the output above."
}

# ═══════════════════════════════════════════════════════════
# Step 9: Final Information
# ═══════════════════════════════════════════════════════════

Write-Step "Step 9: Deployment Summary"

Write-Host ""
Write-Host "🎉 " -NoNewline -ForegroundColor Green
Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Yellow
Write-Host ""

Write-Info "Your Cyber Mirage system is now running on AWS!"
Write-Host ""

Write-Host "📊 Access URLs:" -ForegroundColor Cyan
Write-Host "  • Main Dashboard:  http://$EC2_IP:8501" -ForegroundColor White
Write-Host "  • Grafana:         http://$EC2_IP:3000" -ForegroundColor White
Write-Host "  • Prometheus:      http://$EC2_IP:9090" -ForegroundColor White
Write-Host ""

Write-Host "🔐 Credentials:" -ForegroundColor Cyan
Write-Host "  Saved on server: ~/cyber_mirage_credentials.txt" -ForegroundColor White
Write-Host "  To view: ssh -i $KeyPath ubuntu@$EC2_IP 'cat ~/cyber_mirage_credentials.txt'" -ForegroundColor Gray
Write-Host ""

Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
Write-Host "  Connect to server:" -ForegroundColor Yellow
Write-Host "    ssh -i $KeyPath ubuntu@$EC2_IP" -ForegroundColor Gray
Write-Host ""
Write-Host "  View logs:" -ForegroundColor Yellow
Write-Host "    docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor Gray
Write-Host ""
Write-Host "  Restart services:" -ForegroundColor Yellow
Write-Host "    docker-compose -f docker-compose.production.yml restart" -ForegroundColor Gray
Write-Host ""

Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open http://$EC2_IP:8501 in your browser" -ForegroundColor White
Write-Host "  2. Check Grafana dashboards at http://$EC2_IP:3000" -ForegroundColor White
Write-Host "  3. Monitor honeypot activity" -ForegroundColor White
Write-Host "  4. Set up alerts and notifications" -ForegroundColor White
Write-Host ""

Write-Success "All done! Your system is ready for production use."
Write-Host ""

# Save deployment info
$deploymentInfo = @"
Cyber Mirage AWS Deployment
═══════════════════════════════════════════════════════════
Deployment Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Server IP: $EC2_IP
Region: eu-north-1
Key File: $KeyPath

Access URLs:
- Dashboard: http://$EC2_IP:8501
- Grafana: http://$EC2_IP:3000
- Prometheus: http://$EC2_IP:9090

SSH Command:
ssh -i "$KeyPath" ubuntu@$EC2_IP

Credentials Location:
~/cyber_mirage_credentials.txt (on server)

Status: ✅ DEPLOYED
═══════════════════════════════════════════════════════════
"@

$deploymentInfo | Out-File -FilePath (Join-Path $PSScriptRoot "deployment_info.txt") -Encoding UTF8
Write-Info "Deployment info saved to: deployment_info.txt"
Write-Host ""

<#
.SYNOPSIS
    Complete AWS deployment script for Cyber Mirage

.DESCRIPTION
    Automates the entire deployment process:
    1. Configures Security Group (optional)
    2. Tests SSH connection
    3. Packages project files
    4. Uploads to EC2
    5. Installs Docker & Docker Compose
    6. Configures environment
    7. Starts all services

.PARAMETER EC2_IP
    Public IP address of your EC2 instance

.PARAMETER KeyPath
    Path to your .pem key file

.PARAMETER ConfigureSecurityGroup
    If set, will attempt to configure Security Group via AWS CLI

.PARAMETER SecurityGroupId
    Security Group ID to configure (required if ConfigureSecurityGroup is set)

.EXAMPLE
    .\deploy_to_aws.ps1 -EC2_IP "13.60.1.123" -KeyPath "C:\keys\cyber-mirage-key.pem"
    
.EXAMPLE
    .\deploy_to_aws.ps1 -EC2_IP "13.60.1.123" -KeyPath "C:\keys\key.pem" -ConfigureSecurityGroup -SecurityGroupId "sg-xxxxx"

.NOTES
    Requirements:
    - SSH client (included in Windows 10+)
    - tar command (included in Windows 10+)
    - Internet connection
    - AWS EC2 instance running
    - Valid .pem key file
    
    Optional:
    - AWS CLI (for Security Group configuration)
#>
