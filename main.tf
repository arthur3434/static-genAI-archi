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

# Outputs
output "website_url" {
  description = "URL of the static website"
  value       = module.static_website.website_endpoint
}