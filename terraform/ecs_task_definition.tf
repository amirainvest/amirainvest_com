resource "aws_ecs_task_definition" "tfer--task-definition-002F-prod-api-public-ecs-task-definition" {
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
        { "name" : "ENVIRONMENT", "value" : "prod" },
        { "name" : "PROJECT", "value" : "backend" }
      ],
      essential : true,
      image : data.aws_ecr_image.backend_amirainvest_com.id,
      links : [],
      logConfiguration : {
        "logDriver" : "awslogs",
        "options" : {
          "awslogs-group" : "/ecs/prod-api-public-ecs-task-definition",
          "awslogs-region" : "us-east-1",
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
  cpu = "256"
  execution_role_arn = "arn:aws:iam::903791206266:role/ecsTaskExecutionRole"
  family = "prod-api-public-ecs-task-definition"
  memory = "512"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  runtime_platform {
    operating_system_family = "LINUX"
  }

  tags = {
    "ecs:taskDefinition:createdFrom" = "ecs-console-v2"
    "ecs:taskDefinition:stackId" = "arn:aws:cloudformation:us-east-1:903791206266:stack/ECS-Console-V2-TaskDefinition-f0122edf-e85a-4f1f-908e-aa9d4c121a2a/006c05b0-68c8-11ec-83ae-12be906bece1"
    env = "prod"
  }

  tags_all = {
    "ecs:taskDefinition:createdFrom" = "ecs-console-v2"
    "ecs:taskDefinition:stackId" = "arn:aws:cloudformation:us-east-1:903791206266:stack/ECS-Console-V2-TaskDefinition-f0122edf-e85a-4f1f-908e-aa9d4c121a2a/006c05b0-68c8-11ec-83ae-12be906bece1"
    env = "prod"
  }

  task_role_arn = "arn:aws:iam::903791206266:role/prod-api-public-ecs-task-definition-role"
}
