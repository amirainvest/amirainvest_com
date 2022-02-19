resource "aws_ecs_cluster" "api" {
  configuration {
    execute_command_configuration {
      logging = "DEFAULT"
    }
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

resource "aws_ecs_cluster_capacity_providers" "api" {
  cluster_name       = aws_ecs_cluster.api.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  default_capacity_provider_strategy {
    base              = "0"
    weight            = "1"
    capacity_provider = "FARGATE_SPOT"
  }
}
