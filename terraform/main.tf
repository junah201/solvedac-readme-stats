module "lambda_default_role" {
  source = "./modules/role"
  name   = "LambdaDefault"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:*:*:*"
    }
  ]
}
EOF
}

// s3
resource "aws_s3_bucket" "lambda_build_bucket" {
  bucket = var.lambda_build_bucket
}

// layer
module "util_layer" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name          = "util_layer"
  description         = "util layer"
  compatible_runtimes = ["python3.10"]

  source_path = "../layers/util_layer"

  store_on_s3 = true
  s3_bucket   = aws_s3_bucket.lambda_build_bucket.id
}

// Lambda
module "v1_generate_badge_lambda" {
  depends_on = [aws_s3_bucket.lambda_build_bucket]

  source = "terraform-aws-modules/lambda/aws"

  function_name = "v1__generate-badge"
  description   = "Generate badge for SolvedAC"
  handler       = "main.lambda_handler"
  runtime       = "python3.10"
  timeout       = 120
  source_path   = "../lambdas/v1/generate_badge"

  store_on_s3 = true
  s3_bucket   = var.lambda_build_bucket

  create_role = false
  lambda_role = module.lambda_default_role.role_arn

  layers = [
    module.util_layer.lambda_layer_arn
  ]

  tags = {
    version = "v1"
  }
}

// rest api
module "aws_api_gateway_route" {
  source = "./modules/restapi"

  name        = "solvedac-rest-api"
  description = "solvedac readme rest api"

  domain_certificate_name = "*.junah.dev"
  domain_name             = "solvedac.junah.dev"

  lambdas = [
    module.v1_generate_badge_lambda.lambda_function_name
  ]
}
