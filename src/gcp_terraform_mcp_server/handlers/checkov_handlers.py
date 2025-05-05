"""
Handlers for Checkov security scanning operations.
"""
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

from gcp_terraform_mcp_server.models import MCPResponse

logger = logging.getLogger(__name__)

def run_checkov_scan(path: str, framework: Optional[str] = "terraform") -> MCPResponse:
    """
    Run a Checkov security scan on Terraform code.
    
    Args:
        path: Path to the Terraform code to scan
        framework: Framework to use (default: terraform)
        
    Returns:
        MCPResponse with scan results
    """
    logger.info(f"Running Checkov scan on {path} for framework {framework}")
    
    try:
        # Run Checkov with JSON output
        cmd = ["checkov", "-d", path, "--framework", framework, "-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0 and not result.stdout:
            # If checkov failed without output, return the error
            logger.error(f"Checkov scan failed: {result.stderr}")
            return MCPResponse(
                content=f"Error running Checkov scan: {result.stderr}",
                metadata={
                    "success": False,
                    "error": result.stderr,
                }
            )
        
        # Parse the JSON output
        try:
            scan_results = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse Checkov output: {result.stdout}")
            return MCPResponse(
                content=f"Failed to parse Checkov output. Raw output: {result.stdout}",
                metadata={
                    "success": False,
                    "raw_output": result.stdout,
                }
            )
            
        # Extract the summary and create a formatted response
        passed = scan_results.get("summary", {}).get("passed", 0)
        failed = scan_results.get("summary", {}).get("failed", 0)
        skipped = scan_results.get("summary", {}).get("skipped", 0)
        
        # Format results for better readability
        formatted_results = format_checkov_results(scan_results)
        
        return MCPResponse(
            content=formatted_results,
            metadata={
                "success": True,
                "summary": {
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                },
                "raw_results": scan_results,
            }
        )
    
    except Exception as e:
        logger.exception("Error during Checkov scan")
        return MCPResponse(
            content=f"An error occurred during the Checkov scan: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


def fix_security_issues(path: str, checks: Optional[List[str]] = None) -> MCPResponse:
    """
    Attempt to automatically fix security issues identified by Checkov.
    
    Args:
        path: Path to the Terraform code to fix
        checks: List of specific check IDs to fix (optional)
        
    Returns:
        MCPResponse with fix results
    """
    logger.info(f"Attempting to fix security issues in {path}")
    
    try:
        # Run Checkov with the fix option
        cmd = ["checkov", "-d", path, "--framework", "terraform", "--fix"]
        
        # Add specific checks if provided
        if checks and len(checks) > 0:
            cmd.extend(["--check", ",".join(checks)])
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0 and not result.stdout:
            # If checkov failed without output, return the error
            logger.error(f"Checkov fix failed: {result.stderr}")
            return MCPResponse(
                content=f"Error fixing security issues: {result.stderr}",
                metadata={
                    "success": False,
                    "error": result.stderr,
                }
            )
            
        # Process the output
        if "Fixed" in result.stdout:
            # Extract information about what was fixed
            fixed_issues = extract_fixed_issues(result.stdout)
            
            return MCPResponse(
                content=f"Successfully fixed {len(fixed_issues)} security issues in {path}.\n\n" + 
                        format_fixed_issues(fixed_issues),
                metadata={
                    "success": True,
                    "fixed_issues": fixed_issues,
                    "raw_output": result.stdout,
                }
            )
        else:
            return MCPResponse(
                content=f"No security issues were automatically fixed. Manual remediation may be required.\n\n" +
                        f"Output: {result.stdout}",
                metadata={
                    "success": True,
                    "fixed_issues": [],
                    "raw_output": result.stdout,
                }
            )
            
    except Exception as e:
        logger.exception("Error while fixing security issues")
        return MCPResponse(
            content=f"An error occurred while fixing security issues: {str(e)}",
            metadata={
                "success": False,
                "error": str(e),
            }
        )


def format_checkov_results(scan_results: Dict[str, Any]) -> str:
    """Format Checkov results for readability."""
    summary = scan_results.get("summary", {})
    results = scan_results.get("results", {})
    
    formatted_output = []
    
    # Add summary
    formatted_output.append("# Checkov Security Scan Results\n")
    formatted_output.append(f"## Summary\n")
    formatted_output.append(f"- Passed: {summary.get('passed', 0)}")
    formatted_output.append(f"- Failed: {summary.get('failed', 0)}")
    formatted_output.append(f"- Skipped: {summary.get('skipped', 0)}")
    formatted_output.append(f"- Parsing Errors: {summary.get('parsing_errors', 0)}\n")
    
    # Add failed checks
    if "failed_checks" in results:
        formatted_output.append("## Failed Checks\n")
        for check in results["failed_checks"]:
            formatted_output.append(f"### {check.get('check_id')}: {check.get('check_name')}")
            formatted_output.append(f"- File: {check.get('file_path')}")
            formatted_output.append(f"- Resource: {check.get('resource')}")
            formatted_output.append(f"- Guideline: {check.get('guideline')}\n")
            formatted_output.append("#### Remediation:")
            formatted_output.append(f"{check.get('check_remediation', 'No specific remediation provided.')}\n")
    
    # Add passing checks summary
    if "passed_checks" in results:
        formatted_output.append(f"## Passed Checks: {len(results['passed_checks'])}\n")
    
    return "\n".join(formatted_output)


def extract_fixed_issues(output: str) -> List[Dict[str, str]]:
    """Extract information about fixed issues from the Checkov output."""
    fixed_issues = []
    lines = output.splitlines()
    
    current_issue = {}
    for line in lines:
        if line.startswith("Fixed"):
            if current_issue and "check_id" in current_issue:
                fixed_issues.append(current_issue)
                current_issue = {}
                
            parts = line.split(":", 1)
            if len(parts) > 1:
                check_info = parts[0].strip()
                file_info = parts[1].strip()
                
                check_id = check_info.replace("Fixed", "").strip()
                current_issue = {
                    "check_id": check_id,
                    "file": file_info
                }
        elif "was fixed" in line and current_issue:
            current_issue["description"] = line.strip()
    
    # Add the last issue if it exists
    if current_issue and "check_id" in current_issue:
        fixed_issues.append(current_issue)
        
    return fixed_issues


def format_fixed_issues(fixed_issues: List[Dict[str, str]]) -> str:
    """Format the list of fixed issues for readability."""
    if not fixed_issues:
        return "No issues were fixed automatically."
        
    formatted_output = ["## Fixed Issues\n"]
    
    for issue in fixed_issues:
        formatted_output.append(f"### {issue.get('check_id')}")
        formatted_output.append(f"- File: {issue.get('file')}")
        if "description" in issue:
            formatted_output.append(f"- Description: {issue.get('description')}")
        formatted_output.append("")
        
    return "\n".join(formatted_output)