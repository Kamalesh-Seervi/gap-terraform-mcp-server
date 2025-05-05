"""
Handlers for GCP provider resources and documentation.
"""
import logging
import json
from typing import Any, Dict, List, Optional

from gcp_terraform_mcp_server.models import MCPResponse

logger = logging.getLogger(__name__)

# Sample GCP provider resources database
# In a production environment, this would be more extensive or fetched dynamically
GCP_PROVIDER_RESOURCES = {
    "compute": [
        {
            "name": "google_compute_instance",
            "description": "Manages a VM instance resource within GCE.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance"
        },
        {
            "name": "google_compute_disk",
            "description": "Manages a disk within GCE.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_disk"
        },
        {
            "name": "google_compute_network",
            "description": "Manages a VPC network.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_network"
        },
        {
            "name": "google_compute_firewall",
            "description": "Manages a firewall resource within GCE.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_firewall"
        },
        {
            "name": "google_compute_address",
            "description": "Manages a static IP address resource in GCE.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_address"
        }
    ],
    "storage": [
        {
            "name": "google_storage_bucket",
            "description": "Manages a Cloud Storage bucket.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket"
        },
        {
            "name": "google_storage_bucket_object",
            "description": "Manages an object within a Cloud Storage bucket.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket_object"
        },
        {
            "name": "google_storage_bucket_iam_binding",
            "description": "Manages IAM bindings for a Cloud Storage bucket.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket_iam_binding"
        }
    ],
    "container": [
        {
            "name": "google_container_cluster",
            "description": "Manages a Google Kubernetes Engine (GKE) cluster.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster"
        },
        {
            "name": "google_container_node_pool",
            "description": "Manages a node pool in a GKE cluster.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_node_pool"
        }
    ],
    "sql": [
        {
            "name": "google_sql_database_instance",
            "description": "Manages a Cloud SQL instance.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database_instance"
        },
        {
            "name": "google_sql_database",
            "description": "Manages a Cloud SQL database.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database"
        },
        {
            "name": "google_sql_user",
            "description": "Manages a Cloud SQL user.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_user"
        }
    ],
    "iam": [
        {
            "name": "google_project_iam_binding",
            "description": "Manages IAM bindings for a GCP project.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_binding"
        },
        {
            "name": "google_service_account",
            "description": "Manages a Google Cloud service account.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account"
        },
        {
            "name": "google_service_account_key",
            "description": "Manages a Google Cloud service account key.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_key"
        }
    ],
    "cloudrun": [
        {
            "name": "google_cloud_run_service",
            "description": "Manages a Cloud Run service.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_service"
        }
    ],
    "bigquery": [
        {
            "name": "google_bigquery_dataset",
            "description": "Manages a BigQuery dataset.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset"
        },
        {
            "name": "google_bigquery_table",
            "description": "Manages a BigQuery table.",
            "documentation_url": "https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_table"
        }
    ]
}


# Sample resource documentation database
# In a production environment, this would be fetched from Terraform Registry API
RESOURCE_DOCUMENTATION = {
    "google_compute_instance": {
        "description": "Manages a VM instance resource within GCE.",
        "arguments": [
            {
                "name": "name",
                "description": "The name of the instance.",
                "required": True,
                "type": "string"
            },
            {
                "name": "machine_type",
                "description": "The machine type to create.",
                "required": True,
                "type": "string"
            },
            {
                "name": "zone",
                "description": "The zone that the machine should be created in.",
                "required": True,
                "type": "string"
            },
            {
                "name": "boot_disk",
                "description": "The boot disk for the instance.",
                "required": True,
                "type": "block"
            },
            {
                "name": "network_interface",
                "description": "Networks to attach to the instance.",
                "required": True,
                "type": "block"
            },
            {
                "name": "metadata",
                "description": "Metadata key/value pairs to make available from within the instance.",
                "required": False,
                "type": "map(string)"
            },
            {
                "name": "tags",
                "description": "Tags to attach to the instance.",
                "required": False,
                "type": "set(string)"
            }
        ],
        "example": """
resource "google_compute_instance" "default" {
  name         = "test-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral IP
    }
  }

  metadata = {
    foo = "bar"
  }

  tags = ["foo", "bar"]
}
"""
    },
    "google_storage_bucket": {
        "description": "Manages a Cloud Storage bucket.",
        "arguments": [
            {
                "name": "name",
                "description": "The name of the bucket.",
                "required": True,
                "type": "string"
            },
            {
                "name": "location",
                "description": "The GCS location of the bucket.",
                "required": True,
                "type": "string"
            },
            {
                "name": "force_destroy",
                "description": "When deleting a bucket, this boolean option indicates whether all contained objects should be deleted.",
                "required": False,
                "type": "bool"
            },
            {
                "name": "uniform_bucket_level_access",
                "description": "Enables Uniform bucket-level access.",
                "required": False,
                "type": "bool"
            },
            {
                "name": "versioning",
                "description": "The bucket's Versioning configuration.",
                "required": False,
                "type": "block"
            }
        ],
        "example": """
resource "google_storage_bucket" "static-site" {
  name          = "image-store-bucket"
  location      = "EU"
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }
}
"""
    }
}


def list_provider_resources(service: Optional[str] = None) -> MCPResponse:
    """
    List GCP provider resources, optionally filtered by service.
    
    Args:
        service: Optional service filter (compute, storage, container, etc.)
        
    Returns:
        MCPResponse with resource listings
    """
    logger.info(f"Listing GCP provider resources for service: {service}")
    
    if service and service in GCP_PROVIDER_RESOURCES:
        resources = {service: GCP_PROVIDER_RESOURCES[service]}
    else:
        resources = GCP_PROVIDER_RESOURCES
        
    if not resources:
        return MCPResponse(
            content=f"No resources found for service: {service}",
            metadata={
                "success": False,
                "error": f"No resources found for service: {service}",
            }
        )
    
    # Format the response
    formatted_output = ["# GCP Terraform Provider Resources\n"]
    
    for svc, res_list in resources.items():
        formatted_output.append(f"## {svc.capitalize()} Resources")
        
        for res in res_list:
            formatted_output.append(f"- **{res['name']}**: {res['description']} " +
                                   f"[Documentation]({res['documentation_url']})")
            
        formatted_output.append("")  # Add a blank line between sections
    
    return MCPResponse(
        content="\n".join(formatted_output),
        metadata={
            "success": True,
            "services": list(resources.keys()),
            "resources": resources,
        }
    )


def get_resource_documentation(resource_name: str) -> MCPResponse:
    """
    Get detailed documentation for a specific GCP provider resource.
    
    Args:
        resource_name: The name of the resource (e.g. google_compute_instance)
        
    Returns:
        MCPResponse with resource documentation
    """
    logger.info(f"Getting documentation for resource: {resource_name}")
    
    # Find the resource in our documentation database
    if resource_name in RESOURCE_DOCUMENTATION:
        doc = RESOURCE_DOCUMENTATION[resource_name]
    else:
        # Check if the resource exists in our provider resources
        for service, resources in GCP_PROVIDER_RESOURCES.items():
            for resource in resources:
                if resource["name"] == resource_name:
                    return MCPResponse(
                        content=f"# {resource_name}\n\n{resource['description']}\n\n" +
                                f"For detailed documentation, visit: {resource['documentation_url']}",
                        metadata={
                            "success": True,
                            "resource": resource,
                            "note": "Limited documentation available. Follow the link for full details."
                        }
                    )
                    
        return MCPResponse(
            content=f"Resource documentation not found for: {resource_name}",
            metadata={
                "success": False,
                "error": f"Resource documentation not found for: {resource_name}",
            }
        )
    
    # Format the response
    formatted_output = [f"# {resource_name}\n"]
    formatted_output.append(f"{doc['description']}\n")
    
    # Add arguments section
    formatted_output.append("## Arguments\n")
    for arg in doc['arguments']:
        required = "Required" if arg.get('required', False) else "Optional"
        formatted_output.append(f"- **{arg['name']}** - ({required}, {arg['type']}) {arg['description']}")
    
    formatted_output.append("\n## Example Usage\n")
    formatted_output.append(f"```terraform\n{doc['example']}\n```")
    
    return MCPResponse(
        content="\n".join(formatted_output),
        metadata={
            "success": True,
            "resource": resource_name,
            "documentation": doc,
        }
    )