provider "aws" {
    # Paris 
  region = "eu-west-3"
}

# S3 static website module
module "static_website" {
  source = "./modules/s3-static-website"
  project_name = var.project_name
  bucket_name  = "static-website-ask-the-ai-interviewer"
}

# API Gateway and Lambda module
module "api_lambda" {
  source = "./modules/api-lambda"
  project_name = var.project_name
  aws_region = var.aws_region
  bedrock_model_id = var.bedrock_model_id
}

# Outputs
output "website_url" {
  description = "URL of the static website"
  value       = module.static_website.website_endpoint
}

output "api_gateway_url" {
  description = "URL of the API Gateway"
  value       = module.api_lambda.api_gateway_url
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.api_lambda.lambda_function_name
}