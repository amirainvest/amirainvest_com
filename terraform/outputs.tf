output "aws_ecs_cluster_tfer--api_id" {
  value = "${aws_ecs_cluster.tfer--api.id}"
}

output "aws_ecs_service_tfer--api_prod-api-public-service_id" {
  value = "${aws_ecs_service.tfer--api_prod-api-public-service.id}"
}

output "aws_ecs_task_definition_tfer--task-definition-002F-prod-api-public-ecs-task-definition_id" {
  value = "${aws_ecs_task_definition.tfer--task-definition-002F-prod-api-public-ecs-task-definition.id}"
}
