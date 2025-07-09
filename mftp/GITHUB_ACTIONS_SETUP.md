# GitHub Actions Deployment Guide

This guide will help you deploy the CDC Notice Scrapper on GitHub Actions using Docker Compose to run every 10 minutes.

## Setup Instructions

### 1. Prepare Your Configuration

**Important**: This workflow uses your existing `mftp_config` directory instead of GitHub Secrets.

Make sure your `mftp_config` directory contains:
- ✅ `env.py` - Your environment configuration with credentials
- ✅ `credentials.json` - Google API credentials (if using Gmail API)
- ✅ `token.json` - Google API tokens (if using Gmail API)  
- ✅ `mail_send_creds.json` - Additional mail credentials
- ✅ `mail_send_token.json` - Additional mail tokens
- ✅ `companies.json` - Companies data (will be created if missing)

**Security Note**: Make sure your repository is **PRIVATE** since it will contain your credentials.

### 2. Verify Your env.py Configuration

Your `mftp_config/env.py` should look like this:

```python
# ERP Credentials
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
HOSTER_EMAIL = ["your_email@gmail.com"]
HOSTER_NAME = "Your Name"
HOSTER_ROLL = ROLL_NUMBER
HOSTER_INTERESTED_ROLLS = [ROLL_NUMBER]

# Feature Flags
COMPANY_NOTIFIER = True
SHORTLIST_NOTIFIER = True
ROLL_NAME = {
    HOSTER_ROLL: HOSTER_NAME,
}
ROLL_MAIL = {
    HOSTER_ROLL: HOSTER_EMAIL,
}

# Email Configuration
FROM_EMAIL = "your_gmail@gmail.com"  # Your Gmail
FROM_EMAIL_PASS = "app_password_here"  # Gmail app password
BCC_EMAIL_S = ["recipient@email.com"]  # Who gets notifications

# NTFY Configuration (Optional)
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
```

### 3. Push Code to GitHub

**Important**: Ensure your repository is PRIVATE for security.

```bash
# Make sure mftp_config directory is included
git add mftp_config/
git add .github/
git add .
git commit -m "Add GitHub Actions workflow with mftp_config"
git push origin main
```

### 4. No GitHub Secrets Required! 

Since all configuration is in your `mftp_config/env.py` file, you don't need to add any GitHub secrets.

### 5. Test the Workflow

#### Manual Test
1. Go to Actions tab in your GitHub repository
2. Click on "CDC Notice Scraper" workflow
3. Click "Run workflow" → "Run workflow"
4. Monitor the execution

#### Check Scheduled Runs
- The workflow runs automatically every 10 minutes
- View logs in the Actions tab
- Download artifacts for session data and logs

## Workflow Features

✅ **Automated Scheduling**: Runs every 10 minutes  
✅ **Docker Compose**: Uses your existing docker setup  
✅ **Uses Existing Config**: No need for GitHub secrets - uses your mftp_config files
✅ **Error Handling**: Continues running even if individual runs fail  
✅ **Logging**: Uploads logs and session data as artifacts  
✅ **Manual Trigger**: Can be triggered manually for testing  
✅ **Resource Efficient**: Automatically cleans up containers  

## Security Considerations

🔒 **Important**: Since your `mftp_config/env.py` contains sensitive credentials:

1. **Make your repository PRIVATE** - This is crucial!
2. **Never share your repository** with unauthorized users
3. **Use Gmail App Passwords**, not your main password
4. **Regularly rotate your credentials**
5. **Monitor your GitHub Actions usage**

## How It Works

1. **Checkout**: Gets your code including `mftp_config/` directory
2. **Verify Config**: Checks that `env.py` exists and creates missing files
3. **Build**: Uses Docker Compose to build containers
4. **Run**: Executes scraper once with `--cron --smtp`
5. **Log**: Captures all output and uploads artifacts
6. **Cleanup**: Removes containers to save resources

## Monitoring

### View Logs
1. Go to Actions tab
2. Click on any workflow run
3. Expand "Build and run with Docker Compose" step
4. View real-time logs

### Download Artifacts
1. Go to completed workflow run
2. Scroll down to "Artifacts" section
3. Download `scraper-logs-*` for session data

### Check Status
- ✅ Green checkmark = Successful run
- ❌ Red X = Failed run (click to see error details)
- 🟡 Yellow dot = Currently running

## Troubleshooting

### Common Issues

1. **env.py not found**
   - Ensure `mftp_config/env.py` exists in your repository
   - Check that you've committed the mftp_config directory

2. **ERP Login Failed**
   - Verify ROLL_NUMBER and PASSWORD in env.py
   - Check security question answers

3. **Email Sending Failed**
   - Ensure Gmail app password is correct in env.py
   - Verify FROM_EMAIL is correct

4. **Repository is Public**
   - Make sure your repository is PRIVATE to protect credentials
   - Go to Settings → General → Danger Zone → Change visibility

### Debug Steps

1. **Check workflow logs**:
   ```
   Actions → Latest Run → Verify mftp_config files exist
   ```

2. **Verify your config locally**:
   ```bash
   python -c "import mftp_config.env as env; print('Config loaded successfully')"
   ```

3. **Test Docker Compose locally**:
   ```bash
   docker-compose --env-file .env up --build
   ```

## Free Usage Limits

GitHub Actions provides:
- ✅ **2,000 minutes/month** for free accounts
- ✅ **Unlimited** for public repositories
- Each run takes ~2-5 minutes
- Running every 10 minutes = ~8,640 minutes/month
- **Recommendation**: Consider running every 15-20 minutes for private repos

## Security Notes

- All sensitive data is stored as encrypted secrets
- Secrets are not exposed in logs
- Session tokens are saved as artifacts (encrypted)
- MongoDB runs in isolated container network

## Customization

### Change Schedule
Edit `.github/workflows/cdc-scraper.yml`:
```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
  - cron: '0 */2 * * *'   # Every 2 hours
  - cron: '0 9-17 * * 1-5' # Business hours only
```

### Modify Notification Methods
Update the command in workflow:
```yaml
MFTP_MODE=python mftp.py --cron --smtp --ntfy
```

---

🎉 **Your CDC Notice Scrapper is now automated!** 

The scraper will run every 10 minutes and send you notifications about new companies and notices automatically.
