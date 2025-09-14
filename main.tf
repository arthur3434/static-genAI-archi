provider "aws" {
    # Paris 
  region = "eu-west-3"
}

# Extract clean domain name from API Gateway URL
locals {
  api_gateway_domain = regex("^https://([^/]+)", module.api_lambda.api_gateway_domain_name)[0]
}

# S3 static website module
module "static_website" {
  source = "./modules/s3-static-website"
  project_name = var.project_name
  bucket_name  = "static-website-ask-the-ai-interviewer"
  cloudfront_distribution_arn = module.cloudfront.cloudfront_distribution_arn
}

# API Gateway and Lambda module
module "api_lambda" {
  source = "./modules/api-lambda"
  project_name = var.project_name
  aws_region = var.aws_region
  bedrock_model_id = var.bedrock_model_id
}

# CloudFront module
module "cloudfront" {
  source = "./modules/cloudfront"
  project_name = var.project_name
  api_gateway_domain_name = local.api_gateway_domain
  s3_bucket_regional_domain_name = module.static_website.bucket_regional_domain_name
}

# Monitoring module
module "monitoring" {
  source = "./modules/monitoring"
  project_name = var.project_name
  lambda_function_name = module.api_lambda.lambda_function_name
  api_gateway_name = module.api_lambda.api_gateway_name
  aws_region = var.aws_region
}

# Outputs
output "website_url" {
  description = "URL of the static website (S3 direct)"
  value       = module.static_website.website_endpoint
}

output "cloudfront_url" {
  description = "URL of the CloudFront distribution (recommended)"
  value       = module.cloudfront.cloudfront_url
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = module.api_lambda.api_gateway_url
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.api_lambda.lambda_function_name
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = module.cloudfront.cloudfront_domain_name
}

output "monitoring_dashboard_url" {
  description = "CloudWatch Dashboard URL"
  value       = module.monitoring.dashboard_url
}

output "sns_topic_arn" {
  description = "SNS Topic ARN for alerts"
  value       = module.monitoring.sns_topic_arn
}

output "api_key" {
  description = "API Key for the API Gateway"
  value       = module.api_lambda.api_key
  sensitive   = true
}