resource "aws_key_pair" "valheim-keypair" {
  key_name   = "valheim-key"
  public_key = file("~/.ssh/valheim.pub")
}

resource "aws_eip" "valheim-eip" {
  instance = aws_instance.valheim-server.id
}

resource "aws_instance" "valheim-server" {
  ami           = var.ec2_ami_id
  key_name      = aws_key_pair.valheim-keypair.key_name
  instance_type = "c5.xlarge"
  associate_public_ip_address = true
  tags = {
    Name = "valheim-server"
  }
  lifecycle {
    ignore_changes = [associate_public_ip_address]
  }
  vpc_security_group_ids  = [aws_security_group.valheim.id]

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = file("~/.ssh/valheim")
    host        = self.public_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y",
      "sudo amazon-linux-extras install docker -y",
      "sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose",
      "sudo chmod +x /usr/local/bin/docker-compose",
      "mkdir -p $HOME/valheim-server/config $HOME/valheim-server/data",
      "cd $HOME/valheim-server/",
      "touch $HOME/valheim-server/valheim.env",
      "echo SERVER_NAME=anttila >>$HOME/valheim-server/valheim.env",
      "echo WORLD_NAME=anttila >> $HOME/valheim-server/valheim.env",
      "echo SERVER_PASS=kissa123 >> $HOME/valheim-server/valheim.env",
      "echo SERVER_PUBLIC=true >> $HOME/valheim-server/valheim.env",
      "curl -o $HOME/valheim-server/docker-compose.yaml https://raw.githubusercontent.com/lloesche/valheim-server-docker/main/docker-compose.yaml",
      "sudo usermod -a -G docker ec2-user",
    ]
  }
  provisioner "remote-exec" {
    inline = [
      "cd $HOME/valheim-server/",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "docker-compose up -d"
    ]
  }
}


resource "aws_security_group" "valheim" {
  name        = "allow_valheim"
  description = "Allow Valheim server traffic"
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "valheim_ingress_tcp" {
  type              = "ingress"
  from_port         = 2456
  to_port           = 2457
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.valheim.id
}

resource "aws_security_group_rule" "valheim_ingress_udp" {
  type              = "ingress"
  from_port         = 2456
  to_port           = 2457
  protocol          = "udp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.valheim.id
}

resource "aws_security_group_rule" "valheim_ingress_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.ec2_management_source_ip]
  security_group_id = aws_security_group.valheim.id
}

resource "aws_security_group_rule" "valheim_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]
  security_group_id = aws_security_group.valheim.id
}

resource "aws_route53_record" "valheim-dns-record" {
  zone_id = "Z101725331HY9MIDLV5DM"
  name    = "valheim.whado.net"
  type    = "A"
  ttl     = 300
  records = [aws_eip.valheim-eip.public_ip]
}