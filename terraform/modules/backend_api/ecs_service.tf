resource "aws_ecs_service" "api-public-service" {
  capacity_provider_strategy {
    base              = "0"
    capacity_provider = "FARGATE_SPOT"
    weight            = "1"
  }

  cluster = "api"

  deployment_circuit_breaker {
    enable   = "true"
    rollback = "true"
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_maximum_percent         = "200"
  deployment_minimum_healthy_percent = "100"
  desired_count                      = "2"
  enable_ecs_managed_tags            = "true"
  enable_execute_command             = "false"
  health_check_grace_period_seconds  = "0"

  load_balancer {
    container_name   = "backend_api"
    container_port   = "5000"
    target_group_arn = "arn:aws:elasticloadbalancing:${var.region}:903791206266:targetgroup/${var.environment}-api-public-service-TG/7d8e301140dfece3"
  }

  name = "${var.environment}-api-public-service"

  network_configuration {
    assign_public_ip = "false"
    security_groups  = ["sg-04c6dcf097a53b73c"]
    subnets          = var.private_subnets
  }

  platform_version    = "LATEST"
  scheduling_strategy = "REPLICA"

  tags = {
    env = var.environment
  }

  tags_all = {
    env = var.environment
  }

  task_definition = aws_ecs_task_definition.api-public-ecs-task-definition.arn
}
