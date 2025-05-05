from __future__ import annotations
import os
import logging
import sys, types

# Stub fastmcp.models to satisfy CLI import
_fastmcp_models = types.ModuleType("fastmcp.models")
_fastmcp_models.MCPRequest = object
_fastmcp_models.MCPResponse = object
sys.modules["fastmcp.models"] = _fastmcp_models

from fastmcp import FastMCP

from gcp_terraform_mcp_server.handlers import (
    checkov_handlers,
    gcp_best_practices_handlers,
    gcp_provider_handlers,
    terraform_registry_handlers,
    terraform_workflow_handlers,
    genai_modules_handlers,
)

# Create FastMCP server instance
mcp = FastMCP(
    name="GCP Terraform MCP Server",
    instructions="Terraform on GCP best practices, infrastructure as code patterns, and security compliance with Checkov",
)

# Register Terraform workflow tools
@mcp.tool(name="terraform_workflow_guide", description="Get workflow guide for Terraform on GCP")
def workflow_guide() -> str:
    return terraform_workflow_handlers.get_workflow_guide().content

@mcp.tool(name="terraform_init", description="Initialize Terraform project")
def terraform_init(path: str) -> str:
    return terraform_workflow_handlers.initialize_project(path).content

@mcp.tool(name="terraform_validate", description="Validate Terraform project")
def terraform_validate(path: str) -> str:
    return terraform_workflow_handlers.validate_project(path).content

@mcp.tool(name="terraform_plan", description="Plan Terraform project")
def terraform_plan(path: str, variables: dict[str, str] | None = None) -> str:
    return terraform_workflow_handlers.plan_project(path, variables).content

@mcp.tool(name="terraform_apply", description="Apply Terraform plan")
def terraform_apply(path: str, plan_file: str = "tfplan") -> str:
    return terraform_workflow_handlers.apply_project(path, plan_file).content

@mcp.tool(name="terraform_destroy", description="Destroy Terraform resources")
def terraform_destroy(path: str, variables: dict[str, str] | None = None) -> str:
    return terraform_workflow_handlers.destroy_project(path, variables).content

# Register Checkov tools
@mcp.tool(name="terraform_run_checkov", description="Run Checkov scan")
def run_checkov(path: str) -> str:
    return checkov_handlers.run_checkov_scan(path).content

@mcp.tool(name="terraform_fix_security_issues", description="Fix security issues with Checkov")
def fix_security(path: str, checks: list[str] | None = None) -> str:
    return checkov_handlers.fix_security_issues(path, checks).content

# Register GCP best practices tools
@mcp.tool(name="terraform_gcp_best_practices", description="Get GCP best practices")
def best_practices(category: str | None = None) -> str:
    return gcp_best_practices_handlers.get_best_practices(category).content

@mcp.tool(name="terraform_gcp_security_recommendations", description="Get GCP security recommendations")
def security_recs(impact: str | None = None) -> str:
    return gcp_best_practices_handlers.get_security_recommendations(impact).content

# Register GCP provider resource tools
@mcp.tool(name="terraform_gcp_provider_resources_listing", description="List GCP provider resources")
def list_resources(service: str | None = None) -> str:
    return gcp_provider_handlers.list_provider_resources(service).content

@mcp.tool(name="terraform_gcp_resource_documentation", description="Get GCP resource documentation")
def resource_docs(resource_name: str) -> str:
    return gcp_provider_handlers.get_resource_documentation(resource_name).content

# Register Terraform Registry tools
@mcp.tool(name="terraform_search_modules", description="Search Terraform modules")
def search_modules(query: str) -> str:
    return terraform_registry_handlers.search_modules(query).content

@mcp.tool(name="terraform_analyze_module", description="Analyze Terraform module")
async def analyze_module(module_id: str) -> str:
    resp = await terraform_registry_handlers.analyze_module(module_id)
    return resp.content

# Register GenAI modules tools
@mcp.tool(name="terraform_genai_modules", description="List GenAI modules")
def list_genai() -> str:
    return genai_modules_handlers.list_genai_modules().content

@mcp.tool(name="terraform_vertex_ai_module", description="Get Vertex AI module template")
def vertex_ai() -> str:
    return genai_modules_handlers.get_vertex_ai_module().content

@mcp.tool(name="terraform_gke_ai_module", description="Get GKE AI module template")
def gke_ai() -> str:
    return genai_modules_handlers.get_gke_ai_module().content


def main() -> None:
    log_level = os.environ.get("FASTMCP_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level), format="%(asctime)s %(levelname)s %(message)s")
    mcp.run()


if __name__ == "__main__":
    main()