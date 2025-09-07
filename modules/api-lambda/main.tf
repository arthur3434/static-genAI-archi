# Lambda function for interview role processing
resource "aws_lambda_function" "interview_processor" {
  filename         = "lambda_function.zip"
  function_name    = "${var.project_name}-interview-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.11"
  timeout         = 360

  environment {
    variables = {
      BEDROCK_MODEL_ID = var.bedrock_model_id

    }
  }

  tags = {
    Project = var.project_name
  }
}

# Create the Lambda deployment package
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "lambda_function.zip"
  source {
    content = templatefile("${path.module}/lambda_function.py", {
      bedrock_model_id = var.bedrock_model_id,
      aws_region      = var.aws_region
    })
    filename = "index.py"
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# IAM policy for Lambda to access Bedrock
resource "aws_iam_policy" "lambda_bedrock_policy" {
  name        = "${var.project_name}-lambda-bedrock-policy"
  description = "Policy for Lambda to access Bedrock"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"

      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

# Attach policies to Lambda role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_bedrock_access" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_bedrock_policy.arn
}

# API Gateway
resource "aws_api_gateway_rest_api" "interview_api" {
  name        = "${var.project_name}-api"
  description = "API for interview role processing"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Project = var.project_name
  }
}

# API Gateway resource
resource "aws_api_gateway_resource" "interview_resource" {
  rest_api_id = aws_api_gateway_rest_api.interview_api.id
  parent_id   = aws_api_gateway_rest_api.interview_api.root_resource_id
  path_part   = "interview"
}

# API Gateway method
resource "aws_api_gateway_method" "interview_method" {
  rest_api_id   = aws_api_gateway_rest_api.interview_api.id
  resource_id   = aws_api_gateway_resource.interview_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway integration
resource "aws_api_gateway_integration" "interview_integration" {
  rest_api_id = aws_api_gateway_rest_api.interview_api.id
  resource_id = aws_api_gateway_resource.interview_resource.id
  http_method = aws_api_gateway_method.interview_method.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.interview_processor.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.interview_processor.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.interview_api.execution_arn}/*/*"
}

# CORS configuration
resource "aws_api_gateway_method" "interview_options" {
  rest_api_id   = aws_api_gateway_rest_api.interview_api.id
  resource_id   = aws_api_gateway_resource.interview_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "interview_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.interview_api.id
  resource_id = aws_api_gateway_resource.interview_resource.id
  http_method = aws_api_gateway_method.interview_options.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_stage" "interview_stage" {
  rest_api_id = aws_api_gateway_rest_api.interview_api.id
  deployment_id = aws_api_gateway_deployment.interview_deployment.id
  stage_name = "prod"
}

resource "aws_api_gateway_method_response" "interview_options_response" {
  rest_api_id = aws_api_gateway_rest_api.interview_api.id
  resource_id = aws_api_gateway_resource.interview_resource.id
  http_method = aws_api_gateway_method.interview_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "interview_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.interview_api.id
  resource_id = aws_api_gateway_resource.interview_resource.id
  http_method = aws_api_gateway_method.interview_options.http_method
  status_code = aws_api_gateway_method_response.interview_options_response.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "interview_deployment" {
  depends_on = [
    aws_api_gateway_integration.interview_integration,
    aws_api_gateway_integration.interview_options_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.interview_api.id

  lifecycle {
    create_before_destroy = true
  }
}
