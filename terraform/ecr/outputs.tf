output "repository_url" {
  description = "Docker image repository URL"
  value       = aws_ecr_repository.app.repository_url
}