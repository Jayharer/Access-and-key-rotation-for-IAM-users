resource "aws_lambda_function_url" "access_secret_key_rotation" {
    function_name = var.lambda_key_rotation
    authorization_type = "AWS_IAM"
}

resource "aws_lambda_function_url" "lambda_console_access" {
    function_name = var.lambda_console_access
    authorization_type = "AWS_IAM"
}

resource "aws_lambda_permission" "allow_event_bridge_key_rotation" {
    statement_id = "AllowExecutionFromEventBridgeKeyRotation"
    action = "lambda:InvokeFunction"
    function_name = var.lambda_key_rotation
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.lambdaExecutionRule.arn
    depends_on = [ aws_cloudwatch_event_rule.lambdaExecutionRule ]
}

resource "aws_lambda_permission" "permission_lambda_console_access" {
    statement_id = "AllowExecutionFromEventBridgeConsoleAccess"
    action = "lambda:InvokeFunction"
    function_name = var.lambda_console_access
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.lambdaExecutionRule.arn
    depends_on = [ aws_cloudwatch_event_rule.lambdaExecutionRule ]
}