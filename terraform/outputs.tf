output "app_url" {
  description = "Open this in your browser once the frontend task is healthy"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_backend_url" {
  description = "Push the backend image here"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "Push the frontend image here"
  value       = aws_ecr_repository.frontend.repository_url
}

output "rds_endpoint" {
  description = "RDS endpoint (reachable only from the ECS tasks)"
  value       = aws_db_instance.main.address
}

output "ecs_cluster" {
  value = aws_ecs_cluster.main.name
}
