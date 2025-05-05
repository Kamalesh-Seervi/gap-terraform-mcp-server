"""
Handlers for Terraform workflow operations.
"""
import logging
import os
import subprocess
import tempfile
from typing import Dict, List, Optional

from gcp_terraform_mcp_server.models import MCPResponse

logger = logging.getLogger(__name__)


def get_workflow_guide() -> MCPResponse:
    """
    Get a guide for Terraform development workflow on GCP.
    
    Returns:
        MCPResponse with workflow guide
    """
    logger.info("Getting Terraform workflow guide")
    
    guide = """# Terraform Development Workflow for GCP

## Security-First Development Process

Follow this structured workflow to ensure secure Terraform deployments on GCP:

### 1. Initialize Project

```bash
terraform init
```

This initializes your Terraform project, downloading required providers and modules.

### 2. Format Code

```bash
terraform fmt -recursive
```

Format your Terraform code for consistency.

### 3. Validate Code

```bash
terraform validate
```

Validate your configuration for syntax errors and internal consistency.

### 4. Security Scan

```bash
checkov -d .
```

Run Checkov to identify security issues in your Terraform code.

### 5. Plan Deployment

```bash
terraform plan -out=tfplan
```

Generate an execution plan and review changes.

### 6. Security Scan on Plan

```bash
terraform show -json tfplan | checkov -f json
```

Run Checkov on the plan file to catch runtime security issues.

### 7. Apply Changes

```bash
terraform apply tfplan
```

Apply the plan to create/modify resources.

### 8. Document Architecture

Document your architecture, security considerations, and any deviations from best practices.

### 9. Destroy Resources (When No Longer Needed)

```bash
terraform destroy
```

Clean up resources when they're no longer needed.

## Best Practices

1. **Use GCP Service Account with Minimal Permissions**: Follow the principle of least privilege.
2. **Store State in a Secure Remote Backend**: Use GCS with versioning and encryption.
3. **Use Modules for Reusable Components**: Create or use trusted modules.
4. **Separate Environments**: Use workspaces or separate directories.
5. **Version Control**: Store your Terraform code in version control.
6. **Enable Checkov Pre-Commit Hook**: Catch issues before they're committed.
7. **Use Variables for Customization**: Avoid hardcoding values.
8. **Tag Resources**: Implement consistent tagging strategy.
9. **Use Data Sources for Dynamic Values**: Avoid hardcoding GCP resource identifiers.
10. **Review Terraform Plan Output**: Always review changes before applying.

## Security Checkpoints

- ✅ **Before init**: Repository is securely configured
- ✅ **After validate**: Code is syntactically correct
- ✅ **After first Checkov scan**: Code meets security standards
- ✅ **After plan**: Changes are as expected
- ✅ **After plan Checkov scan**: Runtime configuration is secure
- ✅ **After apply**: Resources match expected state
"""
    
    return MCPResponse(
        content=guide,
        metadata={
            "success": True,
            "workflow_steps": [
                "init", "fmt", "validate", "security_scan", "plan", 
                "security_scan_plan", "apply", "document", "destroy"
            ],
            "security_checkpoints": [
                "before_init", "after_validate", "after_first_scan",
                "after_plan", "after_plan_scan", "after_apply"
            ]
        }
    )


def initialize_project(working_dir: str) -> MCPResponse:
    """
    Initialize a Terraform project.
    
    Args:
        working_dir: The directory containing Terraform configuration files
        
    Returns:
        MCPResponse with initialization results
    """
    logger.info(f"Initializing Terraform project in {working_dir}")
    
    try:
        cmd = ["terraform", "init"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=working_dir)
        
        if result.returncode != 0:
            logger.error(f"Terraform init failed: {result.stderr}")
            return MCPResponse(
                content=f"Error initializing Terraform project: {result.stderr}",
                metadata={
                    "success": False,
                    "error": result.stderr,
                    "command": " ".join(cmd),
                }
            )
            
        # Process the output
        return MCPResponse(
            content=f"Terraform project initialized successfully in {working_dir}.\n\n{result.stdout}",
            metadata={
                "success": True,
                "raw_output": result.stdout,
                "command": " ".join(cmd),
            }
        )
            
    except Exception as e:
        logger.exception("Error during Terraform initialization")
        return MCPResponse(
            content=f"An error occurred during Terraform initialization: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


def validate_project(working_dir: str) -> MCPResponse:
    """
    Validate a Terraform project.
    
    Args:
        working_dir: The directory containing Terraform configuration files
        
    Returns:
        MCPResponse with validation results
    """
    logger.info(f"Validating Terraform project in {working_dir}")
    
    try:
        # Format the code first
        format_cmd = ["terraform", "fmt", "-recursive"]
        subprocess.run(format_cmd, capture_output=True, text=True, check=False, cwd=working_dir)
        
        # Then validate
        cmd = ["terraform", "validate", "-json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=working_dir)
        
        if result.returncode != 0:
            logger.error(f"Terraform validate failed: {result.stderr}")
            return MCPResponse(
                content=f"Error validating Terraform project: {result.stderr}",
                metadata={
                    "success": False,
                    "error": result.stderr,
                    "command": " ".join(cmd),
                }
            )
            
        # Process the output
        success_message = "Terraform configuration is valid."
        if "valid" in result.stdout and "true" in result.stdout.lower():
            return MCPResponse(
                content=success_message,
                metadata={
                    "success": True,
                    "raw_output": result.stdout,
                    "command": " ".join(cmd),
                }
            )
        else:
            errors = extract_validation_errors(result.stdout)
            return MCPResponse(
                content=f"Terraform validation failed with errors:\n\n{errors}",
                metadata={
                    "success": False,
                    "raw_output": result.stdout,
                    "errors": errors,
                    "command": " ".join(cmd),
                }
            )
            
    except Exception as e:
        logger.exception("Error during Terraform validation")
        return MCPResponse(
            content=f"An error occurred during Terraform validation: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


def plan_project(working_dir: str, variables: Optional[Dict[str, str]] = None) -> MCPResponse:
    """
    Generate a Terraform execution plan.
    
    Args:
        working_dir: The directory containing Terraform configuration files
        variables: Optional dictionary of variables to pass to Terraform
        
    Returns:
        MCPResponse with plan results
    """
    logger.info(f"Planning Terraform project in {working_dir}")
    
    try:
        # Build the command
        cmd = ["terraform", "plan", "-out=tfplan"]
        
        # Add variables if provided
        if variables:
            for key, value in variables.items():
                cmd.append(f"-var={key}={value}")
                
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=working_dir)
        
        if result.returncode != 0:
            logger.error(f"Terraform plan failed: {result.stderr}")
            return MCPResponse(
                content=f"Error planning Terraform project: {result.stderr}",
                metadata={
                    "success": False,
                    "error": result.stderr,
                    "command": " ".join(cmd),
                }
            )
            
        # Process the output
        formatted_output = format_plan_output(result.stdout)
        return MCPResponse(
            content=formatted_output,
            metadata={
                "success": True,
                "raw_output": result.stdout,
                "command": " ".join(cmd),
                "plan_file": os.path.join(working_dir, "tfplan"),
            }
        )
            
    except Exception as e:
        logger.exception("Error during Terraform plan")
        return MCPResponse(
            content=f"An error occurred during Terraform plan: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


def apply_project(working_dir: str, plan_file: Optional[str] = "tfplan") -> MCPResponse:
    """
    Apply a Terraform execution plan.
    
    Args:
        working_dir: The directory containing Terraform configuration files
        plan_file: Optional plan file to apply (default: tfplan)
        
    Returns:
        MCPResponse with apply results
    """
    logger.info(f"Applying Terraform plan in {working_dir}")
    
    try:
        # Check if plan file exists
        plan_path = os.path.join(working_dir, plan_file)
        if not os.path.exists(plan_path):
            return MCPResponse(
                content=f"Error: Plan file {plan_file} not found. Run terraform plan first.",
                metadata={
                    "success": False,
                    "error": f"Plan file {plan_file} not found",
                }
            )
        
        # Build the command
        cmd = ["terraform", "apply", plan_file]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=working_dir)
        
        if result.returncode != 0:
            logger.error(f"Terraform apply failed: {result.stderr}")
            return MCPResponse(
                content=f"Error applying Terraform plan: {result.stderr}",
                metadata={
                    "success": False,
                    "error": result.stderr,
                    "command": " ".join(cmd),
                }
            )
            
        # Process the output
        return MCPResponse(
            content=f"Terraform plan applied successfully.\n\n{result.stdout}",
            metadata={
                "success": True,
                "raw_output": result.stdout,
                "command": " ".join(cmd),
            }
        )
            
    except Exception as e:
        logger.exception("Error during Terraform apply")
        return MCPResponse(
            content=f"An error occurred during Terraform apply: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


def destroy_project(working_dir: str, variables: Optional[Dict[str, str]] = None) -> MCPResponse:
    """
    Destroy resources created by Terraform.
    
    Args:
        working_dir: The directory containing Terraform configuration files
        variables: Optional dictionary of variables to pass to Terraform
        
    Returns:
        MCPResponse with destroy results
    """
    logger.info(f"Destroying Terraform resources in {working_dir}")
    
    try:
        # Build the command
        cmd = ["terraform", "destroy", "-auto-approve"]
        
        # Add variables if provided
        if variables:
            for key, value in variables.items():
                cmd.append(f"-var={key}={value}")
                
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=working_dir)
        
        if result.returncode != 0:
            logger.error(f"Terraform destroy failed: {result.stderr}")
            return MCPResponse(
                content=f"Error destroying Terraform resources: {result.stderr}",
                metadata={
                    "success": False,
                    "error": result.stderr,
                    "command": " ".join(cmd),
                }
            )
            
        # Process the output
        return MCPResponse(
            content=f"Terraform resources destroyed successfully.\n\n{result.stdout}",
            metadata={
                "success": True,
                "raw_output": result.stdout,
                "command": " ".join(cmd),
            }
        )
            
    except Exception as e:
        logger.exception("Error during Terraform destroy")
        return MCPResponse(
            content=f"An error occurred during Terraform destroy: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


# Helper functions
def extract_validation_errors(output: str) -> str:
    """Extract validation errors from Terraform output."""
    try:
        import json
        data = json.loads(output)
        
        if not data.get("valid", True):
            diagnostics = data.get("diagnostics", [])
            errors = []
            
            for diag in diagnostics:
                if diag.get("severity", "") == "error":
                    location = ""
                    if "range" in diag:
                        file = diag["range"].get("filename", "")
                        if file:
                            location = f" in {file}"
                    
                    errors.append(f"- {diag.get('summary', 'Unknown error')}{location}: {diag.get('detail', '')}")
            
            return "\n".join(errors)
        
        return "No validation errors found."
    
    except (json.JSONDecodeError, KeyError):
        return "Could not parse validation output."


def format_plan_output(output: str) -> str:
    """Format Terraform plan output for readability."""
    lines = output.splitlines()
    formatted_lines = []
    
    # Find the plan summary sections
    plan_section = False
    for line in lines:
        if "Plan:" in line:
            plan_section = True
            formatted_lines.append("\n## Plan Summary\n")
        
        if plan_section:
            formatted_lines.append(line)
    
    if formatted_lines:
        return "# Terraform Plan\n\n" + "\n".join(formatted_lines)
    else:
        return "# Terraform Plan\n\n" + output