variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Name prefix for all resources"
  type        = string
  default     = "stock-ai"
}

variable "image_tag" {
  description = "Image tag to deploy from ECR (push images with this tag first)"
  type        = string
  default     = "latest"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "stockai"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "stockai"
}

variable "ai_provider" {
  description = "auto | claude | openai"
  type        = string
  default     = "auto"
}

# AI keys are optional (the app falls back to mock analysis). Prefer setting these
# AFTER apply via the AWS console / CLI rather than committing them to tfvars.
variable "openai_api_key" {
  description = "OpenAI API key (stored in Secrets Manager)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key (stored in Secrets Manager)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "desired_count" {
  description = "Number of tasks per service"
  type        = number
  default     = 1
}

variable "backend_cpu" {
  type    = number
  default = 256
}

variable "backend_memory" {
  type    = number
  default = 512
}

variable "frontend_cpu" {
  type    = number
  default = 256
}

variable "frontend_memory" {
  type    = number
  default = 512
}
