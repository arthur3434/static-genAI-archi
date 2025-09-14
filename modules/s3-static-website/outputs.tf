output "website_endpoint" {
  description = "Endpoint URL"
  value       = aws_s3_bucket_website_configuration.website.website_endpoint
}

output "bucket_id" {
  description = "bucket ID"
  value       = aws_s3_bucket.website_bucket.id
}

output "bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.website_bucket.bucket_domain_name
}

output "bucket_regional_domain_name" {
  value = aws_s3_bucket.website_bucket.bucket_regional_domain_name
}