# Rename resource

When renaming a resource:
* `terraform refresh`
* Commit
* Change the resource name
* `terraform state mv <old_name> <new_name>`
* `terraform plan`
* If nothing changes in the plan commit. If something does, have fun reading docs!
