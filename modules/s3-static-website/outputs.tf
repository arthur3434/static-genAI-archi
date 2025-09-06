output "website_endpoint" {
  description = "Endpoint URL"
  value       = aws_s3_bucket_website_configuration.website.website_endpoint
}

output "bucket_id" {
  description = "bucket ID"
  value       = aws_s3_bucket.website_bucket.id
}