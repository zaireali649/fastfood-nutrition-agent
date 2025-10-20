# ⚡ Quick Start Guide

Get your Fast Food Nutrition Agent running in **5 minutes**.

---

## 🖥️ Local Development

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/fastfood-nutrition-agent.git
cd fastfood-nutrition-agent
```

### 2. Run Setup Script
```bash
# On macOS/Linux
chmod +x scripts/setup.sh
./scripts/setup.sh

# On Windows
# Run commands manually from setup.sh
```

### 3. Add Your OpenAI API Key
Edit `.env` file:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Run the App
```bash
streamlit run multi_agent_app.py
```

Open http://localhost:8501 in your browser!

---

## ☁️ Deploy to Production (FREE)

### Prerequisites
- GitHub account
- OpenAI API key ($5/month)
- 10 minutes

### Steps

#### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Set Up Supabase (3 minutes)
1. Go to [supabase.com](https://supabase.com) → New Project
2. SQL Editor → New Query
3. Copy & paste `supabase/schema.sql`
4. Run query
5. Copy `Project URL` and `API Key` from Settings → API

#### 3. Deploy to Streamlit Share (2 minutes)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. New app → Select your repo → `multi_agent_app.py`
3. Deploy (will fail - expected!)

#### 4. Add Secrets (2 minutes)
In Streamlit app settings → Secrets, paste:

```toml
OPENAI_API_KEY = "sk-your-key"
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJxxx..."
ENVIRONMENT = "production"
ENABLE_CONTENT_FILTER = "true"
```

Save → App auto-redeploys → **Done!** 🎉

---

## 🧪 Run Tests

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📚 Full Documentation

- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Architecture**: [docs/week_3/ARCHITECTURE.md](docs/week_3/ARCHITECTURE.md)
- **API Reference**: See code docstrings

---

## 💰 Cost Breakdown

| Service | Tier | Cost |
|---------|------|------|
| Streamlit Share | Free | $0 |
| Supabase | Free | $0 |
| OpenAI API | Pay-as-you-go | ~$5/month |
| **Total** | | **$5/month** |

Protected by built-in budget limits!

---

## 🆘 Troubleshooting

**App won't start locally?**
```bash
pip install -r requirements.txt
# Check .env has valid OPENAI_API_KEY
```

**Database not working?**
- App works without database (uses JSON fallback)
- For production, follow Supabase setup in Step 2 above

**Tests failing?**
- Normal for first setup without all credentials
- Core tests should pass

---

## ✅ Next Steps

- [ ] Test locally with your OpenAI key
- [ ] Deploy to Streamlit Share
- [ ] Set up Supabase database
- [ ] Configure production secrets
- [ ] Share your app URL!

---

**Need help?** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

