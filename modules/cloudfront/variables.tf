variable "project_name" {
  description = "Name for tagging resources"
  type        = string
}

variable "origin_id" {
  description = "Origin ID for the S3 bucket"
  type        = string
  default     = "S3-Website"
}

variable "api_origin_id" {
  description = "Origin ID for the API Gateway"
  type        = string
  default     = "API-Gateway"
}

variable "api_gateway_domain_name" {
  description = "Domain name of the API Gateway"
  type        = string
}

variable "s3_bucket_regional_domain_name" {
  type        = string
  description = "domain name bucket S3 (pour OAC)"
}