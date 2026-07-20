link - https://main.d33nxciktfjj9q.amplifyapp.com

customer- https://g0nwr1t6u4.execute-api.ap-south-1.amazonaws.com/Prod/customers

audit-https://g0nwr1t6u4.execute-api.ap-south-1.amazonaws.com/Prod/audit

security-alerts-https://g0nwr1t6u4.execute-api.ap-south-1.amazonaws.com/Prod/security-alerts

# AI Permission Proxy for Secure Tool Governance

An AI-powered permission proxy built on AWS Serverless that enforces role-based access control (RBAC) for AI agents before they interact with enterprise CRM tools.

This project demonstrates how Large Language Models (LLMs) can safely invoke business tools while ensuring that every request is authenticated, authorized, audited, and monitored.

---

## Overview

The system allows users to interact with a CRM using natural language.

Instead of directly accessing backend services, every AI-generated tool call passes through a Permission Proxy that:

- Authenticates users using JWT
- Verifies role-based permissions
- Logs all tool usage
- Detects repeated unauthorized access
- Creates security alerts
- Forwards only authorized requests to the CRM

This architecture provides a governance layer between AI agents and enterprise systems.

---

## Architecture

```
               User
                 │
                 ▼
     Frontend (HTML Dashboard)
                 │
                 ▼
          AI Agent (Gemini)
                 │
                 ▼
      Permission Proxy Lambda
                 │
     ┌───────────┴────────────┐
     ▼                        ▼
 Audit Logs             Security Alerts
 DynamoDB                 DynamoDB
     │
     ▼
 CRM Lambda
     │
     ▼
 Customers DynamoDB
```

---

## Features

### AI Agent

- Natural language understanding using Google Gemini
- Automatic tool selection
- Function calling
- Customer search
- Customer update
- Customer deletion

### Permission Proxy

- JWT Authentication
- Role-Based Access Control (RBAC)
- Permission validation
- Audit logging
- Security alert generation
- Request forwarding

### CRM

Supports:

- Get Customer
- List Customers
- Update Customer
- Delete Customer

### Dashboard

- Role switching
- JWT authentication
- Natural language input
- Permission status
- Customer data display
- AI decision visualization

---

## Technologies Used

### Cloud

- AWS Lambda
- AWS SAM
- API Gateway
- DynamoDB
- CloudWatch
- AWS Amplify

### AI

- Google Gemini 2.5 Flash
- Gemini Function Calling

### Backend

- Python 3.13
- Requests
- PyJWT

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript

---

## Project Structure

```
tool-permission-proxy/

│
├── ai_agent/
│   ├── app.py
│   └── requirements.txt
│
├── permission_proxy/
│   ├── app.py
│   ├── auth.py
│   ├── permissions.py
│   ├── audit.py
│   └── permissions.json
│
├── mock_crm/
│   ├── app.py
│   └── requirements.txt
│
├── events/
│
├── template.yaml
├── samconfig.toml
├── index.html
└── README.md
```

---

## User Roles

| Role | Permissions |
|-------|------------|
| Support Agent | View Customers |
| Sales Agent | View + Update Customers |
| Admin | View + Update + Delete Customers |

---

## Supported AI Commands

### Retrieve Customer

```
Show customer 1001
```

```
Find customer 1004
```

```
List Gold members
```

---

### Update Customer

```
Update customer 1004 city to Chennai
```

```
Change customer 1004 membership to Gold
```

---

### Delete Customer

```
Delete customer 1004
```

---

## Security Features

- JWT Authentication
- Role-Based Authorization
- AI Tool Governance
- Audit Logging
- Security Alert Generation
- Unauthorized Access Detection
- Least Privilege Access

---

## Audit Logging

Every request records:

- User
- Role
- Tool Used
- Resource
- Status
- Timestamp
- Reason

---

## Security Alerts

The system automatically generates alerts after repeated denied access attempts.

Example:

```
User:
support

Attempted Tool:
DELETE_CUSTOMER

Denied Attempts:
3

Status:
OPEN
```

---

## API Endpoints

### AI Agent

```
POST /agent
```

---

### Permission Proxy

```
GET /proxy/customers/{id}
```

```
PUT /proxy/customers/{id}
```

```
DELETE /proxy/customers/{id}
```

---

### CRM

```
GET /crm/customers
```

```
GET /crm/customers/{id}
```

```
PUT /crm/customers/{id}
```

```
DELETE /crm/customers/{id}
```

---

## Deployment

### Backend

Deploy using AWS SAM

```bash
sam build
```

```bash
sam deploy --guided
```

---

### Frontend

Hosted using AWS Amplify.

---

## Local Development

Start the local API

```bash
sam local start-api --env-vars env.json
```

The API will be available at:

```
http://127.0.0.1:3000
```

---

## Environment Variables

```
GEMINI_API_KEY
```

---

## Future Improvements

- AWS Secrets Manager integration
- Amazon Cognito authentication
- Multi-factor authentication
- Amazon EventBridge alerts
- Email/SNS notifications
- CloudWatch dashboards
- Fine-grained attribute-based access control (ABAC)
- Multi-tool orchestration
- Rate limiting
- Security analytics dashboard

---

## Learning Outcomes

This project demonstrates:

- Secure AI Tool Calling
- Serverless Application Development
- AI Governance
- Role-Based Access Control
- API Gateway Integration
- AWS Lambda Development
- DynamoDB Operations
- JWT Authentication
- Audit and Compliance Logging
- AI Security Best Practices

---

## Author

**Lakshita Senthilkumar**

Integrated M.Sc. Data Science



---
