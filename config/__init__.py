import os

VERSION="v1"

JIRA_API_TOKEN=os.getenv("JIRA_API_TOKEN")
assert JIRA_API_TOKEN is not None

JIRAURL="https://jira-pro.it.hpe.com:8443"
