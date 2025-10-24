# 🚀 Deployment Guide: Streamlit Share + Supabase

Complete guide to deploy Fast Food Nutrition Agent to production.

---

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ GitHub account
- ✅ OpenAI API key ($5/month budget)
- ✅ Supabase account (free tier)
- ✅ Code pushed to GitHub repository

---

## 🎯 Quick Start (5 Steps)

### Step 1: Set Up Supabase Database

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Click "New Project"
   - Fill in:
     - Name: `fastfood-nutrition`
     - Database Password: (save this securely)
     - Region: (choose closest to your users)
   - Wait for project creation (~2 minutes)

2. **Run Database Schema**
   - In Supabase dashboard, go to **SQL Editor**
   - Click **New Query**
   - Copy entire contents of `supabase/schema.sql`
   - Paste and click **Run**
   - Verify: Check **Table Editor** to see tables created

3. **Get API Credentials**
   - Go to **Settings** → **API**
   - Copy these values:
     - `Project URL` (e.g., https://xxxxx.supabase.co)
     - `anon public` key (long string starting with eyJ...)
   - Save both for Step 4

---

### Step 2: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Production-ready deployment"

# Create GitHub repository and push
git remote add origin https://github.com/YOUR_USERNAME/fastfood-nutrition-agent.git
git branch -M main
git push -u origin main
```

---

### Step 3: Deploy to Streamlit Share

1. **Sign Up for Streamlit Share**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Authorize Streamlit

2. **Create New App**
   - Click **"New app"**
   - Select your repository
   - Set:
     - Main file path: `multi_agent_app.py`
     - Python version: `3.11`
   - Click **"Deploy"** (don't worry about secrets yet)

3. **Wait for Initial Deploy**
   - App will fail first time (missing secrets)
   - This is expected!

---

### Step 4: Configure Secrets

1. **In Streamlit Share Dashboard**
   - Click on your app
   - Click **⚙️ Settings** (three dots menu)
   - Select **Secrets**

2. **Add Secrets** (paste this template with YOUR values):

```toml
# OpenAI Configuration
OPENAI_API_KEY = "sk-your-actual-openai-key"

# Supabase Configuration  
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJxxxxx-your-actual-key"

# Environment
ENVIRONMENT = "production"

# Optional Settings
ENABLE_CONTENT_FILTER = "true"
ENABLE_MONITORING = "true"
```

3. **Save Secrets**
   - Click **Save**
   - App will automatically redeploy

---

### Step 5: Verify Deployment

1. **Check App Status**
   - Wait for "Running" status (1-2 minutes)
   - Click app URL

2. **Test Basic Functionality**
   - Create a test profile
   - Request a meal recommendation
   - Verify profile saves to database

3. **Check Database**
   - Go to Supabase **Table Editor**
   - Verify `user_profiles` has your test profile
   - Check `api_usage` for cost tracking

---

## 🔒 Security Checklist

Before going public:

- [ ] All secrets configured in Streamlit Share (not in code)
- [ ] `.env` file in `.gitignore` (never committed)
- [ ] Content filtering enabled
- [ ] Rate limiting active
- [ ] Database RLS policies reviewed
- [ ] Cost limits configured ($5/month)

---

## 💰 Cost Management

### OpenAI Budget Protection

Built-in limits:
- **Daily Limit**: $0.17 (~$5/month)
- **Hourly Requests**: 20 requests
- **Model**: GPT-3.5-turbo (most cost-effective)

Monitor usage:
```python
# View in app (add to sidebar)
from config.cost_control import get_usage_stats
stats = get_usage_stats()
```

### Supabase Free Tier Limits

- **Database**: 500MB
- **Bandwidth**: 2GB/month
- **API Requests**: Unlimited

Monitor in Supabase dashboard: **Settings** → **Usage**

---

## 📊 Monitoring

### Streamlit Share

- **Logs**: Click app → **Manage app** → **Logs**
- **Metrics**: **App analytics** tab
- **Status**: Green = healthy

### Supabase

- **Database Metrics**: **Database** → **Performance**
- **API Usage**: **Settings** → **API** → **Usage**
- **Logs**: **Logs** section

### Health Check

Add to your app:
```python
from monitoring.health import get_health
health = get_health()
```

---

## 🐛 Troubleshooting

### App Won't Start

**Error**: "Module not found"
- ✅ Check `requirements.txt` includes all dependencies
- ✅ Redeploy: **Settings** → **Reboot app**

**Error**: "OpenAI API key not found"
- ✅ Check secrets are saved in Streamlit Share
- ✅ Verify key starts with `sk-`
- ✅ Test key at [platform.openai.com](https://platform.openai.com)

**Error**: "Database connection failed"
- ✅ Verify Supabase URL and key in secrets
- ✅ Check Supabase project is running
- ✅ Test connection in Supabase SQL editor

### App is Slow

- Check OpenAI API response times
- Review Streamlit Share logs for errors
- Consider caching frequent queries

### Database Issues

**Profiles not saving**
- Check Supabase **Table Editor** for data
- Review **Logs** for SQL errors
- Verify schema was run correctly

**Out of storage**
- Free tier = 500MB
- Upgrade to Pro ($25/month) for 8GB
- Or clean old data

### Cost Overruns

**Exceeded $5/month**
- Check `api_usage` table in Supabase
- Review cost per request
- Reduce `max_tokens` in `config/environments.py`
- Implement aggressive caching

---

## 🔄 Updates & Maintenance

### Deploy Code Updates

```bash
# Make changes locally
git add .
git commit -m "Update: description of changes"
git push origin main

# Streamlit Share auto-deploys from main branch
# Watch deployment in dashboard
```

### Database Migrations

If you modify database schema:

1. Write migration SQL
2. Test locally first
3. Run in Supabase SQL Editor
4. Verify tables updated
5. Deploy code changes

### Backup Data

**Automatic backups** (Supabase):
- Free tier: Daily backups (7 days retention)
- Access: **Database** → **Backups**

**Manual backup**:
```sql
-- In Supabase SQL Editor
-- Export user_profiles
SELECT * FROM user_profiles;
```

---

## 📈 Scaling Plan

### Current Setup
- **Free Tier Limits**:
  - Streamlit: 1GB RAM, unlimited viewers
  - Supabase: 500MB DB, 50K active users
  - Cost: $5/month (OpenAI only)

### If You Grow

**100+ daily users**:
- Upgrade Supabase to Pro: $25/month (8GB, better performance)
- Increase OpenAI budget: $20-50/month
- Enable response caching

**1000+ daily users**:
- Consider Streamlit Teams: $250/month (more resources)
- Supabase Team plan: $599/month (dedicated resources)
- Implement CDN for static assets
- Add Redis for caching

---

## 🆘 Support

### Documentation
- Streamlit: [docs.streamlit.io](https://docs.streamlit.io)
- Supabase: [supabase.com/docs](https://supabase.com/docs)
- OpenAI: [platform.openai.com/docs](https://platform.openai.com/docs)

### Community
- Streamlit Forum: [discuss.streamlit.io](https://discuss.streamlit.io)
- Supabase Discord: [discord.supabase.com](https://discord.supabase.com)

### Issues
- Report bugs: Create GitHub issue
- Feature requests: GitHub discussions

---

## ✅ Production Checklist

Before announcing your app:

- [ ] Deployment successful
- [ ] All tests passing (`pytest`)
- [ ] Database schema created
- [ ] Secrets configured
- [ ] Test profile works end-to-end
- [ ] Content filter active
- [ ] Cost limits verified
- [ ] Monitoring enabled
- [ ] Error logging working
- [ ] Health check responds
- [ ] Documentation updated
- [ ] README has app URL

---

## 🎉 You're Live!

Your app is now available at:
```
https://YOUR_USERNAME-fastfood-nutrition-agent-multi-agent-app-xxxxx.streamlit.app
```

Share it with users and monitor:
- Streamlit logs for errors
- Supabase usage for scaling needs
- OpenAI costs for budget management

**Congratulations on your production deployment! 🚀**

