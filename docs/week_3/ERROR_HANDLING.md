# Error Handling & Fallback Strategies

## Error Handling Architecture

```mermaid
flowchart TD
    A[Request Start] --> PM{Profile Manager Agent}
    PM -->|Success| B{Nutritionist Agent}
    PM -->|Timeout| D[Use Partial Data]
    PM -->|Error| E[Log Error]
    
    B -->|Success| C{Restaurant Agent}
    B -->|Timeout| D
    B -->|Error| E
    
    C -->|Success| F{Coordinator}
    C -->|Timeout| D
    C -->|Error| E
    
    D --> F
    E --> F
    
    F -->|Success| G[Return Response]
    F -->|Error| H{Fallback Trigger}
    
    H --> I[Single-Agent Mode]
    I --> J{Original Agent}
    J -->|Success| K[Return Fallback Response]
    J -->|Error| L[Return Error Message]
    
    style H fill:#E74C3C
    style I fill:#F39C12
    style L fill:#C0392B
```

## Fallback Hierarchy

```mermaid
graph TB
    Level1[Level 1: Multi-Agent Mode] --> Check1{All Agents OK?}
    Check1 -->|Yes| Success[✓ Full Response]
    Check1 -->|No| Level2[Level 2: Partial Mode]
    
    Level2 --> Check2{Any Agent OK?}
    Check2 -->|Yes| Partial[⚠ Partial Response]
    Check2 -->|No| Level3[Level 3: Single-Agent Fallback]
    
    Level3 --> Check3{Original Agent OK?}
    Check3 -->|Yes| Fallback[⚠ Fallback Response]
    Check3 -->|No| Level4[Level 4: Error Mode]
    
    Level4 --> Error[✗ Error Message]
    
    style Success fill:#27AE60
    style Partial fill:#F39C12
    style Fallback fill:#E67E22
    style Error fill:#C0392B
```

## Timeout Protection

Each agent has a 30-second timeout:

```mermaid
sequenceDiagram
    participant C as Coordinator
    participant A as Agent
    participant T as Timer
    
    C->>A: Start Request
    C->>T: Start 30s Timer
    
    alt Agent responds in time
        A-->>C: Response
        T-->>C: Cancel Timer
        Note over C: Use Response
    else Timeout occurs
        T-->>C: Timeout Signal
        Note over C: Use Partial Data
        C->>A: Cancel Request
    end
```

## Error Types & Handling

| Error Type | Strategy | User Impact |
|------------|----------|-------------|
| **Agent Timeout** | Use partial results or skip agent | Degraded recommendations |
| **API Error** | Retry once, then fallback | Slight delay |
| **Profile Load Error** | Continue in guest mode | No personalization |
| **Prompt File Missing** | Use hardcoded defaults | Reduced quality |
| **Network Error** | Fallback to single-agent | Simplified response |
| **All Agents Fail** | Return error message | Clear error state |

## Graceful Degradation

```mermaid
graph LR
    A[Multi-Agent<br/>Full Context] -->|Agent Fails| B[Multi-Agent<br/>Reduced Context]
    B -->|Another Fails| C[Single-Agent<br/>Fallback Mode]
    C -->|Fails| D[Error Message<br/>with Guidance]
    
    style A fill:#27AE60
    style B fill:#F39C12
    style C fill:#E67E22
    style D fill:#C0392B
```

## Session Context Tracking

The coordinator tracks errors in session context:

```python
session_context = {
    "user_goal": "...",
    "agents_used": ["Nutritionist", "Restaurant", "Coordinator"],
    "errors": [],  # Empty if all succeeded
    "fallback_triggered": False
}
```

Example with errors:

```python
session_context = {
    "user_goal": "...",
    "agents_used": ["Nutritionist"],  # Only 1 succeeded
    "errors": ["Restaurant Agent timeout"],
    "fallback_triggered": True
}
```

## Recovery Strategies

```mermaid
flowchart TD
    E[Error Detected] --> T{Error Type?}
    
    T -->|Timeout| R1[Cancel Request]
    T -->|API Error| R2[Retry Once]
    T -->|Profile Error| R3[Use Guest Mode]
    T -->|Network Error| R4[Wait & Retry]
    
    R1 --> N[Use Available Data]
    R2 --> C{Retry Success?}
    C -->|Yes| S[Continue]
    C -->|No| N
    R3 --> N
    R4 --> N
    
    N --> F{Enough Data?}
    F -->|Yes| P[Partial Response]
    F -->|No| FB[Trigger Fallback]
    
    style E fill:#E74C3C
    style FB fill:#C0392B
    style P fill:#F39C12
    style S fill:#27AE60
```

## User Communication

Errors are communicated transparently:

- **Success**: "🤝 Agents collaborated: Nutritionist → Restaurant → Coordinator"
- **Partial**: "⚠️ Restaurant Agent timeout - using nutritional guidance only"
- **Fallback**: "⚠️ Using simplified single-agent mode due to technical issues"
- **Error**: "❌ An error occurred while processing your request"

