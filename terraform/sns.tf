resource "aws_sns_topic" "autoec2" {
  name = "autoec2-status"
}

resource "aws_sns_topic_subscription" "autoec2" {
  topic_arn = aws_sns_topic.autoec2.arn
  protocol  = "email"
  endpoint  = var.sns_email # ToDo: Lambda function
}