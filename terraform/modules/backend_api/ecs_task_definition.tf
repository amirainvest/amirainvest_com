resource "aws_ecs_task_definition" "api-public-ecs-task-definition" {
  container_definitions = jsonencode(
    [
      {
        command : [],
        cpu : 0,
        dnsSearchDomains : [],
        dnsServers : [],
        dockerSecurityOptions : [],
        entryPoint : [],
        environment : [
          { "name" : "ENVIRONMENT", "value" : var.environment },
          { "name" : "PROJECT", "value" : "backend" }
        ],
        essential : true,
        image : "${aws_ecr_repository.backend_amirainvest_com.repository_url}@${data.aws_ecr_image.backend_amirainvest_com.id}",
        links : [],
        logConfiguration : {
          "logDriver" : "awslogs",
          "options" : {
            "awslogs-group" : "/ecs/${var.environment}-api-public-ecs-task-definition",
            "awslogs-region" : var.region,
            "awslogs-stream-prefix" : "ecs"
          }
        },
        mountPoints : [],
        name : "backend_api",
        portMappings : [
          {
            "containerPort" : 5000,
            "hostPort" : 5000,
            "protocol" : "tcp"
          }
        ],
        systemControls : [],
        volumesFrom : []
      }
    ]

  )
  cpu                      = "1 vCPU"
  execution_role_arn       = "arn:aws:iam::903791206266:role/ecsTaskExecutionRole"
  family                   = "${var.environment}-api-public-ecs-task-definition"
  memory                   = "1GB"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  runtime_platform {
    operating_system_family = "LINUX"
  }

  tags = {
    "ecs:taskDefinition:createdFrom" = "ecs-console-v2"
    "ecs:taskDefinition:stackId"     = "arn:aws:cloudformation:${var.region}:903791206266:stack/ECS-Console-V2-TaskDefinition-f0122edf-e85a-4f1f-908e-aa9d4c121a2a/006c05b0-68c8-11ec-83ae-12be906bece1"
    env                              = var.environment
  }

  tags_all = {
    "ecs:taskDefinition:createdFrom" = "ecs-console-v2"
    "ecs:taskDefinition:stackId"     = "arn:aws:cloudformation:${var.region}:903791206266:stack/ECS-Console-V2-TaskDefinition-f0122edf-e85a-4f1f-908e-aa9d4c121a2a/006c05b0-68c8-11ec-83ae-12be906bece1"
    env                              = var.environment
  }

  task_role_arn = "arn:aws:iam::903791206266:role/${var.environment}-api-public-ecs-task-definition-role"
}
