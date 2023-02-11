resource "aws_instance" "autoec2-server" {
  ami           = var.ec2_ami_id
  instance_type = var.ec2_instance_type
  associate_public_ip_address = true
  tags = {
    Name = "satisfactory-server"
  }
  lifecycle {
    ignore_changes = [associate_public_ip_address]
  }
  vpc_security_group_ids  = [aws_security_group.autoec2.id]
}

resource "aws_security_group" "autoec2" {
  name        = "allow_autoec2"
  description = "Allow autoec2 server traffic"
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "autoec2_ingress_udp1" {
  type              = "ingress"
  from_port         = 15777
  to_port           = 15777
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.autoec2.id
}

resource "aws_security_group_rule" "autoec2_ingress_udp2" {
  type              = "ingress"
  from_port         = 7777
  to_port           = 7777
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.autoec2.id
}

resource "aws_security_group_rule" "autoec2_ingress_udp3" {
  type              = "ingress"
  from_port         = 15000
  to_port           = 15000
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.autoec2.id
}

resource "aws_security_group_rule" "autoec2_ingress_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.ec2_management_source_ip]
  security_group_id = aws_security_group.autoec2.id
}

resource "aws_security_group_rule" "autoec2_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]
  security_group_id = aws_security_group.autoec2.id
}


