# Architecture Overview  Ask the AI

The project provides a generic serverless architecture to deploy a static website that interacts with a large language model (LLM) using Amazon Bedrock.

This architecture is ideal for creating a variety of applications, such as a content generator, a chatbot, or a question-and-answer tool. It's designed to be easily replicated and adapted for different business needs.

## Key Components of the Architecture

### **Frontend (S3 + CloudFront)**
- **Technology**: React/TypeScript with Tailwind CSS
- **Hosting**: Amazon S3 static website hosting
- **CDN**: CloudFront distribution with 15+ edge locations
- **Security**: OAC authentication
- **Performance**: Browser caching & compression out of the box
- **Cost**: Pay-per-request, no server maintenance

### **API Gateway**
- **Type**: REST API with HTTPS endpoints
- **Authentication**: API Key required (`x-api-key` header)
- **Rate Limiting**: 1000 requests/day per API key
- **Throttling**: 50 requests/second, 100 burst limit
- **CORS**: Restricted to CloudFront domain only
- **Monitoring**: CloudWatch integration, request/response logging

### **Lambda Function**
- **Runtime**: Python 3.11
- **Memory**: 128 MB (configurable)
- **Timeout**: 15 seconds (security optimized)
- **Input Validation**: Length (10-10000 chars), pattern filtering
- **Error Handling**: Generic error messages, structured logging
- **IAM Role**: Bedrock access with least privilege principle

### **Amazon Bedrock**
- **Model**: `amazon.titan-text-express-v1` (default)
- **Context**: 8K tokens maximum
- **Cost**: $0.0008 per 1K input tokens, $0.0016 per 1K output tokens
- **Region**: eu-west-3 (Paris)
- **Access**: IAM-based authentication
- **Fallback**: `amazon.titan-text-lite-v1` for cost optimization

### **Monitoring & Security**
- **CloudWatch Dashboard**: Real-time metrics visualization
- **SNS Alerts**: Email notifications for errors and anomalies
- **Log Retention**: 14 days (configurable)

##² Architecture 

```
+--------------------+
|   USER (Browser)   |
+---------+----------+
          |
   (1) HTTPS Request
          |
+---------v----------+
|   CloudFront CDN   |
| +---------------+  |
| |    AWS WAF    |  |
| +---------------+  |
+---------+----------+
     |          |
     |          +----------------------+
     |                                 |
     | (2a) Static Content             | (2b) API Requests
     |                                 |
+----v----+                      +-----v------+
|  Amazon |                      |   Amazon   |
|   S3    |                      | API Gateway|
| (Static |                      | (Endpoint) |
| Website)|                      +-----+------+
+---------+                            |
                                       |
                                (3) Lambda Trigger
                                       |
                                 +-----v------+
                                 |   AWS       |
                                 |   Lambda    |
                                 +-----+------+
                                       |
                          +------------+-------------+
                          |                          |
                    (4) Logs/Metrics           (5) AI Generation
                          |                          |
                   +------v------+          +--------v--------+
                   | Amazon      |          |  Amazon Bedrock |
                   | CloudWatch  |          |  (Generative AI)|
                   +-------------+          +-----------------+

```

## To do

- PROBLEM timeout -> SQS event

- Configure WAF rules for CloudFront

- Add VPC + Security Groups for network isolation

- Set up SSL certificates for production

- Encrypt and rotate keys with KMS

- Fine-tune API security beyond simple key auth