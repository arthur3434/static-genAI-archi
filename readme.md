# Architecture Overview – Ask the AI Interviewer

The project provides a generic serverless architecture to deploy a static website that interacts with a large language model (LLM) using Amazon Bedrock.

This architecture is ideal for creating a variety of applications, such as a content generator, a chatbot, or a question-and-answer tool. It's designed to be easily replicated and adapted for different business needs.

## Key Components of the Architecture
- Frontend: The static website, built with HTML, CSS, and JavaScript, is hosted on Amazon S3. This ensures the site is highly available and cost-effective.

- API Gateway: This service acts as the single entry point for all requests from the frontend to the backend. It exposes a secure REST API that triggers the serverless code.

- Lambda: This is the core of the application's logic. A Lambda function, written in a language like Python, takes the user's input from the API Gateway. It's responsible for making the call to the Bedrock API.

- Amazon Bedrock: This managed service provides access to a variety of foundation models (FMs) from different providers. Your Lambda function communicates with Bedrock to get the AI-generated response. The chosen model then performs the requested task, such as generating text, answering a question, or providing a summary.

## Architecture 

```
+--------------------+
|   USER (Browser)   |
+---------+----------+
          |
  (1) HTTPS Request
          |
+---------v----------+
|  Amazon CloudFront |
|        (CDN)       |
+---------+----------+
          |
   (2) HTTPS Request
          |
+---------v----------+
| Amazon API Gateway |
|   (Endpoint API)   |
+---------+----------+
          |
    (3) Lambda Trigger
          |
+---------v----------+
|    AWS Lambda      |
|  (Fonction Code)   |
+---------+----------+
   |             |
   | (4) Log/Metrics |
   |               |
+--v----------------+--v------------------+
| Amazon CloudWatch | Amazon Bedrock       |
|    (Monitoring)   |   (AI Generation)    |
+-------------------+----------------------+
```

