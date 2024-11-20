
resource "aws_cloudwatch_event_rule" "lambdaExecutionRule" {
  name = "lambdaExecutionRule"
  description = "rule that executes lambda function daily at 6pm"
  event_bus_name = "default"
  schedule_expression = "cron(0 18 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambdaTarget" {
  rule = aws_cloudwatch_event_rule.lambdaExecutionRule.name
  target_id = "lambda-target"
  arn = aws_lambda_function_url.access_secret_key_rotation
}



