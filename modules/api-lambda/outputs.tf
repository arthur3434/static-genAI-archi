output "api_gateway_url" {
  description = "URL of the API Gateway"
  value = "https://${aws_api_gateway_rest_api.interview_api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.interview_stage.stage_name}/interview"
}

output "api_gateway_domain_name" {
  description = "Domain name of the API Gateway"
  value = "https://${aws_api_gateway_rest_api.interview_api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.interview_stage.stage_name}"
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.interview_processor.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.interview_processor.arn
}

output "api_gateway_name" {
  description = "Name of the API Gateway"
  value       = aws_api_gateway_rest_api.interview_api.name
}

output "api_key" {
  description = "API Key for the API Gateway"
  value       = aws_api_gateway_api_key.api_key.value
  sensitive   = true
}