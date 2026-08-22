variable "aws_region" {
    type    = string
    default = "eu-central-1"
}
variable "project_name" {
    type    = string
    default = "fastapi-cicd"
}
variable "cluster_version" {
    type    = string
    default = "1.30"
}
variable "vpc_cidr" {
    type    = string
    default = "10.0.0.0/16"
}
variable "node_instance_type" {
    type    = string
    default = "t3.small"
}
variable "node_desired_size" {
    type    = number
    default = 2
}