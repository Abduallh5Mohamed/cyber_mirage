# Fix AWS Security Group - Allow SSH from your IP
# Run this if you have AWS CLI configured

# Get your current public IP
$myIP = (Invoke-WebRequest -Uri "https://api.ipify.org").Content

Write-Host "Your Public IP: $myIP" -ForegroundColor Cyan

# Instructions
Write-Host "`n=== AWS Security Group Fix ===" -ForegroundColor Yellow
Write-Host "`n1. Go to AWS Console: https://console.aws.amazon.com/ec2/" -ForegroundColor White
Write-Host "2. Click on 'Security Groups' in the left menu" -ForegroundColor White
Write-Host "3. Find the security group for instance with IP: 13.48.194.249" -ForegroundColor White
Write-Host "4. Click 'Edit inbound rules'" -ForegroundColor White
Write-Host "5. Add this rule:" -ForegroundColor White
Write-Host "   - Type: SSH" -ForegroundColor Green
Write-Host "   - Protocol: TCP" -ForegroundColor Green
Write-Host "   - Port: 22" -ForegroundColor Green
Write-Host "   - Source: $myIP/32" -ForegroundColor Green
Write-Host "6. Save rules" -ForegroundColor White

Write-Host "`n=== Or use AWS CLI (if configured) ===" -ForegroundColor Yellow
Write-Host "aws ec2 authorize-security-group-ingress ``" -ForegroundColor Cyan
Write-Host "  --group-id sg-YOUR_GROUP_ID ``" -ForegroundColor Cyan
Write-Host "  --protocol tcp ``" -ForegroundColor Cyan
Write-Host "  --port 22 ``" -ForegroundColor Cyan
Write-Host "  --cidr $myIP/32" -ForegroundColor Cyan

# Save to file
$myIP | Out-File -FilePath "a:\cyber_mirage\my_current_ip.txt" -NoNewline
Write-Host "`nYour IP saved to: a:\cyber_mirage\my_current_ip.txt" -ForegroundColor Green
