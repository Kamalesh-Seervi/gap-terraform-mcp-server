"""
Handlers for Terraform Registry module operations.
"""
import json
import logging
import re
import tempfile
import os
import subprocess
from typing import Any, Dict, List, Optional
import httpx

from gcp_terraform_mcp_server.models import MCPResponse

logger = logging.getLogger(__name__)


async def search_modules(query: str, provider: Optional[str] = "google") -> MCPResponse:
    """
    Search for Terraform modules in the Terraform Registry.
    
    Args:
        query: Search query for modules
        provider: Provider to filter by (default: google)
        
    Returns:
        MCPResponse with search results
    """
    logger.info(f"Searching for Terraform modules: query='{query}', provider='{provider}'")
    
    try:
        # Create the API URL
        url = "https://registry.terraform.io/v1/modules/search"
        params = {"q": query}
        
        if provider:
            params["provider"] = provider
            
        # Make the API request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
        if response.status_code != 200:
            logger.error(f"Module search failed: {response.text}")
            return MCPResponse(
                content=f"Error searching for modules: {response.text}",
                metadata={
                    "success": False,
                    "error": response.text,
                }
            )
            
        # Parse the response
        data = response.json()
        modules = data.get("modules", [])
        
        if not modules:
            return MCPResponse(
                content=f"No modules found for query: '{query}' with provider: '{provider}'",
                metadata={
                    "success": True,
                    "count": 0,
                    "modules": [],
                }
            )
            
        # Format the response
        formatted_output = [f"# Terraform Module Search Results\n"]
        formatted_output.append(f"Found {len(modules)} modules matching '{query}' for provider '{provider}':\n")
        
        for module in modules:
            name = module.get("name", "")
            namespace = module.get("namespace", "")
            provider_name = module.get("provider", "")
            description = module.get("description", "")
            downloads = module.get("downloads", 0)
            version = module.get("version", "")
            
            formatted_output.append(f"## {namespace}/{name}/{provider_name}")
            if description:
                formatted_output.append(f"{description}\n")
            
            formatted_output.append(f"- **Version:** {version}")
            formatted_output.append(f"- **Downloads:** {downloads}")
            formatted_output.append(f"- **Source:** terraform-{provider_name}-{name}")
            formatted_output.append(f"- **URL:** https://registry.terraform.io/modules/{namespace}/{name}/{provider_name}/\n")
            
        return MCPResponse(
            content="\n".join(formatted_output),
            metadata={
                "success": True,
                "count": len(modules),
                "modules": modules,
            }
        )
            
    except Exception as e:
        logger.exception("Error searching for Terraform modules")
        return MCPResponse(
            content=f"An error occurred while searching for Terraform modules: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


async def analyze_module(module_id: str) -> MCPResponse:
    """
    Analyze a Terraform module from the Terraform Registry.
    
    Args:
        module_id: Module ID in the format namespace/name/provider
        
    Returns:
        MCPResponse with module analysis
    """
    logger.info(f"Analyzing Terraform module: {module_id}")
    
    try:
        # Parse module ID
        parts = module_id.split("/")
        if len(parts) != 3:
            return MCPResponse(
                content=f"Invalid module ID: {module_id}. Format should be namespace/name/provider.",
                metadata={
                    "success": False,
                    "error": f"Invalid module ID: {module_id}",
                }
            )
            
        namespace, name, provider = parts
        
        # Fetch module details
        details_url = f"https://registry.terraform.io/v1/modules/{namespace}/{name}/{provider}"
        
        async with httpx.AsyncClient() as client:
            details_response = await client.get(details_url)
            
        if details_response.status_code != 200:
            logger.error(f"Module details fetch failed: {details_response.text}")
            return MCPResponse(
                content=f"Error fetching module details: {details_response.text}",
                metadata={
                    "success": False,
                    "error": details_response.text,
                }
            )
            
        # Parse the details
        details = details_response.json()
        latest_version = details.get("version", "")
        
        # Fetch the module content
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download module
            cmd = ["terraform", "init", "-get=true"]
            
            # Create a temp file with module reference
            temp_file = os.path.join(temp_dir, "main.tf")
            with open(temp_file, "w") as f:
                f.write(f"""
module "analyzed_module" {{
  source  = "{namespace}/{name}/{provider}"
  version = "{latest_version}"
}}
""")
            
            # Initialize to download the module
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=temp_dir)
            
            if result.returncode != 0:
                logger.error(f"Module download failed: {result.stderr}")
                return MCPResponse(
                    content=f"Error downloading module: {result.stderr}",
                    metadata={
                        "success": False,
                        "error": result.stderr,
                    }
                )
                
            # Try to find the module directory
            module_dir = os.path.join(temp_dir, ".terraform/modules/analyzed_module")
            if not os.path.exists(module_dir):
                # Try alternative locations
                modules_dir = os.path.join(temp_dir, ".terraform/modules")
                for d in os.listdir(modules_dir):
                    if d.startswith("analyzed_module"):
                        module_dir = os.path.join(modules_dir, d)
                        break
            
            module_data = {
                "inputs": [],
                "outputs": [],
                "resources": [],
                "readme": "",
            }
            
            # Extract inputs (variables)
            variables_file = os.path.join(module_dir, "variables.tf")
            if os.path.exists(variables_file):
                with open(variables_file, "r") as f:
                    content = f.read()
                    # Simple regex to find variable blocks
                    var_blocks = re.findall(r"variable\s+\"([^\"]+)\"\s+{([^}]+)}", content, re.DOTALL)
                    
                    for name, block in var_blocks:
                        variable = {"name": name}
                        
                        # Extract description
                        desc_match = re.search(r"description\s+=\s+\"([^\"]+)\"", block)
                        if desc_match:
                            variable["description"] = desc_match.group(1)
                            
                        # Extract type
                        type_match = re.search(r"type\s+=\s+([^\n]+)", block)
                        if type_match:
                            variable["type"] = type_match.group(1).strip()
                            
                        # Extract default value
                        default_match = re.search(r"default\s+=\s+([^\n]+)", block)
                        if default_match:
                            variable["default"] = default_match.group(1).strip()
                            
                        module_data["inputs"].append(variable)
            
            # Extract outputs
            outputs_file = os.path.join(module_dir, "outputs.tf")
            if os.path.exists(outputs_file):
                with open(outputs_file, "r") as f:
                    content = f.read()
                    # Simple regex to find output blocks
                    out_blocks = re.findall(r"output\s+\"([^\"]+)\"\s+{([^}]+)}", content, re.DOTALL)
                    
                    for name, block in out_blocks:
                        output = {"name": name}
                        
                        # Extract description
                        desc_match = re.search(r"description\s+=\s+\"([^\"]+)\"", block)
                        if desc_match:
                            output["description"] = desc_match.group(1)
                            
                        # Extract value
                        value_match = re.search(r"value\s+=\s+([^\n]+)", block)
                        if value_match:
                            output["value"] = value_match.group(1).strip()
                            
                        module_data["outputs"].append(output)
            
            # Extract README
            readme_file = os.path.join(module_dir, "README.md")
            if os.path.exists(readme_file):
                with open(readme_file, "r") as f:
                    module_data["readme"] = f.read()
        
        # Format the response
        formatted_output = [f"# Module Analysis: {module_id}\n"]
        
        # Add module details
        formatted_output.append(f"**Version:** {latest_version}")
        formatted_output.append(f"**Registry Link:** https://registry.terraform.io/modules/{module_id}\n")
        
        # Add inputs section
        formatted_output.append(f"## Inputs ({len(module_data['inputs'])})\n")
        for input_var in module_data["inputs"]:
            name = input_var.get("name", "")
            desc = input_var.get("description", "No description provided")
            var_type = input_var.get("type", "any")
            default = input_var.get("default", "no default")
            
            formatted_output.append(f"### {name}")
            formatted_output.append(f"- **Description:** {desc}")
            formatted_output.append(f"- **Type:** {var_type}")
            formatted_output.append(f"- **Default:** {default}\n")
        
        # Add outputs section
        formatted_output.append(f"## Outputs ({len(module_data['outputs'])})\n")
        for output_var in module_data["outputs"]:
            name = output_var.get("name", "")
            desc = output_var.get("description", "No description provided")
            
            formatted_output.append(f"### {name}")
            formatted_output.append(f"- **Description:** {desc}\n")
        
        # Add README section (truncate if too long)
        readme = module_data["readme"]
        if len(readme) > 2000:
            readme = readme[:2000] + "...\n\n(README truncated due to length)"
            
        formatted_output.append(f"## README\n\n{readme}")
        
        return MCPResponse(
            content="\n".join(formatted_output),
            metadata={
                "success": True,
                "module_id": module_id,
                "version": latest_version,
                "module_data": module_data,
            }
        )
        
    except Exception as e:
        logger.exception("Error analyzing Terraform module")
        return MCPResponse(
            content=f"An error occurred while analyzing the Terraform module: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )