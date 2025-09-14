variable "bucket_name" {
  description = "Bucket S3 name for the static website."
  type        = string
}

variable "index_document" {
  description = "Index document for the static website."
  type        = string
  default     = "index.html"
}

variable "error_document" {
  description = "Error document for the static website."
  type        = string
  default     = "error.html"
}

variable "project_name" {}

variable "cloudfront_distribution_arn" {
  description = "ARN of the CloudFront distribution"
  type        = string
  default     = ""
}