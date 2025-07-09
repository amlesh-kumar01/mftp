@echo off
echo 🚀 Testing CDC Scrapper GitHub Actions Setup
echo ==============================================

REM Create mftp_config directory
echo 📁 Creating mftp_config directory...
if not exist "mftp_config" mkdir mftp_config
if not exist "mftp_config\.session" mkdir mftp_config\.session

REM Create test env.py (you'll need to fill in real values)
echo 📝 Creating test env.py file...
(
echo import os
echo.
echo # ERP Credentials - REPLACE WITH REAL VALUES
echo ROLL_NUMBER = "XXYYXXXXX"  # Your roll number
echo PASSWORD = "**********"   # Your ERP password
echo SECURITY_QUESTIONS_ANSWERS = {
echo     "What is your mother's maiden name?": "answer1",
echo     "What was the name of your first pet?": "answer2", 
echo     "What city were you born in?": "answer3"
echo }
echo.
echo # MongoDB Credentials
echo MONGO_ROOT_USERNAME = "mftp"
echo MONGO_ROOT_PASSWORD = "ptfm" 
echo MONGO_DATABASE = "mftp"
echo MONGO_PORT = "27017"
echo MONGO_URI = f'mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}@db:{MONGO_PORT}'
echo MONGO_COLLECTION = "AY_2024-25"
echo.
echo # Hoster Details
echo HOSTER_EMAIL = ["your_email@gmail.com"]  # REPLACE
echo HOSTER_NAME = "Your Name"  # REPLACE
echo HOSTER_ROLL = ROLL_NUMBER
echo HOSTER_INTERESTED_ROLLS = [ROLL_NUMBER]
echo.
echo # Company Notifier Config
echo COMPANY_NOTIFIER = True
echo.
echo # Shortlist Config  
echo SHORTLIST_NOTIFIER = True
echo ROLL_NAME = {
echo     HOSTER_ROLL: HOSTER_NAME,
echo }
echo ROLL_MAIL = {
echo     HOSTER_ROLL: HOSTER_EMAIL,
echo }
echo.
echo # Email Configuration - REPLACE WITH REAL VALUES
echo FROM_EMAIL = "your_gmail@gmail.com"  # Your Gmail
echo FROM_EMAIL_PASS = "app_password_here"  # Gmail app password
echo BCC_EMAIL_S = ["recipient@email.com"]  # Who gets notifications
echo.
echo # NTFY Configuration
echo NTFY_BASE_URL = "https://ntfy.sh"
echo NTFY_TOPICS = {
echo     "mftp-test": {},
echo     "mftp-placement-test": {
echo         "Type": "PLACEMENT",
echo     },
echo     "mftp-internship-test": {
echo         "Type": "INTERNSHIP", 
echo     },
echo     "mftp-ppo-test": {
echo         "Subject": "PPO",
echo     },
echo }
echo NTFY_TOPIC_ICON = "https://miro.medium.com/v2/resize:fit:600/1*O94LHxqfD_JGogOKyuBFgA.jpeg"
echo NTFY_USER = ""  # Optional
echo NTFY_PASS = ""  # Optional
echo HEIMDALL_COOKIE = ""  # Optional
) > mftp_config\env.py

REM Create empty credential files
echo 📄 Creating empty credential files...
echo {} > mftp_config\credentials.json
echo {} > mftp_config\token.json  
echo {} > mftp_config\mail_send_creds.json
echo {} > mftp_config\mail_send_token.json
echo [] > mftp_config\companies.json

REM Create .env file for docker-compose
echo ⚙️  Creating .env file...
(
echo MFTP_CONFIG=./mftp_config
echo MFTP_MODE=python mftp.py --cron --smtp
echo MONGO_ROOT_USERNAME=mftp
echo MONGO_ROOT_PASSWORD=ptfm
echo MONGO_DATABASE=mftp
echo MONGO_PORT=27017
) > .env

echo.
echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo 1. Edit mftp_config\env.py with your real credentials
echo 2. Run: docker-compose --env-file .env up --build
echo 3. Test the scraper locally before pushing to GitHub
echo.
echo 🔐 For GitHub Actions, add these secrets to your repository:
echo    - ROLL_NUMBER
echo    - ERP_PASSWORD 
echo    - SECURITY_Q1, SECURITY_Q2, SECURITY_Q3
echo    - FROM_EMAIL, FROM_EMAIL_PASS
echo    - BCC_EMAIL, HOSTER_EMAIL, HOSTER_NAME
echo.
echo 🚀 Ready to deploy! Push to GitHub and check Actions tab.
pause
