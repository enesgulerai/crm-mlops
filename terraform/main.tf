terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = "eu-central-1"
}

resource "aws_security_group" "mlops_sg" {
    name        = "mlops-architecture-sg"
    description = "Security group for MLOps FastAPI and UI"

    # SSH Access (Consider restricting 0.0.0.0/0 to your personal IP in strict production)
    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    # FastAPI Backend Port
    ingress {
        from_port   = 8000
        to_port     = 8000
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    # Streamlit UI Port
    ingress {
        from_port   = 8501
        to_port     = 8501
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    # Outbound Rules
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_key_pair" "deployer_key" {
    key_name   = "crm-mlops-deployer-key"
    public_key = file("~/.ssh/crm_mlops_key.pub")
}

data "aws_ami" "ubuntu" {
    most_recent = true
    owners      = ["099720109477"]

    filter {
        name   = "name"
        values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
    }
}

resource "aws_instance" "mlops_server" {
    ami           = data.aws_ami.ubuntu.id
    instance_type = "t3.small"

    key_name               = aws_key_pair.deployer_key.key_name
    vpc_security_group_ids = [aws_security_group.mlops_sg.id]

    user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y ca-certificates curl gnupg
              install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              chmod a+r /etc/apt/keyrings/docker.gpg
              echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              usermod -aG docker ubuntu
              EOF
    tags = {
        Name = "CRM-MLOps-Production"
    }
}

output "server_public_ip" {
    value       = aws_instance.mlops_server.public_ip
    description = "The public IP address of the newly created EC2 instance"
}

# S3 Bucket for ML Models
resource "aws_s3_bucket" "ml_models_bucket" {
    bucket = "crm-mlops-models-enesguler" 
    
    tags = {
        Name        = "ML Models Storage"
        Environment = "Production"
    }
}

# Enable Versioning
resource "aws_s3_bucket_versioning" "ml_models_versioning" {
    bucket = aws_s3_bucket.ml_models_bucket.id
    
    versioning_configuration {
        status = "Enabled"
    }
}

# DevSecOps: Explicitly block all public access to the bucket
resource "aws_s3_bucket_public_access_block" "ml_models_block_public_access" {
    bucket = aws_s3_bucket.ml_models_bucket.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

# Elastic IP
resource "aws_eip" "ml_eip" {
    instance = aws_instance.mlops_server.id
    domain   = "vpc"
}

output "elastic_ip" {
    value       = aws_eip.ml_eip.public_ip
    description = "The Elastic IP address assigned to the EC2 instance"
}