data "aws_availability_zones" "available" {
  state = "available"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs            = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnets = ["10.0.0.0/24", "10.0.1.0/24"]

  # Public subnets only, no NAT gateway. This is an ephemeral demo cluster, so
  # nodes run in public subnets to avoid the hourly NAT Gateway cost. In a
  # long-lived setup nodes would sit in private subnets behind a NAT gateway.
  enable_nat_gateway      = false
  map_public_ip_on_launch = true

  public_subnet_tags = {
    "kubernetes.io/role/elb"                        = "1"
    "kubernetes.io/cluster/${var.project_name}-eks" = "shared"
  }

  tags = { Project = var.project_name }
}