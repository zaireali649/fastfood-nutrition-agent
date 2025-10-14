# Agent Workflow & Interactions

## Request Processing Pipeline

```mermaid
flowchart LR
    A[User Request] --> B{Coordinator}
    
    B --> PM[Profile Manager Agent]
    PM --> O[Analyze Ratings]
    PM --> P[Detect Patterns]
    PM --> Q[Generate Insights]
    O & P & Q --> R[Preference Insights]
    
    R --> B
    B --> C[Nutritionist Agent]
    C --> D[Calculate Macros]
    C --> E[Review History]
    C --> F[Analyze Restrictions]
    D & E & F --> G[Nutritional Analysis + Insights]
    
    G --> B
    B --> H[Restaurant Agent]
    H --> I[Find Menu Items]
    H --> J[Suggest Customizations]
    H --> K[Optimize Nutrition]
    I & J & K --> L[Menu Recommendations + Insights]
    
    L --> B
    B --> M[Combine All Outputs]
    M --> N[Final Response]
    
    style B fill:#4A90E2
    style PM fill:#9B59B6
    style C fill:#50E3C2
    style H fill:#F5A623
```

## Detailed Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Coordinator
    participant ProfileMgr as Profile Manager
    participant Nutritionist
    participant Restaurant
    participant Profile as User Profile
    
    User->>Coordinator: "1000 cal meal from McDonald's"
    
    Note over Coordinator: Step 0: Load Profile
    Coordinator->>Profile: Load user data
    Profile-->>Coordinator: Preferences, history, stats
    
    alt User has 3+ meals tracked
        Note over Coordinator: Step 1: Get Insights
        Coordinator->>ProfileMgr: Analyze preferences
        ProfileMgr->>Profile: Load full history
        Profile-->>ProfileMgr: All meals & ratings
        ProfileMgr->>ProfileMgr: Detect patterns
        ProfileMgr-->>Coordinator: Preference insights
    end
    
    Note over Coordinator: Step 2: Nutritional Analysis
    Coordinator->>Nutritionist: Request + Insights + Profile
    Nutritionist->>Profile: Get today's meals
    Profile-->>Nutritionist: Today's data
    Nutritionist-->>Coordinator: Analysis (macros, health notes)
    
    Note over Coordinator: Step 3: Menu Recommendations
    Coordinator->>Restaurant: Request + Analysis + Insights
    Restaurant->>Profile: Get preferences & dislikes
    Profile-->>Restaurant: Preference data
    Restaurant-->>Coordinator: 2-3 menu options
    
    Note over Coordinator: Step 4: Unification
    Coordinator->>Coordinator: Combine all outputs
    Coordinator-->>User: Unified recommendation
```

## Agent Decision Making

### Nutritionist Agent Logic

```mermaid
graph TD
    A[Receive Request] --> B{Load Profile?}
    B -->|Yes| C[Get Meal History]
    B -->|No| D[Use Defaults]
    C --> E[Calculate Daily Intake]
    D --> E
    E --> F[Set Macro Targets]
    F --> G{Restrictions?}
    G -->|Yes| H[Adjust for Restrictions]
    G -->|No| I[Standard Targets]
    H --> J[Generate Analysis]
    I --> J
    J --> K[Return Analysis]
    
    style A fill:#50E3C2
    style K fill:#50E3C2
```

### Restaurant Agent Logic

```mermaid
graph TD
    A[Receive Analysis] --> B{Parse Restaurant}
    B --> C[Access Menu Database]
    C --> D{Load Preferences?}
    D -->|Yes| E[Filter by Preferences]
    D -->|No| F[All Items]
    E --> G[Match Calorie Target]
    F --> G
    G --> H[Optimize for Macros]
    H --> I[Suggest Customizations]
    I --> J{Highly Rated Similar?}
    J -->|Yes| K[Prioritize Similar Items]
    J -->|No| L[Standard Priority]
    K --> M[Return Top 2-3 Options]
    L --> M
    
    style A fill:#F5A623
    style M fill:#F5A623
```

## Context-Aware Features

### What Each Agent Sees

```mermaid
graph TB
    Profile[(User Profile)]
    
    Profile --> N1[Nutritionist Sees:]
    Profile --> R1[Restaurant Sees:]
    Profile --> PM1[Profile Manager Sees:]
    Profile --> C1[Coordinator Sees:]
    
    N1 --> N2[• Dietary restrictions<br/>• Today's meals<br/>• Meal ratings<br/>• Average calories]
    
    R1 --> R2[• Favorite restaurants<br/>• Disliked items<br/>• Cooking preferences<br/>• Highly rated meals]
    
    PM1 --> PM2[• All meal ratings<br/>• Rating patterns<br/>• Preference trends<br/>• Restaurant frequency<br/>• Satisfaction metrics]
    
    C1 --> C2[• Total meals tracked<br/>• User journey<br/>• Agent workflow<br/>• Session state]
    
    style Profile fill:#D0D0D0
    style N2 fill:#50E3C2
    style R2 fill:#F5A623
    style PM2 fill:#9B59B6
    style C2 fill:#4A90E2
```

## Example Workflows

### Workflow 1: Meal Recommendation

**Input:** "I want a 1200 calorie meal from Chick-fil-A. I'm gluten-free."

**Nutritionist Output:**
```
- Target: 1200 cal
- Protein: 60g (high priority)
- Sodium: <800mg
- Must be gluten-free
```

**Restaurant Output:**
```
Option 1: Grilled Nuggets + Side Salad
Option 2: Grilled Chicken Sandwich (no bun)
Option 3: Market Salad + Fruit Cup
```

**Coordinator Output:**
```
Combined, personalized recommendation with:
- Nutritional rationale
- Specific menu items
- Customization tips
- Reference to user history
```

### Workflow 2: Profile Insights

**Input:** "Show my preference insights" (CLI: `python profile_insights.py username`)

**Profile Manager Output:**
```
Detected Preferences:
- Loves Chick-fil-A (5⭐ average)
- Prefers grilled over fried
- Dislikes spicy items

Recommendation Accuracy:
- Average satisfaction: 4.2/5 stars
- Most successful: Grilled options

Suggested Updates:
- Add "grilled" to cooking preferences
- Add "spicy sauces" to dislikes
- Add Chick-fil-A to favorites

Personalized Tips:
- Continue choosing grilled options
- Try similar items at other restaurants
```

