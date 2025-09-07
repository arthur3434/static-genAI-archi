variable "project_name" {
  description = "Name for tagging resources"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"
}

variable "bedrock_model_id" {
  description = "Bedrock model ID to use for interview processing"
  type        = string
  default     = "amazon.titan-text-express-v1"
}
