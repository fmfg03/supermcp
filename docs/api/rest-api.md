# SuperMCP REST API Documentation

**Version:** 2.0.0  
**Base URL:** `https://api.supermcp.com/v1`  
**Authentication:** Bearer Token  

---

## 🔐 **Authentication**

### **API Key Authentication**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.supermcp.com/v1/health
```

### **JWT Token Authentication**
```bash
# Get JWT token
curl -X POST https://api.supermcp.com/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'

# Use JWT token
curl -H "Authorization: Bearer JWT_TOKEN" \
     https://api.supermcp.com/v1/orchestration/status
```

---

## 📊 **Core Endpoints**

### **Health & Status**

#### `GET /health`
System health check

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-30T21:00:00Z",
  "version": "2.0.0",
  "services": {
    "orchestration": "healthy",
    "memory_analyzer": "healthy",
    "agentius": "healthy",
    "database": "healthy"
  }
}
```

#### `GET /status`
Detailed system status

**Response:**
```json
{
  "system": {
    "uptime": "72h 15m 30s",
    "cpu_usage": 45.2,
    "memory_usage": 68.7,
    "active_tasks": 23,
    "queue_size": 5
  },
  "services": [
    {
      "name": "orchestration",
      "status": "healthy",
      "response_time": "12ms",
      "last_check": "2025-06-30T21:00:00Z"
    }
  ]
}
```

---

## 🎭 **Orchestration API**

### **Task Management**

#### `POST /orchestration/execute`
Execute a task through the orchestration service

**Request:**
```json
{
  "action": "proposal_evaluation",
  "parameters": {
    "client": "TechCorp",
    "context": "Digital transformation project",
    "objectives": ["reduce_costs", "improve_efficiency"],
    "constraints": ["6_month_timeline"],
    "tone": "professional"
  },
  "priority": "high",
  "timeout": 300
}
```

**Response:**
```json
{
  "task_id": "task_20250630_210000_abc123",
  "status": "accepted",
  "estimated_duration": "120s",
  "callback_url": "/orchestration/tasks/task_20250630_210000_abc123",
  "websocket_url": "ws://api.supermcp.com/ws/tasks/task_20250630_210000_abc123"
}
```

#### `GET /orchestration/tasks/{task_id}`
Get task status and results

**Response:**
```json
{
  "task_id": "task_20250630_210000_abc123",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-06-30T21:00:00Z",
  "completed_at": "2025-06-30T21:02:15Z",
  "result": {
    "proposal": "Based on your requirements...",
    "score": 8.7,
    "justification": "This proposal addresses...",
    "iterations": 3
  },
  "metadata": {
    "agent_interactions": 12,
    "processing_time": "135s",
    "model_used": "gpt-4"
  }
}
```

#### `DELETE /orchestration/tasks/{task_id}`
Cancel a running task

**Response:**
```json
{
  "task_id": "task_20250630_210000_abc123",
  "status": "cancelled",
  "cancelled_at": "2025-06-30T21:01:30Z"
}
```

---

## 🤖 **Agentius API**

### **Proposal Evaluation**

#### `POST /agentius/evaluate`
Start a new proposal evaluation

**Request:**
```json
{
  "client": "TechCorp",
  "context": "We need to modernize our legacy CRM system",
  "objectives": [
    "Reduce operational costs by 30%",
    "Improve user experience",
    "Increase system reliability"
  ],
  "constraints": [
    "Must complete within 6 months",
    "Budget limit of $500K",
    "Minimal disruption to current operations"
  ],
  "tone": "professional",
  "judge_archetypes": ["technical_founder", "conservative_cfo"],
  "enable_parallel_variants": true,
  "max_iterations": 5,
  "min_score": 8.0
}
```

**Response:**
```json
{
  "evaluation_id": "eval_20250630_210000_techcorp",
  "status": "started",
  "status_url": "/agentius/evaluations/eval_20250630_210000_techcorp",
  "stream_url": "ws://api.supermcp.com/ws/agentius/eval_20250630_210000_techcorp",
  "estimated_duration": "2-5 minutes"
}
```

#### `GET /agentius/evaluations/{evaluation_id}`
Get evaluation status

**Response:**
```json
{
  "evaluation_id": "eval_20250630_210000_techcorp",
  "status": "running",
  "client": "TechCorp",
  "progress": {
    "current": 65,
    "total": 100,
    "stage": "judge_evaluation"
  },
  "started_at": "2025-06-30T21:00:00Z",
  "current_stage": "Judge panel evaluating proposal",
  "stages_completed": [
    "context_analysis",
    "proposal_generation"
  ],
  "stages_remaining": [
    "refinement",
    "final_validation"
  ]
}
```

#### `GET /agentius/evaluations/{evaluation_id}/result`
Get completed evaluation result

**Response:**
```json
{
  "evaluation_id": "eval_20250630_210000_techcorp",
  "client": "TechCorp",
  "status": "completed",
  "final_score": 8.7,
  "iterations": 3,
  "final_proposal": "# CRM Modernization Proposal\n\n## Executive Summary\n...",
  "justification": "This proposal successfully addresses all key objectives...",
  "metadata": {
    "total_processing_time": "187s",
    "judge_evaluations": 4,
    "refinement_cycles": 2,
    "confidence_score": 0.89
  },
  "decision_trace_url": "/agentius/evaluations/eval_20250630_210000_techcorp/trace",
  "download_urls": {
    "proposal": "/agentius/evaluations/eval_20250630_210000_techcorp/download/proposal",
    "justification": "/agentius/evaluations/eval_20250630_210000_techcorp/download/justification",
    "full_report": "/agentius/evaluations/eval_20250630_210000_techcorp/download/report"
  }
}
```

### **Judge Management**

#### `GET /agentius/judges/archetypes`
Get available judge archetypes

**Response:**
```json
{
  "archetypes": [
    "technical_founder",
    "conservative_cfo", 
    "growth_cmo",
    "bureaucratic_executive"
  ],
  "descriptions": {
    "technical_founder": {
      "name": "Technical Founder",
      "description": "Engineering leadership focused on technical excellence",
      "key_concerns": ["technical_debt", "scalability", "vendor_lock"],
      "typical_score_range": [6.2, 8.9]
    },
    "conservative_cfo": {
      "name": "Conservative CFO", 
      "description": "Financial leadership focused on risk management",
      "key_concerns": ["budget_overrun", "roi_uncertainty", "compliance"],
      "typical_score_range": [5.8, 8.1]
    }
  }
}
```

#### `POST /agentius/judges/evaluate`
Direct judge evaluation (for testing)

**Request:**
```json
{
  "proposal": "Our proposal is to implement a new CRM system...",
  "archetype": "technical_founder",
  "context": {
    "client": "TechCorp",
    "industry": "technology",
    "company_size": "mid_market"
  },
  "iteration": 1
}
```

**Response:**
```json
{
  "archetype": "technical_founder",
  "score": 7.2,
  "confidence": 0.85,
  "evaluation": {
    "strengths": [
      "Clear technical architecture approach",
      "Addresses scalability concerns"
    ],
    "concerns": [
      "Dependency on external vendor",
      "Migration complexity not fully addressed"
    ],
    "objections": [
      "What happens when the vendor relationship ends?",
      "How do we maintain this when consultants leave?"
    ],
    "suggestions": [
      "Include knowledge transfer requirements",
      "Propose hybrid internal/external team structure"
    ]
  },
  "fear_analysis": {
    "triggered_fears": ["vendor_dependency", "knowledge_transfer"],
    "intensity_scores": {
      "vendor_dependency": 0.8,
      "knowledge_transfer": 0.6
    }
  }
}
```

### **Training & Learning**

#### `GET /agentius/training/status`
Get auto-retraining system status

**Response:**
```json
{
  "training_active": true,
  "auto_retraining_enabled": true,
  "last_training_run": "2025-06-30T18:00:00Z",
  "next_scheduled_training": "2025-07-01T18:00:00Z",
  "training_triggers": {
    "accuracy_threshold": 0.05,
    "new_examples_count": 100,
    "time_interval": "7_days"
  },
  "metrics": {
    "total_training_examples": 1847,
    "model_accuracy": 0.946,
    "improvement_rate": 0.032,
    "examples_since_last_training": 25,
    "auto_retraining_count": 15
  },
  "archetype_performance": {
    "technical_founder": {
      "accuracy": 0.951,
      "training_examples": 542,
      "last_improved": "2025-06-29T14:30:00Z",
      "auto_improvements": 8
    },
    "conservative_cfo": {
      "accuracy": 0.923, 
      "training_examples": 398,
      "last_improved": "2025-06-30T09:15:00Z",
      "auto_improvements": 6
    }
  },
  "shadow_mode_stats": {
    "observations": 1543,
    "accuracy": 0.94,
    "learning_contributions": 789
  }
}
```

#### `POST /agentius/training/trigger`
Manually trigger training pipeline

**Request:**
```json
{
  "force_retrain": false,
  "specific_archetypes": ["technical_founder"],
  "training_parameters": {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 10
  }
}
```

**Response:**
```json
{
  "training_job_id": "train_20250630_210000",
  "status": "started",
  "estimated_duration": "45-60 minutes",
  "archetypes_included": ["technical_founder"],
  "training_examples": 342,
  "status_url": "/agentius/training/jobs/train_20250630_210000"
}
```

### **Shadow Mode**

#### `POST /agentius/shadow/observe`
Record a shadow observation

**Request:**
```json
{
  "proposal_text": "We propose implementing a new customer service platform...",
  "context": {
    "client": "ServiceCorp",
    "industry": "customer_service",
    "proposal_source": "email"
  },
  "source": "email",
  "metadata": {
    "sender": "client.lead@servicecorp.com",
    "received_at": "2025-06-30T20:45:00Z"
  }
}
```

**Response:**
```json
{
  "observation_id": "shadow_20250630_210000_servicecorp",
  "status": "observed",
  "agentius_prediction": {
    "recommendation": "approve", 
    "confidence": 0.76,
    "predicted_score": 7.4,
    "key_concerns": ["budget_uncertainty", "timeline_aggressive"]
  },
  "outcome_recording_url": "/agentius/shadow/observations/shadow_20250630_210000_servicecorp/outcome"
}
```

#### `POST /agentius/shadow/observations/{observation_id}/outcome`
Record actual human outcome

**Request:**
```json
{
  "human_outcome": "approved",
  "human_feedback": "Great proposal, but we negotiated on timeline",
  "final_terms": {
    "budget_approved": 450000,
    "timeline_extended": "8_months"
  }
}
```

**Response:**
```json
{
  "observation_id": "shadow_20250630_210000_servicecorp",
  "outcome_recorded": true,
  "accuracy_score": 0.85,
  "learning_value": "high",
  "added_to_training_queue": true
}
```

### **Buyer Simulator API**

#### `POST /agentius/buyer-simulator/simulate`
Run buyer simulation against a proposal

**Request:**
```json
{
  "proposal": "We propose implementing a new CRM system...",
  "buyer_personality": "ruthless_procurement",
  "negotiation_rounds": 5,
  "context": {
    "client": "TechCorp",
    "industry": "technology",
    "budget_range": [400000, 600000]
  },
  "enable_dirty_tactics": true
}
```

**Response:**
```json
{
  "simulation_id": "sim_20250630_210000_techcorp",
  "buyer_personality": "ruthless_procurement",
  "negotiation_outcome": {
    "final_deal_probability": 0.73,
    "negotiation_rounds": 4,
    "final_terms": {
      "price_reduction": 0.15,
      "timeline_extension": "2_months",
      "additional_deliverables": ["training", "support"]
    }
  },
  "tactics_used": [
    "budget_pressure",
    "competitor_comparison",
    "timeline_urgency"
  ],
  "objections_raised": [
    "Price is 20% above our budget",
    "Timeline seems aggressive",
    "What about ongoing support costs?"
  ],
  "proposal_weaknesses": [
    "Insufficient cost justification",
    "Limited risk mitigation details"
  ],
  "recommendations": [
    "Add detailed ROI analysis",
    "Include comprehensive risk assessment"
  ]
}
```

#### `GET /agentius/buyer-simulator/personalities`
Get available buyer personalities

**Response:**
```json
{
  "personalities": [
    {
      "id": "ruthless_procurement",
      "name": "Ruthless Procurement",
      "description": "Aggressive cost-focused buyer with extensive negotiation experience",
      "key_tactics": ["budget_pressure", "competitor_comparison", "timeline_manipulation"],
      "success_rate": 0.82,
      "avg_price_reduction": 0.18
    },
    {
      "id": "paranoid_cto",
      "name": "Paranoid CTO",
      "description": "Security and risk-focused technical decision maker",
      "key_tactics": ["security_concerns", "vendor_dependency", "technical_scrutiny"],  
      "success_rate": 0.69,
      "avg_timeline_extension": "3_months"
    }
  ]
}
```

### **Auto-Brief Extraction API**

#### `POST /agentius/auto-brief/extract`
Extract brief from various document formats

**Request:**
```json
{
  "source_type": "pdf",
  "source_url": "https://client.com/project-brief.pdf",
  "extraction_options": {
    "include_context": true,
    "auto_generate_objectives": true,
    "identify_stakeholders": true,
    "extract_constraints": true
  },
  "client_metadata": {
    "client_name": "TechCorp",
    "industry": "technology"
  }
}
```

**Response:**
```json
{
  "extraction_id": "extract_20250630_210000_techcorp",
  "status": "completed",
  "extracted_brief": {
    "client": "TechCorp",
    "project_title": "CRM System Modernization",
    "context": "Legacy CRM system requires modernization to support growing sales team",
    "objectives": [
      "Reduce operational costs by 30%",
      "Improve user experience and adoption",
      "Increase system reliability and uptime"
    ],
    "constraints": [
      "6-month implementation timeline",
      "$500K budget limit",
      "Minimal disruption to current operations"
    ],
    "stakeholders": [
      {
        "role": "CTO", 
        "concerns": ["technical_architecture", "security"],
        "influence": "high"
      },
      {
        "role": "Sales Director",
        "concerns": ["user_experience", "training"],
        "influence": "medium"
      }
    ],
    "success_metrics": [
      "30% cost reduction within 12 months",
      "90% user adoption rate",
      "99.5% system uptime"
    ]
  },
  "confidence_scores": {
    "overall": 0.89,
    "objectives": 0.92,
    "constraints": 0.85,
    "stakeholders": 0.78
  },
  "auto_evaluate_proposal": {
    "ready": true,
    "estimated_duration": "3_minutes"
  }
}
```

#### `POST /agentius/auto-brief/extract-voice`
Extract brief from voice recordings

**Request:**
```json
{
  "audio_file_url": "https://storage.com/client-meeting.mp3",
  "transcription_options": {
    "speaker_identification": true,
    "language": "en-US",
    "include_timestamps": true
  },
  "context_hints": {
    "meeting_type": "project_kickoff",
    "participants": ["client_stakeholder", "sales_rep"]
  }
}
```

**Response:**
```json
{
  "extraction_id": "voice_extract_20250630_210000",
  "transcription": {
    "text": "We need to modernize our CRM system...",
    "speakers": [
      {
        "speaker_id": "speaker_1",
        "role": "client_stakeholder",
        "segments": ["We need to modernize...", "Budget is around 500K..."]
      }
    ],
    "duration": "15_minutes"
  },
  "extracted_brief": {
    "client": "Extracted from conversation",
    "project_context": "CRM modernization discussed in stakeholder meeting",
    "key_requirements": [
      "Legacy system replacement",
      "User experience improvement",
      "Cost optimization"
    ],
    "budget_mentioned": "$500K",
    "timeline_mentioned": "6_months"
  }
}
```

### **Vertical Deployment API**

#### `POST /agentius/verticals/deploy`
Deploy industry-specific Agentius instance

**Request:**
```json
{
  "vertical": "healthcare",
  "client_id": "hospital-abc",
  "environment": "production",
  "compliance_requirements": ["HIPAA", "Joint_Commission"],
  "customizations": {
    "fear_code_adjustments": {
      "compliance_risk": 0.95,
      "patient_safety": 0.9
    },
    "industry_terminology": true,
    "regulatory_templates": true
  }
}
```

**Response:**
```json
{
  "deployment_id": "vertical_deploy_20250630_healthcare",
  "status": "deploying",
  "vertical": "healthcare",
  "client_id": "hospital-abc",
  "estimated_completion": "15_minutes",
  "endpoints": {
    "evaluation_api": "https://healthcare.agentius.com/hospital-abc/evaluate",
    "management_dashboard": "https://healthcare.agentius.com/hospital-abc/dashboard"
  },
  "compliance_features": [
    "HIPAA_compliance_checks",
    "audit_logging",
    "data_encryption",
    "access_controls"
  ],
  "specialized_judges": [
    "healthcare_cfo",
    "chief_medical_officer", 
    "compliance_officer",
    "it_security_officer"
  ]
}
```

#### `GET /agentius/verticals/available`
List available vertical specializations

**Response:**
```json
{
  "verticals": [
    {
      "id": "healthcare",
      "name": "Healthcare",
      "description": "HIPAA-compliant healthcare industry specialization",
      "compliance_standards": ["HIPAA", "FDA_21_CFR_Part_11"],
      "specialized_judges": 4,
      "deployment_time": "15_minutes"
    },
    {
      "id": "fintech", 
      "name": "Financial Technology",
      "description": "SOX and PCI-compliant fintech specialization",
      "compliance_standards": ["SOX", "PCI_DSS", "GDPR"],
      "specialized_judges": 5,
      "deployment_time": "20_minutes"
    }
  ]
}
```

---

## 🧠 **Memory Analyzer API**

### **Context Management**

#### `POST /memory/contexts`
Create a new context

**Request:**
```json
{
  "context_id": "client_techcorp_project_alpha",
  "context_type": "project",
  "initial_data": {
    "client": "TechCorp",
    "project": "CRM Modernization",
    "stakeholders": ["CTO", "CFO", "Head of Sales"],
    "timeline": "Q3-Q4 2025"
  },
  "retention_policy": "1_year"
}
```

**Response:**
```json
{
  "context_id": "client_techcorp_project_alpha",
  "status": "created",
  "created_at": "2025-06-30T21:00:00Z",
  "storage_location": "memory://contexts/client_techcorp_project_alpha",
  "retention_expires": "2026-06-30T21:00:00Z"
}
```

#### `GET /memory/contexts/{context_id}`
Retrieve context data

**Response:**
```json
{
  "context_id": "client_techcorp_project_alpha",
  "context_type": "project",
  "created_at": "2025-06-30T21:00:00Z",
  "last_accessed": "2025-06-30T21:15:00Z",
  "access_count": 23,
  "data": {
    "client": "TechCorp",
    "project": "CRM Modernization", 
    "stakeholders": ["CTO", "CFO", "Head of Sales"],
    "timeline": "Q3-Q4 2025",
    "history": [
      {
        "timestamp": "2025-06-30T21:00:00Z",
        "event": "context_created",
        "details": "Initial project context established"
      }
    ]
  },
  "metadata": {
    "size_bytes": 2048,
    "compression_ratio": 0.65,
    "encryption_enabled": true
  }
}
```

#### `PUT /memory/contexts/{context_id}`
Update context data

**Request:**
```json
{
  "data": {
    "status": "proposal_approved",
    "approved_budget": 475000,
    "next_milestone": "technical_design_review"
  },
  "merge_strategy": "deep_merge"
}
```

**Response:**
```json
{
  "context_id": "client_techcorp_project_alpha",
  "status": "updated",
  "updated_at": "2025-06-30T21:30:00Z",
  "version": 2,
  "changes_applied": [
    "added: status",
    "added: approved_budget", 
    "added: next_milestone"
  ]
}
```

### **Memory Analytics**

#### `GET /memory/analytics/usage`
Get memory usage analytics

**Response:**
```json
{
  "total_contexts": 1247,
  "active_contexts": 89,
  "total_memory_usage": "2.4GB",
  "average_context_size": "1.9MB",
  "access_patterns": {
    "most_accessed_contexts": [
      {
        "context_id": "client_techcorp_project_alpha",
        "access_count": 156,
        "last_access": "2025-06-30T21:30:00Z"
      }
    ],
    "least_accessed_contexts": [
      {
        "context_id": "archived_project_beta",
        "access_count": 3,
        "last_access": "2025-06-15T10:30:00Z"
      }
    ]
  },
  "retention_stats": {
    "contexts_expiring_30_days": 23,
    "contexts_expired_last_month": 45,
    "average_retention_period": "8.5_months"
  }
}
```

---

## 🔌 **Webhook API**

### **Webhook Management**

#### `POST /webhooks/endpoints`
Create a new webhook endpoint

**Request:**
```json
{
  "url": "https://your-app.com/webhooks/supermcp",
  "events": [
    "task.completed",
    "evaluation.finished", 
    "training.completed"
  ],
  "secret": "your-webhook-secret",
  "active": true,
  "retry_policy": {
    "max_retries": 3,
    "retry_delay": "5s",
    "backoff_multiplier": 2
  }
}
```

**Response:**
```json
{
  "webhook_id": "webhook_20250630_210000",
  "url": "https://your-app.com/webhooks/supermcp",
  "status": "active",
  "created_at": "2025-06-30T21:00:00Z",
  "last_delivery": null,
  "delivery_stats": {
    "successful_deliveries": 0,
    "failed_deliveries": 0,
    "last_success": null,
    "last_failure": null
  }
}
```

#### `GET /webhooks/endpoints`
List webhook endpoints

**Response:**
```json
{
  "webhooks": [
    {
      "webhook_id": "webhook_20250630_210000",
      "url": "https://your-app.com/webhooks/supermcp",
      "events": ["task.completed", "evaluation.finished"],
      "status": "active",
      "created_at": "2025-06-30T21:00:00Z",
      "delivery_stats": {
        "successful_deliveries": 245,
        "failed_deliveries": 3,
        "success_rate": 98.8
      }
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

### **Webhook Events**

#### Example Event: Task Completed
```json
{
  "event": "task.completed",
  "timestamp": "2025-06-30T21:30:00Z",
  "data": {
    "task_id": "task_20250630_210000_abc123",
    "task_type": "proposal_evaluation",
    "status": "completed",
    "result": {
      "proposal": "Based on your requirements...",
      "score": 8.7,
      "iterations": 3
    },
    "metadata": {
      "processing_time": "187s",
      "client": "TechCorp"
    }
  },
  "webhook_id": "webhook_20250630_210000",
  "delivery_id": "delivery_20250630_213000_xyz789"
}
```

#### Example Event: Evaluation Finished
```json
{
  "event": "evaluation.finished",
  "timestamp": "2025-06-30T21:32:00Z", 
  "data": {
    "evaluation_id": "eval_20250630_210000_techcorp",
    "client": "TechCorp",
    "final_score": 8.7,
    "status": "completed",
    "download_urls": {
      "proposal": "/agentius/evaluations/eval_20250630_210000_techcorp/download/proposal",
      "report": "/agentius/evaluations/eval_20250630_210000_techcorp/download/report"
    }
  },
  "webhook_id": "webhook_20250630_210000",
  "delivery_id": "delivery_20250630_213200_abc456"
}
```

---

## 📊 **Analytics API**

### **System Metrics**

#### `GET /analytics/metrics`
Get system performance metrics

**Response:**
```json
{
  "timestamp": "2025-06-30T21:30:00Z",
  "time_range": "24h",
  "metrics": {
    "requests": {
      "total": 12847,
      "per_hour": 535,
      "success_rate": 99.2
    },
    "evaluations": {
      "total_completed": 156,
      "average_score": 8.4,
      "average_duration": "142s",
      "success_rate": 96.2,
      "auto_retraining_improvements": 23,
      "buyer_simulation_tests": 78,
      "shadow_mode_observations": 245
    },
    "performance": {
      "average_response_time": "245ms",
      "p50_response_time": "180ms",
      "p95_response_time": "450ms",
      "p99_response_time": "890ms"
    },
    "errors": {
      "total_errors": 23,
      "error_rate": 0.18,
      "most_common_errors": [
        {
          "error": "timeout_error",
          "count": 12,
          "percentage": 52.2
        }
      ]
    }
  }
}
```

#### `GET /analytics/usage`
Get usage analytics

**Response:**
```json
{
  "timestamp": "2025-06-30T21:30:00Z",
  "period": "30_days",
  "usage": {
    "api_calls": {
      "total": 45672,
      "by_endpoint": {
        "/agentius/evaluate": 3456,
        "/orchestration/execute": 2890,
        "/memory/contexts": 1234
      },
      "by_client": {
        "client_techcorp": 12890,
        "client_healthco": 8765,
        "client_fintech": 6543
      }
    },
    "evaluations": {
      "total": 1847,
      "by_vertical": {
        "technology": 656,
        "healthcare": 334,
        "finance": 289,
        "education": 145,
        "manufacturing": 123
      },
      "success_metrics": {
        "average_score": 8.4,
        "approval_rate": 92.1,
        "average_iterations": 2.6,
        "auto_retraining_accuracy_gain": "18%",
        "buyer_simulation_success_rate": "89%"
      },
      "advanced_features_usage": {
        "auto_brief_extractions": 567,
        "shadow_mode_observations": 1234,
        "buyer_simulations": 456,
        "vertical_deployments": 89
      }
    },
    "training": {
      "total_training_runs": 38,
      "auto_retraining_runs": 15,
      "models_improved": 24,
      "accuracy_improvement": 3.2,
      "shadow_mode_contributions": 789,
      "fine_tuning_datasets_generated": 12
    }
  }
}
```

---

## 🔧 **Admin API**

### **System Administration**

#### `POST /admin/maintenance`
Schedule system maintenance

**Request:**
```json
{
  "maintenance_type": "scheduled_restart",
  "scheduled_time": "2025-07-01T02:00:00Z",
  "duration_estimate": "15_minutes",
  "affected_services": ["orchestration", "agentius"],
  "notification_channels": ["email", "webhook"]
}
```

**Response:**
```json
{
  "maintenance_id": "maint_20250630_210000",
  "status": "scheduled", 
  "scheduled_time": "2025-07-01T02:00:00Z",
  "estimated_duration": "15_minutes",
  "notification_sent": true,
  "cancellation_deadline": "2025-07-01T01:00:00Z"
}
```

#### `GET /admin/logs`
Get system logs

**Query Parameters:**
- `level`: debug, info, warn, error, fatal
- `service`: orchestration, agentius, memory, webhook
- `start_time`: ISO 8601 timestamp
- `end_time`: ISO 8601 timestamp
- `limit`: number of log entries (max 1000)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-06-30T21:30:00Z",
      "level": "info",
      "service": "agentius",
      "message": "Evaluation completed successfully",
      "metadata": {
        "evaluation_id": "eval_20250630_210000_techcorp",
        "score": 8.7,
        "duration": "187s"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 100,
  "has_more": false
}
```

---

## 📝 **Error Handling**

### **Standard Error Response**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "objectives",
        "message": "At least one objective is required"
      }
    ],
    "request_id": "req_20250630_210000_abc123",
    "timestamp": "2025-06-30T21:00:00Z"
  }
}
```

### **Error Codes**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing authentication |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |
| `TIMEOUT_ERROR` | 504 | Request timeout |

---

## 📊 **Rate Limits**

### **Default Limits**
- **Free Tier:** 100 requests/hour
- **Pro Tier:** 1,000 requests/hour  
- **Enterprise:** 10,000 requests/hour
- **Custom:** Negotiated limits

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1625097600
X-RateLimit-Retry-After: 3600
```

---

## 🔗 **SDK Examples**

### **Python SDK**
```python
from supermcp import SuperMCPClient

client = SuperMCPClient(
    api_key="your-api-key",
    base_url="https://api.supermcp.com/v1"
)

# Simple evaluation
result = await client.agentius.evaluate(
    client="TechCorp",
    context="Digital transformation project",
    objectives=["reduce_costs", "improve_efficiency"]
)

print(f"Proposal score: {result.final_score}")
print(f"Proposal text: {result.final_proposal}")
```

### **JavaScript SDK**
```javascript
import { SuperMCPClient } from '@supermcp/sdk';

const client = new SuperMCPClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.supermcp.com/v1'
});

// Evaluate proposal
const result = await client.agentius.evaluate({
  client: 'TechCorp',
  context: 'Digital transformation project',
  objectives: ['reduce_costs', 'improve_efficiency']
});

console.log(`Proposal score: ${result.finalScore}`);
```

### **cURL Examples**
```bash
# Health check
curl https://api.supermcp.com/v1/health

# Start evaluation
curl -X POST https://api.supermcp.com/v1/agentius/evaluate \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "client": "TechCorp",
    "context": "Digital transformation project",
    "objectives": ["reduce_costs", "improve_efficiency"]
  }'

# Get evaluation result
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.supermcp.com/v1/agentius/evaluations/eval_20250630_210000_techcorp/result
```

---

**📚 For more examples and detailed integration guides, see our [SDK Documentation](./sdk.md) and [Integration Examples](../examples/).**