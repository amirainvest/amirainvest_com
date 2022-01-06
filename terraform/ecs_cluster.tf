resource "aws_ecs_cluster" "api" {
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  configuration {
    execute_command_configuration {
      logging = "DEFAULT"
    }
  }

  default_capacity_provider_strategy {
    base              = "0"
    capacity_provider = "FARGATE_SPOT"
    weight            = "1"
  }

  name = "api"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    "ecs:cluster:createdFrom" = "ecs-console-v2"
  }

  tags_all = {
    "ecs:cluster:createdFrom" = "ecs-console-v2"
  }
}
