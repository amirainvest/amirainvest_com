We are using Terraform for deployment.

# Requirements

* [Install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started).
* Cd `amirainvest_com/terraform`
* Run `terraform init`

# Deployment

* Merge PR into main
* Wait for the [deploy GH action](https://github.com/amirainvest/amirainvest_com/actions/workflows/deploy.yml) to finish
* Run `terraform refresh`
* Run `terraform plan -out="./tf_plan"`
* Read the output and make sure nothing crazy is going to happen
* Run `terraform apply "./tf_plan"`
* Apply any Alembic migrations

# Adding existing infrastructure to TF

[Terraformer](https://github.com/GoogleCloudPlatform/terraformer/blob/master/docs/aws.md)

# Reading

[TF AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
[Terraform tutorials](https://learn.hashicorp.com/terraform)
