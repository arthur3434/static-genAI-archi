# CloudFront Origin Access Control pour S3
resource "aws_cloudfront_origin_access_control" "s3_oac" {
  name                              = "${var.project_name}-s3-oac"
  description                       = "OAC for ${var.project_name} S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# Distribution CloudFront
resource "aws_cloudfront_distribution" "s3_distribution" {
  origin {
    domain_name = var.s3_bucket_regional_domain_name
    origin_id   = var.origin_id

    origin_access_control_id = aws_cloudfront_origin_access_control.s3_oac.id
  }

  origin {
    domain_name = var.api_gateway_domain_name
    origin_id   = var.api_origin_id

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CloudFront distribution for ${var.project_name}"
  default_root_object = "index.html"

  # Cache API
  ordered_cache_behavior {
    path_pattern            = "/api/*"
    target_origin_id        = var.api_origin_id
    allowed_methods         = ["GET","HEAD","OPTIONS","PUT","POST","PATCH","DELETE"]
    cached_methods          = ["GET","HEAD"]
    viewer_protocol_policy  = "https-only"
    min_ttl                 = 0
    default_ttl             = 0
    max_ttl                 = 0

    forwarded_values {
      query_string = true
      headers      = ["Authorization","Content-Type","x-api-key"]
      cookies { forward = "none" }
    }
  }

  # Cache  SPA / static assets
  ordered_cache_behavior {
    path_pattern            = "/assets/*"
    target_origin_id        = var.origin_id
    allowed_methods         = ["GET", "HEAD", "OPTIONS"]
    cached_methods          = ["GET", "HEAD"]
    viewer_protocol_policy  = "redirect-to-https"
    min_ttl                 = 0
    default_ttl             = 31536000
    max_ttl                 = 31536000

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }

  # Other static files (e.g., CSS, JS)
  default_cache_behavior {
    target_origin_id       = var.origin_id
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction { restriction_type = "none" }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Project = var.project_name
  }
}
