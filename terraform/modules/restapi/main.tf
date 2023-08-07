resource "aws_api_gateway_rest_api" "rest-api" {
  name        = var.name
  description = var.description
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}


resource "aws_lambda_permission" "lambda_permission" {
  for_each      = toset(var.lambdas)
  statement_id  = "AllowMyDemoAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = each.value
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.rest-api.execution_arn}/*"
}


module "aws_api_domain" {
  source                  = "./domain"
  domain_name             = var.domain_name
  domain_certificate_name = var.domain_certificate_name
}
