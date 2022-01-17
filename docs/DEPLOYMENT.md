We are using Terraform for deployment.

# Requirements

* Have a Amira Invest Terraform Cloud Account

# Deployment

* Merge PR into main
* Wait for the [deploy GH action](https://github.com/amirainvest/amirainvest_com/actions/workflows/deploy.yml) to finish
* Go to [the Amira Invest Terraform cloud.](https://app.terraform.io/app/AmiraInvest/workspaces/Production)
* Click `actions` on the top right
* Click `Start a new plan`
* In `Reason for starting plan` type `PR #<PR number>`
* Make sure `Choose plan type` is `Plan (most common)`
* Click `Start plan`
* Wait for `Plan` to finish running
* Read the output and make sure nothing crazy is going to happen
* Click `Apply plan`
* Wait for the little green check to appear.
* [Apply any Alembic migrations]

# Adding existing infrastructure to TF

[Terraformer](https://github.com/GoogleCloudPlatform/terraformer/blob/master/docs/aws.md)

# Reading

[TF AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
[Terraform tutorials](https://learn.hashicorp.com/terraform)
