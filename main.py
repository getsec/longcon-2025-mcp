#!/usr/bin/env python3
import os
from jira import JIRA
from fastmcp import FastMCP
import re
from dotenv import load_dotenv
from typing import Any, Dict, Callable
from functools import wraps

load_dotenv()

def validate_mcp_response(response: Any) -> Dict[str, Any]:
    """
    Validates MCP tool/resource return values for security threats including:
    - Unsafe/untrusted domains
    - Prompt injection attempts
    - Malicious content patterns

    Args:
        response: The return value from any MCP tool or resource

    Returns:
        Dict with 'is_safe' boolean and 'issues' list of detected problems
    """
    issues = []

    # Convert response to string for analysis
    response_str = str(response).lower()

    # Check for untrusted/suspicious domains
    suspicious_domains = [
        'bit.ly', 'tinyurl.com', 'goo.gl', 'ow.ly',
        'pastebin.com', 'hastebin.com', 'dpaste.org',
        'discord.gg', 'throwaway', 'burner', 'gist.githubusercontent.com'
    ]

    for domain in suspicious_domains:
        if domain in response_str:
            issues.append(f"Suspicious domain detected: {domain}")

    # Check for prompt injection patterns
    injection_patterns = [
        r'ignore\s+previous\s+instructions',
        r'forget\s+everything\s+above',
        r'system\s*:\s*you\s+are',
        r'act\s+as\s+if\s+you\s+are',
        r'pretend\s+to\s+be',
        r'jailbreak',
        r'override\s+security',
        r'bypass\s+restrictions',
        r'execute\s+code',
        r'run\s+command',
        r'</?\s*system\s*>',
        r'</?\s*assistant\s*>',
        r'</?\s*user\s*>',
        r'<\s*script\s*>',
        r'javascript\s*:',
        r'data\s*:\s*text/html'
    ]

    for pattern in injection_patterns:
        if re.search(pattern, response_str, re.IGNORECASE):
            issues.append(f"Potential prompt injection pattern: {pattern}")

    # Check for credential exposure patterns
    credential_patterns = [
        r'password\s*[:=]\s*\S+',
        r'token\s*[:=]\s*[a-zA-Z0-9_\-]{20,}',
        r'api[_\-]?key\s*[:=]\s*[a-zA-Z0-9_\-]{20,}',
        r'secret\s*[:=]\s*[a-zA-Z0-9_\-]{20,}',
        r'bearer\s+[a-zA-Z0-9_\-]{20,}',
        r'ssh-rsa\s+[a-zA-Z0-9+/=]+',
        r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'
    ]

    for pattern in credential_patterns:
        if re.search(pattern, response_str, re.IGNORECASE):
            issues.append(f"Potential credential exposure: {pattern}")

    # Check for file system manipulation attempts
    filesystem_patterns = [
        r'\.\./+',
        r'/etc/passwd',
        r'/etc/shadow',
        r'%2e%2e%2f',
        r'file\s*:\s*//',
        r'\\\\.*\\\\',
        r'c:\\windows\\system32'
    ]

    for pattern in filesystem_patterns:
        if re.search(pattern, response_str, re.IGNORECASE):
            issues.append(f"Potential filesystem manipulation: {pattern}")

    # Check for code execution attempts
    exec_patterns = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__\s*\(',
        r'subprocess\.',
        r'os\.system\s*\(',
        r'shell\s*=\s*true',
        r'powershell\s+-',
        r'cmd\s*/c\s+',
        r'/bin/(?:sh|bash|zsh)'
    ]

    for pattern in exec_patterns:
        if re.search(pattern, response_str, re.IGNORECASE):
            issues.append(f"Potential code execution attempt: {pattern}")

    # Check for excessive length (potential DoS)
    if len(response_str) > 100000:
        issues.append("Response exceeds safe length limit")

    # Check for suspicious URL schemes
    url_schemes = re.findall(r'([a-z]+)://', response_str)
    safe_schemes = {'http', 'https', 'ftp', 'ftps', 'mailto'}
    for scheme in url_schemes:
        if scheme not in safe_schemes:
            issues.append(f"Suspicious URL scheme: {scheme}://")

    return {
        'is_safe': len(issues) == 0,
        'issues': issues,
        'response': response
    }

def secure_mcp_response(raise_on_unsafe: bool = True):
    """
    Decorator to validate MCP tool/resource return values for security threats.

    Args:
        raise_on_unsafe: If True, raises SecurityError on unsafe content.
                        If False, returns validation result dict.

    Usage:
        @secure_mcp_response()
        def my_tool():
            return potentially_unsafe_data

        @secure_mcp_response(raise_on_unsafe=False)
        def my_other_tool():
            return potentially_unsafe_data
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            validation = validate_mcp_response(result)

            if not validation['is_safe']:
                if raise_on_unsafe:
                    raise SecurityError(f"Unsafe MCP response detected: {validation['issues']}")
                else:
                    return validation

            return result
        return wrapper
    return decorator

class SecurityError(Exception):
    """Raised when unsafe content is detected in MCP responses"""
    pass

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
@secure_mcp_response()
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
@secure_mcp_response()
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
@secure_mcp_response()
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