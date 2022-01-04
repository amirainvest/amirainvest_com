We are using Terraform for deployment.

# Requirements
* [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started).
* Cd `amirainvest_com/terraform`
* Run `terraform init`


# Deployment
* Run `terraform refresh`
* Run `terraform plan -out="./tf_plan"`
* Read the output and make sure nothing crazy is going to happen
* Run `terraform apply "./tf_plan`
