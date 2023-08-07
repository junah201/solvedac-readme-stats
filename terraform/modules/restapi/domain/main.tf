resource "aws_acm_certificate" "domain_cert" {
  domain_name       = var.domain_certificate_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_domain_name" "domain" {
  depends_on = [aws_acm_certificate.domain_cert]

  domain_name              = var.domain_name
  regional_certificate_arn = aws_acm_certificate.domain_cert.arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
