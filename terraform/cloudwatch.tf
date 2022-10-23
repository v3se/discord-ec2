resource "aws_cloudwatch_metric_alarm" "autoec2-inactivity" {
  alarm_name          = "autoec2-inactivity"
  alarm_description   = "Stop autoec2 after 30 minutes of inactivity"
  comparison_operator = "LessThanThreshold"
  datapoints_to_alarm = "3"
  evaluation_periods  = "3"
  metric_name         = "NetworkIn"
  period              = "600"
  statistic           = "Average"
  namespace           = "AWS/EC2"
  threshold           = "50000"
  alarm_actions = [
    aws_sns_topic.autoec2.arn,
    "arn:aws:swf:${var.aws_region}:${data.aws_caller_identity.aws-info.account_id}:action/actions/AWS_EC2.InstanceId.Stop/1.0",
  ]
  dimensions = { "InstanceId" = aws_instance.autoec2-server.id }
}