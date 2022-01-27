import json
import os


"""
jobs:
  Params:
    runs-on: ubuntu-20.04
    outputs:
      environment: ${{ steps.params.outputs.environment }}
      microservice_list: ${{ steps.params.outputs.microservice_list }}
      deploy_tf: ${{ steps.params.outputs.deploy_tf }}
      pr_merged: ${{ steps.params.outputs.pr_merged }}
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Generate params
        env:
          GITHUB_CONTEXT: ${{ toJSON(github) }}
        id: params
        shell: bash
        run: python ./bin/github_params.py

  test_job:
    needs: Params
    runs-on: ubuntu-20.04
    steps:
      - name: Check if PR merged
        if: needs.Params.outputs.pr_merged != 'true'
"""

_github_context = json.loads(os.environ["GITHUB_CONTEXT"])
_print_base = "::set-output name="

_branch_name = _github_context["ref_name"]
_trigger_type = _github_context["event_name"]


def main():
    # TODO get this list from the OS
    microservice_list = ["backend_amirainvest_com", "brokerage.lambda", "market_data.lambda"]
    environment = "prod" if _branch_name == "main" else "test"
    deploy_tf = "true" if _branch_name == "main" else "false"
    pr_merged = "false"

    if _github_context["event"].get("pull_request"):
        if _github_context["event"]["pull_request"]["merged"] is True:
            pr_merged = "true"

    var_dict = {
        "environment": environment,
        "microservice_list": microservice_list,
        "deploy_tf": deploy_tf,
        "pr_merged": pr_merged,
    }
    for key, val in iter(var_dict):
        print(f"{_print_base}{key}::{val!s}")


if __name__ == '__main__':
    main()
