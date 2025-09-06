resource "aws_s3_bucket" "website_bucket" {
  bucket = var.bucket_name
  tags = {
    Project = var.project_name
  }
}

resource "aws_s3_bucket_website_configuration" "website" {
    bucket = aws_s3_bucket.website_bucket.id
    
    index_document {
        suffix = var.index_document
    }
    
    error_document {
        key = var.error_document
    }
  
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.website_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "s3:GetObject"
        Resource = "${aws_s3_bucket.website_bucket.arn}/*"
      }
    ]
  })
}

resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket = aws_s3_bucket.website_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
  
}