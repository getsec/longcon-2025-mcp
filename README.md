# JIRA MCP Server

## Security Wanning
This repository contains security training materials and proof-of-concept code designed for educational purposes only. The code demonstrates security vulnerabilities and attack techniques that could be harmful if misused.

Malicious sample code is in `./malicious_code_examples`

**AUTHORIZED USE ONLY**: This code is provided exclusively for:
- Security research and education
- Authorized penetration testing with explicit written permission
- Security awareness training in controlled environments
- Academic study of cybersecurity concepts

**PROHIBITED USES**: This code must NOT be used for:
- Unauthorized access to computer systems
- Malicious attacks against any systems or networks
- Any illegal activities or violations of computer crime laws
- Testing against systems without explicit written authorization

> By downloading, viewing, or using any code in this repository, you agree to use it only for lawful, authorized purposes and accept full responsibility for your actions.

## Disclaimer of Liability

The author(s) and contributors to this repository:
- Provide this code "AS IS" without warranty of any kind
- Disclaim all liability for any damages resulting from use or misuse
- Do not endorse or encourage any illegal or unauthorized activities
- Assume no responsibility for actions taken by users of this code

## Overview

A Model Context Protocol (MCP) server that provides JIRA integration.
This server allows AI systems to interact with JIRA issues, search for tickets, create new issues, and access project information.

> Examples here will use claude.

## Features

- **Get JIRA Issues**: Retrieve detailed information about specific JIRA issues
- **Create Issues**: Create new JIRA issues with customizable fields
- **Search Issues**: Search for JIRA issues using JQL (JIRA Query Language)
- **Project Information**: Access project keys and user information
- **Resources**: Access JIRA project keys and current user information

## Prerequisites

- Python 3.13 or higher
- JIRA account with API access
- JIRA Personal Access Token (PAT)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd longcon-mcp-demo
```

2. Install dependencies using uv (recommended) or pip:
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

## Configuration

### 1. JIRA Setup

1. Create a JIRA Personal Access Token:
   - Go to your JIRA instance
   - Navigate to Account Settings > Security > API tokens
   - Create a new token and copy it

2. Create a `.env` file in the project root:
```bash
JIRA_USERNAME=your-email@example.com
JIRA_PAT=your-personal-access-token
JIRA_URL=https://your-instance.atlassian.net
```

4. Update the project keys in the `jira_project_keys()` function (line 24):
```python
return ['YOUR_PROJECT_KEY']  # Replace with your actual project keys
```

### 2. Test the Server

Run the server locally to ensure it's working:
```bash
python main.py
```

The server should start without errors. Press Ctrl+C to stop it.

## Claude Desktop Configuration

### 1. Install Claude Desktop

Download and install Claude Desktop from [https://claude.ai/download](https://claude.ai/download)

### 2. Configure MCP Server

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration to the file. If the file doesn't exist, create it:

```json
{
  "mcpServers": {
    "longcon": {
      "command": "python",
      "args": ["/absolute/path/to/longcon-mcp-demo/main.py"],
      "env": {
        "JIRA_USERNAME": "your-email@example.com",
        "JIRA_PAT": "your-personal-access-token"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/longcon-mcp-demo/main.py` with the actual absolute path to your `main.py` file.

### 3. Alternative Configuration (Using .env file)

If you prefer to use the `.env` file for credentials:

```json
{
  "mcpServers": {
    "longcon": {
      "command": "python",
      "args": ["/absolute/path/to/longcon-mcp-demo/main.py"],
      "cwd": "/absolute/path/to/longcon-mcp-demo"
    }
  }
}
```

### 4. Using uv (Recommended)

For better dependency management, you can use uv:

```json
{
  "mcpServers": {
    "longcon": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/absolute/path/to/longcon-mcp-demo",
      "env": {
        "JIRA_USERNAME": "your-email@example.com",
        "JIRA_PAT": "your-personal-access-token"
      }
    }
  }
}
```

## Usage in Claude

Once configured, restart Claude Desktop. You can now use JIRA-related commands in your conversations:

### Available Tools

1. **Get JIRA Issue**:
   ```
   Get details for issue CRM-123
   ```

2. **Create JIRA Issue**:
   ```
   Create a new task in project CRM with summary "Fix login bug" and description "Users unable to login"
   ```

3. **Search JIRA Issues**:
   ```
   Search for all open issues assigned to me
   ```

### Available Resources

- **Project Keys**: Access available project keys
- **User Information**: Get current user details

### Example Interactions

```
User: What are the details of issue CRM-123?
Claude: [Uses get_jira_issue tool to fetch and display issue details]

User: Create a bug report for the login issue
Claude: [Uses create_jira_issue tool to create a new issue]

User: Show me all high-priority open issues
Claude: [Uses search_jira_issues with JQL: "priority = High AND status = Open"]
```

## Troubleshooting

### Common Issues

1. **"JIRA_USERNAME and JIRA_PAT must be set" Error**
   - Ensure your `.env` file is in the correct location
   - Verify the environment variables are set correctly in Claude Desktop config

2. **"Permission Denied" Error**
   - Check that your JIRA PAT has the necessary permissions
   - Verify your JIRA username is correct

3. **"Server not found" Error**
   - Ensure the JIRA server URL is correct in `main.py`
   - Check your internet connection

4. **Claude Desktop doesn't recognize the server**
   - Verify the absolute path in the configuration is correct
   - Restart Claude Desktop after making configuration changes
   - Check Claude Desktop logs for error messages

### Verification

To verify everything is working:

1. Start a new conversation in Claude Desktop
2. Ask: "What JIRA projects are available?"
3. Claude should respond with the project keys you configured

### Dependencies

- `jira`: JIRA Python library for API interactions
- `fastmcp`: Simplified MCP server framework
- `python-dotenv`: Environment variable management

## Security Notes

- Never commit your `.env` file or expose your JIRA PAT
- Use environment variables or secure configuration management
- Regularly rotate your JIRA Personal Access Tokens
- Limit PAT permissions to only what's necessary
