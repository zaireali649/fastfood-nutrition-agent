# Multi-Agent System Architecture

## Overview
Sequential pipeline pattern with 4 specialized agents coordinated by a central orchestrator.

## System Architecture

```mermaid
graph TB
    User[User Request] --> Coordinator[Coordinator Agent]
    Coordinator --> ProfileMgr[Profile Manager Agent]
    Coordinator --> Nutritionist[Nutritionist Agent]
    Coordinator --> Restaurant[Restaurant Agent]
    
    ProfileMgr --> |Preference Insights| Nutritionist
    ProfileMgr --> |Preference Insights| Restaurant
    Nutritionist --> |Dietary Analysis| Coordinator
    Restaurant --> |Menu Recommendations| Coordinator
    Coordinator --> Response[Unified Response]
    
    Memory[(User Profile Memory)] --> ProfileMgr
    Memory --> Nutritionist
    Memory --> Restaurant
    Session[(Session Context)] --> Coordinator
    
    style Coordinator fill:#4A90E2
    style Nutritionist fill:#50E3C2
    style Restaurant fill:#F5A623
    style ProfileMgr fill:#9B59B6
    style Memory fill:#D0D0D0
    style Session fill:#E0E0E0
```

## Agent Roles

| Agent | Responsibility | Key Functions |
|-------|---------------|---------------|
| **Coordinator** | Orchestrates workflow, combines outputs | Route requests, handle errors, unify responses |
| **Nutritionist** | Analyzes dietary needs | Calculate macros, evaluate health impact, review history |
| **Restaurant** | Menu expertise | Recommend items, suggest customizations, optimize nutrition |
| **Profile Manager** | Learns user preferences | Analyze ratings, detect patterns, suggest updates, provide insights |

## Sequential Pipeline Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as Coordinator
    participant PM as Profile Manager
    participant N as Nutritionist
    participant R as Restaurant
    participant M as Memory
    
    U->>C: Meal Request
    C->>M: Load User Profile
    M-->>C: Profile Data
    
    alt User has 3+ meals tracked
        C->>PM: Get Profile Insights
        PM->>M: Load Full History
        M-->>PM: All Meal Data
        PM-->>C: Preference Insights
    end
    
    C->>N: Analyze Dietary Needs + Insights
    N->>M: Get Today's Meals
    M-->>N: History Data
    N-->>C: Nutritional Analysis
    
    C->>R: Get Recommendations + Insights
    R->>M: Get Preferences
    M-->>R: Preference Data
    R-->>C: Menu Options
    
    C->>C: Combine All Outputs
    C-->>U: Unified Recommendation
```

## Shared Memory Mechanisms

### 1. User Profile Memory
- **Storage**: JSON files in `data/profiles/`
- **Contents**: Preferences, meal history, statistics
- **Access**: Read by all agents, updated by Profile Manager
- **Persistence**: Disk-based, survives sessions

### 2. Session Context
- **Storage**: In-memory dictionary
- **Contents**: Agent workflow, errors, current state
- **Access**: Passed through coordinator
- **Persistence**: Request-scoped only

## File Structure

```
fastfood-nutrition-agent/
├── multi_agents/
│   ├── coordinator.py          # Main orchestrator
│   ├── nutritionist_agent.py   # Dietary analysis
│   ├── restaurant_agent.py     # Menu recommendations
│   └── profile_manager_agent.py # Preference learning
├── prompts/
│   ├── coordinator_prompt.txt
│   ├── nutritionist_agent_prompt.txt
│   ├── restaurant_agent_prompt.txt
│   └── profile_manager_prompt.txt
├── memory/
│   └── user_profile.py         # Shared memory layer
├── multi_agent_app.py          # Streamlit interface
├── demo.py                     # Demonstration script
└── profile_insights.py         # CLI insights tool
```

## Technology Stack

- **Framework**: OpenAI Agents SDK
- **LLM**: GPT-4 (via OpenAI API)
- **UI**: Streamlit
- **Storage**: JSON file-based
- **Language**: Python 3.13

