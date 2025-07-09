#!/bin/bash

# GitHub Actions Local Test Script
# This script mimics what GitHub Actions will do

echo "🚀 Testing CDC Scrapper GitHub Actions Setup"
echo "=============================================="

# Create mftp_config directory
echo "📁 Creating mftp_config directory..."
mkdir -p mftp_config/.session

# Create test env.py (you'll need to fill in real values)
echo "📝 Creating test env.py file..."
cat > mftp_config/env.py << 'EOF'
import os

# ERP Credentials - REPLACE WITH REAL VALUES
ROLL_NUMBER = "XXYYXXXXX"  # Your roll number
PASSWORD = "**********"   # Your ERP password
SECURITY_QUESTIONS_ANSWERS = {
    "What is your mother's maiden name?": "answer1",
    "What was the name of your first pet?": "answer2", 
    "What city were you born in?": "answer3"
}

# MongoDB Credentials
MONGO_ROOT_USERNAME = "mftp"
MONGO_ROOT_PASSWORD = "ptfm" 
MONGO_DATABASE = "mftp"
MONGO_PORT = "27017"
MONGO_URI = f'mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}@db:{MONGO_PORT}'
MONGO_COLLECTION = "AY_2024-25"

# Hoster Details
HOSTER_EMAIL = ["your_email@gmail.com"]  # REPLACE
HOSTER_NAME = "Your Name"  # REPLACE
HOSTER_ROLL = ROLL_NUMBER
HOSTER_INTERESTED_ROLLS = [ROLL_NUMBER]

# Company Notifier Config
COMPANY_NOTIFIER = True

# Shortlist Config  
SHORTLIST_NOTIFIER = True
ROLL_NAME = {
    HOSTER_ROLL: HOSTER_NAME,
}
ROLL_MAIL = {
    HOSTER_ROLL: HOSTER_EMAIL,
}

# Email Configuration - REPLACE WITH REAL VALUES
FROM_EMAIL = "your_gmail@gmail.com"  # Your Gmail
FROM_EMAIL_PASS = "app_password_here"  # Gmail app password
BCC_EMAIL_S = ["recipient@email.com"]  # Who gets notifications

# NTFY Configuration
NTFY_BASE_URL = "https://ntfy.sh"
NTFY_TOPICS = {
    "mftp-test": {},
    "mftp-placement-test": {
        "Type": "PLACEMENT",
    },
    "mftp-internship-test": {
        "Type": "INTERNSHIP", 
    },
    "mftp-ppo-test": {
        "Subject": "PPO",
    },
}
NTFY_TOPIC_ICON = "https://miro.medium.com/v2/resize:fit:600/1*O94LHxqfD_JGogOKyuBFgA.jpeg"
NTFY_USER = ""  # Optional
NTFY_PASS = ""  # Optional
HEIMDALL_COOKIE = ""  # Optional
EOF

# Create empty credential files
echo "📄 Creating empty credential files..."
echo '{}' > mftp_config/credentials.json
echo '{}' > mftp_config/token.json  
echo '{}' > mftp_config/mail_send_creds.json
echo '{}' > mftp_config/mail_send_token.json
echo '[]' > mftp_config/companies.json

# Create .env file for docker-compose
echo "⚙️  Creating .env file..."
cat > .env << 'EOF'
MFTP_CONFIG=./mftp_config
MFTP_MODE=python mftp.py --cron --smtp
MONGO_ROOT_USERNAME=mftp
MONGO_ROOT_PASSWORD=ptfm
MONGO_DATABASE=mftp
MONGO_PORT=27017
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit mftp_config/env.py with your real credentials"
echo "2. Run: docker-compose --env-file .env up --build"
echo "3. Test the scraper locally before pushing to GitHub"
echo ""
echo "🔐 For GitHub Actions, add these secrets to your repository:"
echo "   - ROLL_NUMBER"
echo "   - ERP_PASSWORD" 
echo "   - SECURITY_Q1, SECURITY_Q2, SECURITY_Q3"
echo "   - FROM_EMAIL, FROM_EMAIL_PASS"
echo "   - BCC_EMAIL, HOSTER_EMAIL, HOSTER_NAME"
echo ""
echo "🚀 Ready to deploy! Push to GitHub and check Actions tab."
