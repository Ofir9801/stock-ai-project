# Secrets Manager holds everything sensitive the tasks need at runtime.
# recovery_window_in_days = 0 lets you destroy/recreate freely during development
# (production should keep the default recovery window).

# Full SQLAlchemy URL, assembled from the generated RDS password + endpoint.
resource "aws_secretsmanager_secret" "database_url" {
  name                    = "${var.project}/database-url"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = "postgresql+psycopg2://${var.db_username}:${random_password.db.result}@${aws_db_instance.main.address}:5432/${var.db_name}"
}

resource "aws_secretsmanager_secret" "openai" {
  name                    = "${var.project}/openai-api-key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "openai" {
  secret_id = aws_secretsmanager_secret.openai.id
  # Secrets Manager rejects an empty value; fall back to the app's recognized
  # placeholder so the backend cleanly drops to mock mode when no key is set.
  secret_string = var.openai_api_key != "" ? var.openai_api_key : "your_api_key_here"
}

resource "aws_secretsmanager_secret" "anthropic" {
  name                    = "${var.project}/anthropic-api-key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "anthropic" {
  secret_id     = aws_secretsmanager_secret.anthropic.id
  secret_string = var.anthropic_api_key != "" ? var.anthropic_api_key : "your_api_key_here"
}
