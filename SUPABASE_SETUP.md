# 🗄️ Supabase Database Setup Guide

Quick guide to set up your PostgreSQL database with Supabase.

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Create Supabase Project

1. **Go to Supabase**
   - Visit [supabase.com](https://supabase.com)
   - Sign in or create account (free)

2. **Create New Project**
   - Click **"New Project"**
   - Fill in details:
     - **Name**: `fastfood-nutrition` (or your choice)
     - **Database Password**: Create a strong password (save it!)
     - **Region**: Choose closest to you
     - **Plan**: Free (500MB database)
   - Click **"Create new project"**
   - Wait ~2 minutes for setup

### Step 2: Run Database Schema

1. **Open SQL Editor**
   - In your Supabase project dashboard
   - Click **"SQL Editor"** in left sidebar
   - Click **"New Query"**

2. **Copy & Paste Schema**
   - Open `supabase/schema.sql` in your project
   - Copy ALL contents (470+ lines)
   - Paste into SQL Editor
   - Click **"Run"** (or press Ctrl+Enter)

3. **Verify Tables Created**
   - Click **"Table Editor"** in left sidebar
   - You should see:
     - ✅ `user_profiles`
     - ✅ `meal_history`
     - ✅ `api_usage`
     - ✅ `error_logs`
     - ✅ `system_metrics`

### Step 3: Get API Credentials

1. **Navigate to Settings**
   - Click **"Settings"** (⚙️ icon) in left sidebar
   - Click **"API"** in settings menu

2. **Copy Credentials**
   - **Project URL**: Copy the URL (e.g., `https://xxxxx.supabase.co`)
   - **API Keys**: Copy the `anon public` key (long string starting with `eyJ...`)

### Step 4: Add to Your App

**For Local Development:**

Create/edit `.env` file in project root:
```env
# OpenAI (required)
OPENAI_API_KEY=sk-your-openai-key-here

# Supabase (add these)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxx-your-anon-key-here

# Environment
ENVIRONMENT=development
```

**For Streamlit Share Deployment:**

1. Go to your app in [share.streamlit.io](https://share.streamlit.io)
2. Click **⚙️ Settings** → **Secrets**
3. Add the same credentials:

```toml
OPENAI_API_KEY = "sk-your-key"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJxxxxx-your-key"
ENVIRONMENT = "production"
```

---

## ✅ Test Database Connection

### Local Test

1. **Restart your app**:
   ```bash
   streamlit run multi_agent_app.py
   ```

2. **Check System Health**:
   - Look at sidebar → "🏥 System Health"
   - Database should show: ✅ **Healthy** or ✅ **Database connection OK**

3. **Test Profile Creation**:
   - Create a test profile in the app
   - It should save to Supabase (not just JSON)

### Verify in Supabase

1. **Go to Table Editor**
2. **Click `user_profiles` table**
3. **See your test profile** appear in the table

---

## 🎯 What You Get

With Supabase connected:

✅ **Persistent Storage**: Profiles saved in PostgreSQL  
✅ **Real-time Sync**: Data available across all sessions  
✅ **Meal History**: All meals tracked in database  
✅ **Cost Tracking**: API usage monitored automatically  
✅ **Error Logging**: Errors logged for debugging  
✅ **Performance Metrics**: System metrics tracked  
✅ **Auto Fallback**: Still uses JSON if database unavailable  

---

## 🔍 Database Schema Overview

### Tables Created

1. **`user_profiles`** - User preferences and stats
   - Profile name, dietary restrictions
   - Favorite restaurants
   - Calorie targets
   - Statistics (meals tracked, avg calories, ratings)

2. **`meal_history`** - Meal tracking
   - Restaurant, calories, rating
   - Timestamp
   - Linked to profiles

3. **`api_usage`** - Cost monitoring
   - Model used, tokens, estimated cost
   - Request type, success/failure
   - Automatic tracking

4. **`error_logs`** - Error tracking
   - Error type, message, stack trace
   - Severity levels
   - Resolution status

5. **`system_metrics`** - Performance
   - Request duration, agent execution times
   - Database query performance
   - Custom metrics

### Auto-Features

✅ **Triggers**: Automatically update statistics when meals added  
✅ **Indexes**: Optimized queries for fast performance  
✅ **Views**: Pre-built queries for monitoring  
✅ **Functions**: Automatic timestamp updates  

---

## 🛠️ Troubleshooting

### "Database not configured, using JSON fallback"

**Cause**: Credentials not set or incorrect

**Fix**:
1. Check `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`
2. Restart Streamlit: `Ctrl+C` then `streamlit run multi_agent_app.py`
3. Check sidebar health status

### "Database connection failed"

**Cause**: Network issue or wrong credentials

**Fix**:
1. Verify Supabase project is running (check supabase.com)
2. Test credentials:
   ```bash
   python scripts/health_check.py
   ```
3. Check firewall isn't blocking connection
4. Verify API key is the `anon public` key (not service role)

### "Permission denied for table"

**Cause**: RLS (Row Level Security) blocking access

**Fix**:
1. In Supabase SQL Editor, run:
   ```sql
   -- Check RLS policies
   SELECT tablename, policyname FROM pg_policies 
   WHERE schemaname = 'public';
   ```
2. Our schema includes permissive policies
3. If still blocked, temporarily disable RLS (development only):
   ```sql
   ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
   ALTER TABLE meal_history DISABLE ROW LEVEL SECURITY;
   ```

### Schema already exists error

**Cause**: Tables already created

**Fix**: Drop and recreate (WARNING: deletes data):
```sql
-- Drop all tables
DROP TABLE IF EXISTS system_metrics CASCADE;
DROP TABLE IF EXISTS error_logs CASCADE;
DROP TABLE IF EXISTS api_usage CASCADE;
DROP TABLE IF EXISTS meal_history CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- Then run schema.sql again
```

---

## 💰 Cost & Limits

### Supabase Free Tier

- **Database**: 500MB storage
- **Bandwidth**: 2GB/month
- **Users**: 50,000 monthly active users
- **API Requests**: Unlimited
- **Duration**: Unlimited (no time limit)

### When to Upgrade

**Upgrade to Pro ($25/month) when**:
- Database > 500MB (unlikely for this app)
- Need more than 2GB bandwidth/month
- Want automatic backups retained longer
- Need point-in-time recovery

**Typical Usage** (100 users):
- Profiles: ~10KB each = 1MB for 100 users
- Meals: ~1KB each = 10MB for 10,000 meals
- Logs: ~2KB each = 2MB for 1,000 errors
- **Total**: ~15MB << 500MB limit ✅

---

## 📊 Monitoring Your Database

### In Supabase Dashboard

1. **Database Size**:
   - Settings → Database
   - See storage usage

2. **API Usage**:
   - Settings → API
   - See request counts

3. **Query Performance**:
   - Reports → Database
   - See slow queries

### In Your App

1. **System Health** (sidebar):
   - Shows database connection status

2. **Table Editor**:
   - Browse all data directly

3. **SQL Editor**:
   - Run custom queries:
     ```sql
     -- See all profiles
     SELECT * FROM user_profiles;
     
     -- Count meals
     SELECT COUNT(*) FROM meal_history;
     
     -- Check costs
     SELECT DATE(timestamp), SUM(estimated_cost) 
     FROM api_usage 
     GROUP BY DATE(timestamp);
     ```

---

## 🎓 Advanced Features

### Views Available

```sql
-- Daily usage summary
SELECT * FROM daily_usage_summary;

-- Profile activity
SELECT * FROM profile_activity_summary;

-- Error rates
SELECT * FROM error_rate_summary;

-- Cost monitoring
SELECT * FROM cost_monitoring;
```

### Backup Data

**Export profiles**:
```sql
COPY (SELECT * FROM user_profiles) 
TO '/path/to/backup.csv' 
WITH CSV HEADER;
```

**Or use Supabase dashboard**:
- Table Editor → Select table → Export

---

## ✅ Setup Checklist

- [ ] Created Supabase project
- [ ] Ran `schema.sql` in SQL Editor
- [ ] Verified 5 tables created
- [ ] Copied Project URL
- [ ] Copied `anon public` API key
- [ ] Added to `.env` (local) or Streamlit secrets (production)
- [ ] Restarted app
- [ ] Health check shows "Database: Healthy"
- [ ] Created test profile
- [ ] Verified profile appears in Supabase Table Editor

---

## 🆘 Need Help?

1. **Check health status**: `python scripts/health_check.py`
2. **View logs**: Check Streamlit terminal for errors
3. **Test connection**: Use Supabase dashboard SQL Editor
4. **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)

---

**Your database will be fully functional once setup is complete! The app works perfectly fine with JSON fallback until then.**

