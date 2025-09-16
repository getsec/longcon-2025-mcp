#!/usr/bin/env python3
import os
from jira import JIRA
from fastmcp import FastMCP

from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Jira MCP Server")

try:
    username = os.environ['JIRA_USERNAME']
    api_token = os.environ['JIRA_PAT']
    jira_url = os.environ['JIRA_URL']
except KeyError:
    raise EnvironmentError("JIRA_USERNAME and JIRA_PAT must be set in environment variables")


jira = JIRA(server=jira_url, basic_auth=(username, api_token))

@mcp.resource(uri="resource://jira/project-keys")
def jira_project_keys() -> list:
    """ returns a list of project keys """
    return ['CRM']

@mcp.resource(uri="resource://jira/me")
def jira_me() -> dict:
    """ returns information about the current user """
    user = jira.myself()
    return {
        "name": user['displayName'],
        "email": user['emailAddress'],
        "timeZone": user['timeZone'],
        "accountId": user['accountId']
    }

@mcp.tool()
def get_jira_issue(issue_key: str) -> dict:
    """
    Get detailed information about a specific JIRA issue

    Args:
        issue_key: The JIRA issue key (e.g., "PROJ-123")

    Returns:
        Detailed issue information
    """
    try:
        issue = jira.issue(issue_key)
        content = {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "None",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
        }

        return content
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_jira_issue(project_key: str, summary: str, description: str = "", issue_type: str = "Task", priority: str = "Medium") -> str:
    """
    Create a new JIRA issue

    Args:
        project_key: The JIRA project key (e.g., "PROJ")
        summary: Issue summary/title
        description: Issue description (optional)
        issue_type: Issue type (default: "Task")
        priority: Issue priority (default: "Medium")

    Returns:
        Created issue key and details
    """
    try:

        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            'priority': {'name': priority}
        }

        new_issue = jira.create_issue(fields=issue_dict)

        return f"Successfully created issue: {new_issue.key}\n" \
               f"Summary: {summary}\n" \
               f"Type: {issue_type}\n" \
               f"Priority: {priority}"
    except Exception as e:
        return f"Error creating issue: {str(e)}"

@mcp.tool()
def search_jira_issues(jql: str, max_results: int = 10) -> list[dict]:
    """
    Search for JIRA issues using JQL

    Args:
        jql: JIRA Query Language string
        max_results: Maximum number of results to return (default: 10)
    """
    issues = jira.search_issues(jql, maxResults=max_results)
    results = []
    for issue in issues:
        results.append({
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "None",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
        })
    return results

if __name__ == "__main__":
    mcp.run()