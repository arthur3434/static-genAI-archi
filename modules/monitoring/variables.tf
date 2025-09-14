variable "project_name" {
  description = "Name for tagging resources"
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the Lambda function to monitor"
  type        = string
}

variable "api_gateway_name" {
  description = "Name of the API Gateway to monitor"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}
