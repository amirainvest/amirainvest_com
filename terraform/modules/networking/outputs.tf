output "aws_vpc_public_private_id" {
  value = aws_vpc.public-private.id
}

output "subnet-private-1-id" {
  value = aws_subnet.private-1.id
}

output "subnet-private-2-id" {
  value = aws_subnet.private-2.id
}

output "subnet-private-3-id" {
  value = aws_subnet.private-3.id
}

output "subnet-public-1-id" {
  value = aws_subnet.public-1.id
}

output "subnet-public-2-id" {
  value = aws_subnet.public-2.id
}

output "subnet-public-3-id" {
  value = aws_subnet.public-3.id
}


output "private-subnets" {
  value = [aws_subnet.private-1.id, aws_subnet.private-2.id, aws_subnet.private-3.id]
}
