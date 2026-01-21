# GitHub Actions Setup for Scheduled Tasks

This project uses GitHub Actions to run scheduled tasks (like daily price sync) for free, allowing the Railway app to run serverless and save costs.

## How It Works

1. **GitHub Actions** runs the scheduled task daily at 3:30 PM IST (10:00 AM UTC)
2. **Railway app** runs serverless (saves ~$1-2/month)
3. Both connect to the same **Supabase database**

## Setup Instructions

### 1. Add GitHub Secret

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add:
   - **Name**: `DATABASE_URL`
   - **Value**: Your Supabase connection string (same as in Railway)

### 2. Configure Railway

In Railway Dashboard → Environment Variables:
- Set `ENABLE_SCHEDULER=false` (disables internal scheduler)

### 3. Test the Workflow

1. Go to **Actions** tab in GitHub
2. Click **Daily Price Sync** workflow
3. Click **Run workflow** → **Run workflow** (manual trigger)
4. Check the logs to verify it works

## Switching Between Internal and External Scheduler

### Use Internal Scheduler (Railway always-on):
```bash
# In Railway Environment Variables
ENABLE_SCHEDULER=true
```
- Railway app stays always-on
- Costs ~$2-3/month

### Use External Scheduler (GitHub Actions + Railway serverless):
```bash
# In Railway Environment Variables
ENABLE_SCHEDULER=false
```
- GitHub Actions runs the task (free)
- Railway app can be serverless
- Costs ~$1-2/month

## Monitoring

- **GitHub Actions logs**: Check the Actions tab for task execution logs
- **Railway logs**: Check Railway dashboard for app logs
- **Supabase**: Verify data is being updated in your database

## Cost Savings

- **Always-on**: ~$2-3/month (within $5 free tier)
- **Serverless + GitHub Actions**: ~$1-2/month (saves $1/month)
- **GitHub Actions**: $0 (completely free)

This setup gives you the flexibility to choose based on your needs!
