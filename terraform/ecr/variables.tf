variable "aws_region" {
  description = "ECR repository region" 
  type        = string
  default     = "eu-central-1"
}

variable "repository_name" {
  description = "ECR repository"
  type        = string
  default     = "fastapi-cicd-pipeline"
}