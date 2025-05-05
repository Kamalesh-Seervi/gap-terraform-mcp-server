# GCP Terraform MCP Server

MCP server for Terraform on GCP best practices, infrastructure as code patterns, and security compliance with Checkov.

## Features

- **Terraform Best Practices** - Get prescriptive Terraform advice for building applications on GCP
  - GCP Architecture guidance for Terraform configurations
  - Security and compliance recommendations
  - Best practices for GCP provider configurations

- **Security-First Development Workflow** - Follow a structured process for creating secure code
  - Step-by-step guidance for validation and security scanning
  - Integration of Checkov at the right stages of development
  - Clear handoff points between AI assistance and developer deployment

- **Checkov Integration** - Work with Checkov for security and compliance scanning
  - Run security scans on Terraform code to identify vulnerabilities
  - Automatically fix identified security issues when possible
  - Get detailed remediation guidance for compliance issues

- **GCP Provider Documentation** - Search for Google Cloud provider resources
  - Find documentation for specific resources and attributes
  - Get example snippets and implementation guidance
  - Access best practices for GCP service configuration

- **GCP GenAI Modules** - Access specialized modules for AI/ML workloads
  - Vertex AI module for generative AI applications
  - BigQuery and BigTable for data storage capabilities
  - Cloud Functions for serverless workloads
  - Google Kubernetes Engine for AI workload orchestration

- **Terraform Registry Module Analysis** - Analyze Terraform Registry modules
  - Search for modules by URL or identifier
  - Extract input variables, output variables, and README content
  - Understand module usage and configuration options
  - Analyze module structure and dependencies

- **Terraform Workflow Execution** - Run Terraform commands directly
  - Initialize, plan, validate, apply, and destroy operations
  - Pass variables and specify GCP regions
  - Get formatted command output for analysis

## Tools and Resources

- **Terraform Development Workflow**: Follow security-focused development process via `terraform://workflow_guide`
- **GCP Best Practices**: Access GCP-specific guidance via `terraform://gcp_best_practices`
- **GCP Provider Resources**: Access resource listings via `terraform://gcp_provider_resources_listing`

## Prerequisites

1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.10`
3. Install Terraform CLI for workflow execution
4. Install Checkov for security scanning
5. Set up GCP authentication (gcloud CLI recommended)

## Installation

### Install FastMCP

We recommend using `uv` to install and manage FastMCP:

```bash
uv add fastmcp
```

Alternatively, install directly with pip or uv pip:

```bash
uv pip install fastmcp
# or
pip install fastmcp
```

### Install FastMCP (with models support)

The PyPI release of FastMCP may not include the `fastmcp.models` submodule required by the CLI. To install the latest code directly from GitHub:

```bash
pip install --upgrade git+https://github.com/jlowin/fastmcp.git@main#egg=fastmcp
```

Then verify with:
```bash
fastmcp version
```

### Verify Installation

Run:

```bash
fastmcp version
```

For more details, see the FastMCP docs: https://github.com/jlowin/fastmcp

Here are some ways you can work with MCP: (e.g. for an MCP client configuration):

```json
{
  "mcpServers": {
    "gcp-terraform-mcp-server": {
      "command": "uvx",
      "args": ["gcp-terraform-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

or docker after a successful `docker build -t gcp-terraform-mcp-server .`:

```json
{
  "mcpServers": {
    "gcp-terraform-mcp-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--interactive",
        "--env",
        "FASTMCP_LOG_LEVEL=ERROR",
        "gcp-terraform-mcp-server:latest"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Local Development

To run and develop locally:

1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Upgrade pip and install project dependencies

```bash
pip install --upgrade pip
pip install -e .
```

3. Run the MCP server

```bash
uvicorn gcp_terraform_mcp_server.main:app --host 0.0.0.0 --port 8080
```

4. (Optional) To use the script entry point

```bash
gcp-terraform-mcp-server
```

Ensure that `fastmcp` and other dependencies are installed successfully. If you see `ModuleNotFoundError: No module named 'fastmcp.models'`, make sure the virtual environment is active and the dependencies installed without errors.

## Running the Server

Instead of invoking the main module directly, use the FastMCP CLI to start your server:

```bash
# Start with stdio transport (default)
fastmcp run src/gcp_terraform_mcp_server/main.py:mcp

# Or start as an SSE server on port 8080
fastmcp run src/gcp_terraform_mcp_server/main.py:mcp --transport sse --host 0.0.0.0 --port 8080
```

Make sure you have `fastmcp` installed in your active environment. This CLI automatically locates the `mcp = FastMCP(...)` instance exported in your `main.py`.

## Available MCP Commands

When using this server with GitHub Copilot Chat or other MCP clients, the following commands are available:

### Terraform Workflow Tools

| Command | Description | Example |
|---------|-------------|---------|
| `terraform_workflow_guide` | Get a comprehensive guide for Terraform on GCP | `/mcp gcp-terraform-mcp terraform_workflow_guide` |
| `terraform_init` | Initialize a Terraform project | `/mcp gcp-terraform-mcp terraform_init path="./my-project"` |
| `terraform_validate` | Validate a Terraform project | `/mcp gcp-terraform-mcp terraform_validate path="./my-project"` |
| `terraform_plan` | Plan a Terraform project | `/mcp gcp-terraform-mcp terraform_plan path="./my-project"` |
| `terraform_apply` | Apply a Terraform plan | `/mcp gcp-terraform-mcp terraform_apply path="./my-project" plan_file="tfplan"` |
| `terraform_destroy` | Destroy Terraform resources | `/mcp gcp-terraform-mcp terraform_destroy path="./my-project"` |

### Checkov Security Tools

| Command | Description | Example |
|---------|-------------|---------|
| `terraform_run_checkov` | Run Checkov security scan | `/mcp gcp-terraform-mcp terraform_run_checkov path="./my-project"` |
| `terraform_fix_security_issues` | Fix security issues with Checkov | `/mcp gcp-terraform-mcp terraform_fix_security_issues path="./my-project"` |

### GCP Best Practices & Security

| Command | Description | Example |
|---------|-------------|---------|
| `terraform_gcp_best_practices` | Get GCP best practices | `/mcp gcp-terraform-mcp terraform_gcp_best_practices` |
| `terraform_gcp_security_recommendations` | Get GCP security recommendations | `/mcp gcp-terraform-mcp terraform_gcp_security_recommendations impact="HIGH"` |

### GCP Provider Documentation

| Command | Description | Example |
|---------|-------------|---------|
| `terraform_gcp_provider_resources_listing` | List GCP provider resources | `/mcp gcp-terraform-mcp terraform_gcp_provider_resources_listing service="compute"` |
| `terraform_gcp_resource_documentation` | Get GCP resource documentation | `/mcp gcp-terraform-mcp terraform_gcp_resource_documentation resource_name="google_storage_bucket"` |

### Terraform Registry Tools

| Command | Description | Example |
|---------|-------------|---------|
| `terraform_search_modules` | Search Terraform modules | `/mcp gcp-terraform-mcp terraform_search_modules query="gcp storage"` |
| `terraform_analyze_module` | Analyze Terraform module | `/mcp gcp-terraform-mcp terraform_analyze_module module_id="GoogleCloudPlatform/storage/google/latest"` |

### GenAI Module Tools

| Command | Description | Example |
|---------|-------------|---------|
| `terraform_genai_modules` | List GenAI modules | `/mcp gcp-terraform-mcp terraform_genai_modules` |
| `terraform_vertex_ai_module` | Get Vertex AI module template | `/mcp gcp-terraform-mcp terraform_vertex_ai_module` |
| `terraform_gke_ai_module` | Get GKE AI module template | `/mcp gcp-terraform-mcp terraform_gke_ai_module` |

## GitHub Copilot Integration

To use this MCP server with GitHub Copilot Chat, add the following configuration to your VS Code settings.json:

```json
"mcp": {
  "inputs": [],
  "servers": {
    "gcp-terraform-mcp": {
      "command": "/path/to/your/venv/bin/fastmcp",
      "args": [
        "run",
        "/path/to/your/src/gcp_terraform_mcp_server/main.py:mcp"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "INFO"
      },
      "autoApprove": ["terraform_"]
    }
  }
}
```

After adding this configuration and restarting VS Code, you can use the commands listed above in the GitHub Copilot Chat panel.

## Security Considerations

When using this MCP server, you should consider:
- **Following the structured development workflow** that integrates validation and security scanning
- Reviewing all Checkov warnings and errors manually
- Fixing security issues rather than ignoring them whenever possible
- Documenting clear justifications for any necessary exceptions
- Using the RunCheckovScan tool regularly to verify security compliance
- Following GCP security best practices for your infrastructure

Before applying Terraform changes to production environments, you should conduct your own independent assessment to ensure that your infrastructure would comply with your own specific security and quality control practices and standards, as well as the local laws, rules, and regulations that govern you and your content.