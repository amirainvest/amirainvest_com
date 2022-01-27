import json
import os


"""
jobs:
  Params:
    uses: amirainvest/amirainvest_com/.github/workflows/params.yml@main

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
    run_deploy = "false"
    aws_region = "us-east-1"

    if _trigger_type == "pull_request" and _github_context["event"].get("pull_request"):
        if _github_context["event"]["pull_request"]["merged"] is True:
            run_deploy = "true"
    elif _trigger_type != "pull_request":
        run_deploy = "true"

    var_dict = {
        "environment": environment,
        "microservice_list": microservice_list,
        "deploy_tf": deploy_tf,
        "run_deploy": run_deploy,
        "AWS_REGION": aws_region,
    }
    for key, val in var_dict.items():
        print(f"{_print_base}{key}::{val!s}")


if __name__ == '__main__':
    main()

a = {
    "token": "***",
    "job": "test",
    "ref": "refs/heads/main",
    "sha": "430133fb03947a21978930fb37a2e40291b34cae",
    "repository": "amirainvest/amirainvest_com",
    "repository_owner": "amirainvest",
    "repositoryUrl": "git://github.com/amirainvest/amirainvest_com.git",
    "run_id": "1757799791",
    "run_number": "16",
    "retention_days": "90",
    "run_attempt": "1",
    "actor": "peterHoburg",
    "workflow": "Test",
    "head_ref": "",
    "base_ref": "",
    "event_name": "workflow_dispatch",
    "event": {
        "inputs": null,
        "organization": {
            "avatar_url": "https://avatars.githubusercontent.com/u/87669188?v=4",
            "description": "Active Management in a Social World. Building the platform empowering retail investors. ",
            "events_url": "https://api.github.com/orgs/amirainvest/events",
            "hooks_url": "https://api.github.com/orgs/amirainvest/hooks",
            "id": 87669188,
            "issues_url": "https://api.github.com/orgs/amirainvest/issues",
            "login": "amirainvest",
            "members_url": "https://api.github.com/orgs/amirainvest/members{/member}",
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjg3NjY5MTg4",
            "public_members_url": "https://api.github.com/orgs/amirainvest/public_members{/member}",
            "repos_url": "https://api.github.com/orgs/amirainvest/repos",
            "url": "https://api.github.com/orgs/amirainvest"
        },
        "ref": "refs/heads/main",
        "repository": {
            "allow_forking": false,
            "archive_url": "https://api.github.com/repos/amirainvest/amirainvest_com/{archive_format}{/ref}",
            "archived": false,
            "assignees_url": "https://api.github.com/repos/amirainvest/amirainvest_com/assignees{/user}",
            "blobs_url": "https://api.github.com/repos/amirainvest/amirainvest_com/git/blobs{/sha}",
            "branches_url": "https://api.github.com/repos/amirainvest/amirainvest_com/branches{/branch}",
            "clone_url": "https://github.com/amirainvest/amirainvest_com.git",
            "collaborators_url": "https://api.github.com/repos/amirainvest/amirainvest_com/collaborators{/collaborator}",
            "comments_url": "https://api.github.com/repos/amirainvest/amirainvest_com/comments{/number}",
            "commits_url": "https://api.github.com/repos/amirainvest/amirainvest_com/commits{/sha}",
            "compare_url": "https://api.github.com/repos/amirainvest/amirainvest_com/compare/{base}...{head}",
            "contents_url": "https://api.github.com/repos/amirainvest/amirainvest_com/contents/{+path}",
            "contributors_url": "https://api.github.com/repos/amirainvest/amirainvest_com/contributors",
            "created_at": "2021-12-21T03:54:04Z",
            "default_branch": "main",
            "deployments_url": "https://api.github.com/repos/amirainvest/amirainvest_com/deployments",
            "description": null,
            "disabled": false,
            "downloads_url": "https://api.github.com/repos/amirainvest/amirainvest_com/downloads",
            "events_url": "https://api.github.com/repos/amirainvest/amirainvest_com/events",
            "fork": false,
            "forks": 0,
            "forks_count": 0,
            "forks_url": "https://api.github.com/repos/amirainvest/amirainvest_com/forks",
            "full_name": "amirainvest/amirainvest_com",
            "git_commits_url": "https://api.github.com/repos/amirainvest/amirainvest_com/git/commits{/sha}",
            "git_refs_url": "https://api.github.com/repos/amirainvest/amirainvest_com/git/refs{/sha}",
            "git_tags_url": "https://api.github.com/repos/amirainvest/amirainvest_com/git/tags{/sha}",
            "git_url": "git://github.com/amirainvest/amirainvest_com.git",
            "has_downloads": true,
            "has_issues": true,
            "has_pages": false,
            "has_projects": true,
            "has_wiki": true,
            "homepage": null,
            "hooks_url": "https://api.github.com/repos/amirainvest/amirainvest_com/hooks",
            "html_url": "https://github.com/amirainvest/amirainvest_com",
            "id": 440383198,
            "is_template": false,
            "issue_comment_url": "https://api.github.com/repos/amirainvest/amirainvest_com/issues/comments{/number}",
            "issue_events_url": "https://api.github.com/repos/amirainvest/amirainvest_com/issues/events{/number}",
            "issues_url": "https://api.github.com/repos/amirainvest/amirainvest_com/issues{/number}",
            "keys_url": "https://api.github.com/repos/amirainvest/amirainvest_com/keys{/key_id}",
            "labels_url": "https://api.github.com/repos/amirainvest/amirainvest_com/labels{/name}",
            "language": "Python",
            "languages_url": "https://api.github.com/repos/amirainvest/amirainvest_com/languages",
            "license": null,
            "merges_url": "https://api.github.com/repos/amirainvest/amirainvest_com/merges",
            "milestones_url": "https://api.github.com/repos/amirainvest/amirainvest_com/milestones{/number}",
            "mirror_url": null,
            "name": "amirainvest_com",
            "node_id": "R_kgDOGj-23g",
            "notifications_url": "https://api.github.com/repos/amirainvest/amirainvest_com/notifications{?since,all,participating}",
            "open_issues": 90,
            "open_issues_count": 90,
            "owner": {
                "avatar_url": "https://avatars.githubusercontent.com/u/87669188?v=4",
                "events_url": "https://api.github.com/users/amirainvest/events{/privacy}",
                "followers_url": "https://api.github.com/users/amirainvest/followers",
                "following_url": "https://api.github.com/users/amirainvest/following{/other_user}",
                "gists_url": "https://api.github.com/users/amirainvest/gists{/gist_id}",
                "gravatar_id": "",
                "html_url": "https://github.com/amirainvest",
                "id": 87669188,
                "login": "amirainvest",
                "node_id": "MDEyOk9yZ2FuaXphdGlvbjg3NjY5MTg4",
                "organizations_url": "https://api.github.com/users/amirainvest/orgs",
                "received_events_url": "https://api.github.com/users/amirainvest/received_events",
                "repos_url": "https://api.github.com/users/amirainvest/repos",
                "site_admin": false,
                "starred_url": "https://api.github.com/users/amirainvest/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/amirainvest/subscriptions",
                "type": "Organization",
                "url": "https://api.github.com/users/amirainvest"
            },
            "private": true,
            "pulls_url": "https://api.github.com/repos/amirainvest/amirainvest_com/pulls{/number}",
            "pushed_at": "2022-01-27T18:21:00Z",
            "releases_url": "https://api.github.com/repos/amirainvest/amirainvest_com/releases{/id}",
            "size": 4003,
            "ssh_url": "git@github.com:amirainvest/amirainvest_com.git",
            "stargazers_count": 2,
            "stargazers_url": "https://api.github.com/repos/amirainvest/amirainvest_com/stargazers",
            "statuses_url": "https://api.github.com/repos/amirainvest/amirainvest_com/statuses/{sha}",
            "subscribers_url": "https://api.github.com/repos/amirainvest/amirainvest_com/subscribers",
            "subscription_url": "https://api.github.com/repos/amirainvest/amirainvest_com/subscription",
            "svn_url": "https://github.com/amirainvest/amirainvest_com",
            "tags_url": "https://api.github.com/repos/amirainvest/amirainvest_com/tags",
            "teams_url": "https://api.github.com/repos/amirainvest/amirainvest_com/teams",
            "topics": [],
            "trees_url": "https://api.github.com/repos/amirainvest/amirainvest_com/git/trees{/sha}",
            "updated_at": "2022-01-11T03:05:07Z",
            "url": "https://api.github.com/repos/amirainvest/amirainvest_com",
            "visibility": "private",
            "watchers": 2,
            "watchers_count": 2
        },
        "sender": {
            "avatar_url": "https://avatars.githubusercontent.com/u/3860655?v=4",
            "events_url": "https://api.github.com/users/peterHoburg/events{/privacy}",
            "followers_url": "https://api.github.com/users/peterHoburg/followers",
            "following_url": "https://api.github.com/users/peterHoburg/following{/other_user}",
            "gists_url": "https://api.github.com/users/peterHoburg/gists{/gist_id}",
            "gravatar_id": "",
            "html_url": "https://github.com/peterHoburg",
            "id": 3860655,
            "login": "peterHoburg",
            "node_id": "MDQ6VXNlcjM4NjA2NTU=",
            "organizations_url": "https://api.github.com/users/peterHoburg/orgs",
            "received_events_url": "https://api.github.com/users/peterHoburg/received_events",
            "repos_url": "https://api.github.com/users/peterHoburg/repos",
            "site_admin": false,
            "starred_url": "https://api.github.com/users/peterHoburg/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/peterHoburg/subscriptions",
            "type": "User",
            "url": "https://api.github.com/users/peterHoburg"
        },
        "workflow": ".github/workflows/test.yml"
    },
    "server_url": "https://github.com",
    "api_url": "https://api.github.com",
    "graphql_url": "https://api.github.com/graphql",
    "ref_name": "main",
    "ref_protected": false,
    "ref_type": "branch",
    "secret_source": "Actions",
    "workspace": "/home/runner/work/amirainvest_com/amirainvest_com",
    "action": "__run"
}
