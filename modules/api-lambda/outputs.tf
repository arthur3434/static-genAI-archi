output "api_gateway_url" {
  value = "https://${aws_api_gateway_rest_api.interview_api.id}.execute-api.${var.aws_region}.amazonaws.com/${aws_api_gateway_stage.interview_stage.stage_name}/interview"
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.interview_processor.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = aws_lambda_function.interview_processor.arn
}
