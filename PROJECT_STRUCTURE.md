# 📁 Project Structure

Professional, production-grade organization for the Fast Food Nutrition Agent.

---

## 🎯 Overview

```
fastfood-nutrition-agent/
├── 🚀 Production App
├── 🧠 Core Systems  
├── 🤖 Multi-Agent Architecture
├── 🔒 Security & Monitoring
├── 🧪 Testing Infrastructure
├── 📚 Documentation
└── 🗄️ Archive (Legacy v1)
```

---

## 📂 Directory Structure

### Root Level - Entry Points

```
/
├── multi_agent_app.py          # 🚀 MAIN PRODUCTION APP (Streamlit Share uses this)
├── app.py                       # 🛠️  CLI utility with startup checks
├── requirements.txt             # 📦 Production dependencies
├── requirements-dev.txt         # 🧪 Development dependencies
├── pytest.ini                   # ⚙️  Test configuration
├── .gitignore                   # 🚫 Git exclusions
├── .streamlit/                  # ⚙️  Streamlit configuration
│   ├── config.toml             # Production settings
│   └── secrets.toml.example    # Secrets template
└── README.md                    # 📖 Main documentation
```

### Core Systems (`core/`)

**Purpose**: Advanced production patterns

```
core/
├── __init__.py
├── circuit_breaker.py          # Circuit breaker pattern (prevent cascading failures)
├── retry_handler.py            # Exponential backoff retry logic
└── health_endpoint.py          # Health check UI components
```

**Features**:
- ✅ Circuit breaker prevents cascade failures
- ✅ Intelligent retry with exponential backoff
- ✅ Real-time health monitoring dashboards

### Configuration (`config/`)

**Purpose**: Environment & cost management

```
config/
├── __init__.py
├── environments.py             # Dev/Staging/Prod configs
├── database.py                 # Supabase connection management
└── cost_control.py            # Budget protection ($5/month)
```

**Features**:
- ✅ Automatic environment detection
- ✅ Database fallback (PostgreSQL → JSON)
- ✅ Hard spending limits ($0.17/day)

### Security Middleware (`middleware/`)

**Purpose**: Input validation & filtering

```
middleware/
├── __init__.py
├── security.py                 # SQL injection, XSS protection
├── content_filter.py           # OpenAI Moderation API
└── error_handler.py            # Global error handling
```

**Features**:
- ✅ SQL injection prevention
- ✅ XSS attack blocking
- ✅ Content moderation
- ✅ User-friendly error messages

### Monitoring (`monitoring/`)

**Purpose**: Observability & metrics

```
monitoring/
├── __init__.py
├── logger.py                   # Structured JSON logging
├── metrics.py                  # Performance tracking
└── health.py                   # System health checks
```

**Features**:
- ✅ JSON structured logs
- ✅ Performance metrics
- ✅ Database health monitoring
- ✅ Budget status tracking

### Multi-Agent System (`multi_agents/`)

**Purpose**: AI agent orchestration

```
multi_agents/
├── __init__.py
├── coordinator.py              # Agent orchestration
├── nutritionist_agent.py       # Dietary analysis
├── restaurant_agent.py         # Menu recommendations
└── profile_manager_agent.py    # User preference learning
```

**Features**:
- ✅ 4 specialized AI agents
- ✅ Coordinated workflow
- ✅ Context-aware recommendations

### User Memory (`memory/`)

**Purpose**: Profile & preference storage

```
memory/
├── __init__.py
└── user_profile.py            # Dual storage (PostgreSQL + JSON)
```

**Features**:
- ✅ PostgreSQL primary storage
- ✅ JSON fallback
- ✅ Meal history tracking

### Database (`supabase/`)

**Purpose**: PostgreSQL schema & migrations

```
supabase/
└── schema.sql                  # Complete database schema
```

**Includes**:
- User profiles table
- Meal history tracking
- API usage monitoring
- Error logging
- System metrics
- Automatic triggers

### Testing (`tests/`)

**Purpose**: Comprehensive test coverage

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_security.py            # 15+ security tests
├── test_database.py            # Database operations
├── test_cost_control.py        # Budget protection
├── test_content_filter.py      # Content moderation
├── test_profile_management.py  # Profile operations
└── test_environments.py        # Configuration
```

**Coverage**: 70%+ target

### Scripts (`scripts/`)

**Purpose**: Automation & utilities

```
scripts/
├── setup.sh                    # One-command local setup
├── test.sh                     # Run tests with coverage
├── deploy_check.sh             # Pre-deployment validation
├── health_check.py             # System health CLI
└── cost_report.py              # Budget usage report
```

**Usage**:
```bash
./scripts/setup.sh              # First-time setup
./scripts/test.sh               # Run test suite
./scripts/deploy_check.sh       # Pre-deploy checks
python scripts/health_check.py  # Health status
python scripts/cost_report.py   # Cost analysis
```

### Documentation (`docs/` & root)

**Purpose**: Guides & references

```
/
├── DEPLOYMENT.md               # Complete deployment guide
├── QUICK_START.md              # 5-minute setup
├── PRODUCTION_CHECKLIST.md     # Pre-launch checklist
├── DEPLOYMENT_SUMMARY.md       # Feature overview
├── PROJECT_STRUCTURE.md        # This file
└── docs/
    └── week_3/                 # Architecture docs
```

### Archive (`archive/`)

**Purpose**: Legacy version 1 files

```
archive/
├── README.md
├── app_v1.py                   # Original single-agent app
└── agent_v1.py                 # Original agent implementation
```

**Note**: Use `multi_agent_app.py` for production

### Data (`data/`)

**Purpose**: JSON fallback storage

```
data/
└── profiles/                   # User profile JSON files (fallback)
    ├── user1.json
    └── user2.json
```

**Note**: Primary storage is PostgreSQL; JSON is fallback

### Prompts (`prompts/`)

**Purpose**: AI agent system prompts

```
prompts/
├── coordinator_prompt.txt
├── nutritionist_agent_prompt.txt
├── restaurant_agent_prompt.txt
└── profile_manager_prompt.txt
```

---

## 🔄 Request Flow

```
User Request
    ↓
[app.py - Startup Checks]
    ↓
[multi_agent_app.py - Main UI]
    ↓
[middleware/security.py - Input Validation]
    ↓
[config/cost_control.py - Budget Check]
    ↓
[middleware/content_filter.py - Content Moderation]
    ↓
[core/circuit_breaker.py - Failure Protection]
    ↓
[multi_agents/coordinator.py - Agent Orchestration]
    ├→ [nutritionist_agent.py]
    ├→ [restaurant_agent.py]
    └→ [profile_manager_agent.py]
    ↓
[memory/user_profile.py - Save to Database/JSON]
    ↓
[monitoring/metrics.py - Log Performance]
    ↓
Response to User
```

---

## 🎨 Design Patterns

### 1. **Circuit Breaker Pattern**
- Location: `core/circuit_breaker.py`
- Purpose: Prevent cascading failures
- States: CLOSED → OPEN → HALF_OPEN

### 2. **Retry with Exponential Backoff**
- Location: `core/retry_handler.py`
- Purpose: Handle transient failures
- Features: Jitter, configurable delays

### 3. **Safety Wrapper**
- Location: `middleware/error_handler.py`
- Purpose: Graceful error handling
- Features: User-friendly messages, logging

### 4. **Dual Storage Pattern**
- Location: `memory/user_profile.py`
- Purpose: High availability
- Flow: PostgreSQL → JSON fallback

### 5. **Multi-Agent Coordination**
- Location: `multi_agents/coordinator.py`
- Purpose: Specialized AI agents
- Features: Orchestration, context sharing

---

## 🔒 Security Layers

```
Layer 1: Input Validation (middleware/security.py)
   ↓ SQL injection, XSS, length validation
Layer 2: Content Filtering (middleware/content_filter.py)
   ↓ OpenAI Moderation API
Layer 3: Budget Protection (config/cost_control.py)
   ↓ Rate limiting, spending caps
Layer 4: Circuit Breaker (core/circuit_breaker.py)
   ↓ Prevent cascading failures
Layer 5: Error Handling (middleware/error_handler.py)
   ↓ Graceful degradation
```

---

## 📊 Monitoring Stack

```
Application Level:
- Health checks (monitoring/health.py)
- Performance metrics (monitoring/metrics.py)
- Structured logging (monitoring/logger.py)

Database Level:
- Supabase built-in monitoring
- Custom metrics table
- Error logs table

Cost Level:
- Real-time usage tracking
- Daily/monthly budget alerts
- Per-request cost calculation
```

---

## 🚀 Deployment Files

### Streamlit Share
- **Main file**: `multi_agent_app.py`
- **Config**: `.streamlit/config.toml`
- **Secrets**: Add in Streamlit Share UI

### Required Secrets
```toml
OPENAI_API_KEY = "sk-..."
SUPABASE_URL = "https://...supabase.co"
SUPABASE_KEY = "eyJ..."
ENVIRONMENT = "production"
```

---

## 🧪 Testing Strategy

### Unit Tests
- Individual function testing
- Mock external dependencies
- Fast execution (< 1s)

### Integration Tests
- Database operations
- API interactions
- Multi-component workflows

### Security Tests
- SQL injection attempts
- XSS attempts
- Input validation
- Content filtering

### Performance Tests
- Response time benchmarks
- Load testing (future)

---

## 📈 Scaling Path

### Current (Free Tier)
- Streamlit Share: 1GB RAM
- Supabase: 500MB DB
- Cost: $5/month (OpenAI only)

### Growth Stage (100+ daily users)
- Supabase Pro: $25/month
- Increased OpenAI budget: $20-50/month
- Enable response caching

### Enterprise (1000+ daily users)
- Streamlit Teams: $250/month
- Supabase Team: $599/month
- CDN for static assets
- Redis caching layer

---

## 🛠️ Development Workflow

### Local Development
```bash
# Setup
./scripts/setup.sh

# Run app
streamlit run multi_agent_app.py

# Run tests
./scripts/test.sh

# Check health
python scripts/health_check.py
```

### Pre-Deployment
```bash
# Validate
./scripts/deploy_check.sh

# Run full test suite
pytest tests/ --cov=.

# Check cost configuration
python scripts/cost_report.py
```

### Deployment
1. Push to GitHub
2. Streamlit Share auto-deploys
3. Monitor health dashboard
4. Check cost tracking

---

## 📝 Key Files Reference

| File | Purpose | When to Edit |
|------|---------|--------------|
| `multi_agent_app.py` | Main UI | Add features |
| `config/environments.py` | Environment settings | Change limits |
| `config/cost_control.py` | Budget limits | Adjust spending |
| `middleware/security.py` | Input validation | Add validation rules |
| `supabase/schema.sql` | Database schema | Add tables/fields |
| `requirements.txt` | Dependencies | Add packages |
| `.streamlit/config.toml` | Streamlit settings | UI customization |

---

## 🎯 Quick Navigation

- **Start here**: [QUICK_START.md](QUICK_START.md)
- **Deploy**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Production checklist**: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- **Feature summary**: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

---

**This structure supports enterprise-grade operations while maintaining simplicity for development and deployment.**

