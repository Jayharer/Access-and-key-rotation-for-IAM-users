
resource "aws_cloudwatch_event_rule" "lambdaExecutionRule" {
  name = "lambdaExecutionRule"
  description = "rule that executes lambda function daily at 6pm"
  event_bus_name = "default"
  schedule_expression = "cron(30 12 * * ? *)" # "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "lambdaTarget" {
  rule = aws_cloudwatch_event_rule.lambdaExecutionRule.name
  target_id = "lambda-target"
  arn = aws_lambda_function_url.access_secret_key_rotation.function_arn
}

resource "aws_cloudwatch_event_target" "targetconsoleaccess" {
  rule = aws_cloudwatch_event_rule.lambdaExecutionRule.name
  target_id = "console-access"
  arn = aws_lambda_function_url.lambda_console_access.function_arn
}


