"""
Handlers for GCP best practices and security recommendations.
"""
import logging
from typing import Any, Dict, List, Optional

from gcp_terraform_mcp_server.models import MCPResponse

logger = logging.getLogger(__name__)

# GCP Terraform best practices database
GCP_BEST_PRACTICES = [
    {
        "category": "Networking",
        "title": "Use VPC Flow Logs for network monitoring and security",
        "description": "Enable VPC Flow Logs to monitor and analyze network traffic within your VPC networks.",
        "terraform_example": """
resource "google_compute_subnetwork" "subnet" {
  name          = "my-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = "us-central1"
  network       = google_compute_network.vpc.id
  
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}
""",
        "documentation_url": "https://cloud.google.com/vpc/docs/using-flow-logs"
    },
    {
        "category": "Security",
        "title": "Enable Cloud Armor for web application protection",
        "description": "Use Cloud Armor to protect your applications from DDoS attacks and web-based attacks.",
        "terraform_example": """
resource "google_compute_security_policy" "policy" {
  name = "my-security-policy"
  
  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "XSS attack filtering"
  }
  
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default rule"
  }
}
""",
        "documentation_url": "https://cloud.google.com/armor/docs/cloud-armor-overview"
    },
    {
        "category": "IAM",
        "title": "Use custom IAM roles for least privilege access",
        "description": "Create custom IAM roles to follow the principle of least privilege.",
        "terraform_example": """
resource "google_project_iam_custom_role" "my_custom_role" {
  role_id     = "myCustomRole"
  title       = "My Custom Role"
  description = "A custom role with minimal permissions"
  permissions = [
    "compute.instances.get",
    "compute.instances.list",
  ]
}
""",
        "documentation_url": "https://cloud.google.com/iam/docs/creating-custom-roles"
    },
    {
        "category": "Storage",
        "title": "Enable versioning for Cloud Storage buckets",
        "description": "Enable versioning for Cloud Storage buckets to protect against accidental deletion and modifications.",
        "terraform_example": """
resource "google_storage_bucket" "static_website" {
  name          = "my-static-website"
  location      = "US"
  force_destroy = true
  
  versioning {
    enabled = true
  }
}
""",
        "documentation_url": "https://cloud.google.com/storage/docs/object-versioning"
    },
    {
        "category": "Compute",
        "title": "Use Shielded VMs for enhanced security",
        "description": "Shielded VMs offer verifiable integrity of your VM instances to protect against rootkits and bootkits.",
        "terraform_example": """
resource "google_compute_instance" "default" {
  name         = "shielded-vm"
  machine_type = "e2-medium"
  zone         = "us-central1-a"
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }
  
  network_interface {
    network = "default"
  }
  
  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }
}
""",
        "documentation_url": "https://cloud.google.com/compute/shielded-vm/docs/shielded-vm"
    },
]

# Security recommendations database
SECURITY_RECOMMENDATIONS = [
    {
        "id": "SEC-GCP-001",
        "title": "Enable VPC Service Controls",
        "description": "Use VPC Service Controls to define security perimeters for sensitive GCP services and data.",
        "impact": "HIGH",
        "terraform_example": """
resource "google_access_context_manager_service_perimeter" "service_perimeter" {
  provider   = google-beta
  name       = "accessPolicies/${google_access_context_manager_access_policy.access_policy.name}/servicePerimeters/restrict_services"
  title      = "restrict_services"
  perimeter_type = "PERIMETER_TYPE_REGULAR"
  
  status {
    restricted_services = [
      "bigquery.googleapis.com",
      "storage.googleapis.com",
    ]
    
    vpc_accessible_services {
      enable_restriction = true
      allowed_services   = ["RESTRICTED-SERVICES"]
    }
    
    access_levels = [
      google_access_context_manager_access_level.access_level.name
    ]
  }
}
""",
        "remediation": "Define VPC Service Controls to create a security perimeter around your sensitive GCP services.",
        "compliance": ["NIST SP 800-53", "CIS GCP Foundation"]
    },
    {
        "id": "SEC-GCP-002",
        "title": "Enable organization-level audit logging",
        "description": "Configure organization-level audit logging to track all administrative activities.",
        "impact": "MEDIUM",
        "terraform_example": """
resource "google_organization_iam_audit_config" "org_audit" {
  org_id  = "your-organization-id"
  service = "allServices"
  
  audit_log_config {
    log_type = "ADMIN_READ"
  }
  
  audit_log_config {
    log_type = "DATA_WRITE"
  }
  
  audit_log_config {
    log_type = "DATA_READ"
  }
}
""",
        "remediation": "Enable organization-level audit logging for comprehensive visibility into administrative actions.",
        "compliance": ["NIST SP 800-53", "SOC 2", "PCI DSS"]
    },
    {
        "id": "SEC-GCP-003",
        "title": "Use Customer-Managed Encryption Keys (CMEK)",
        "description": "Use Customer-Managed Encryption Keys for enhanced control over data encryption.",
        "impact": "MEDIUM",
        "terraform_example": """
resource "google_kms_key_ring" "keyring" {
  name     = "keyring-name"
  location = "global"
}

resource "google_kms_crypto_key" "key" {
  name            = "crypto-key-name"
  key_ring        = google_kms_key_ring.keyring.id
  rotation_period = "7776000s" # 90 days
}

resource "google_storage_bucket" "cmek_bucket" {
  name          = "cmek-bucket"
  location      = "US"
  force_destroy = true
  
  encryption {
    default_kms_key_name = google_kms_crypto_key.key.id
  }
}
""",
        "remediation": "Set up Customer-Managed Encryption Keys (CMEK) and configure GCP resources to use them.",
        "compliance": ["NIST SP 800-53", "HIPAA", "PCI DSS"]
    },
    {
        "id": "SEC-GCP-004",
        "title": "Configure Binary Authorization for GKE",
        "description": "Use Binary Authorization to ensure only trusted container images are deployed on your GKE clusters.",
        "impact": "HIGH",
        "terraform_example": """
resource "google_binary_authorization_policy" "policy" {
  admission_whitelist_patterns {
    name_pattern = "gcr.io/google_containers/*"
  }
  
  admission_whitelist_patterns {
    name_pattern = "gcr.io/$PROJECT_ID/*"
  }
  
  default_admission_rule {
    evaluation_mode  = "ALWAYS_ALLOW"
    enforcement_mode = "ENFORCED_BLOCK_AND_AUDIT_LOG"
  }
}

resource "google_container_cluster" "primary" {
  name     = "my-gke-cluster"
  location = "us-central1"
  
  # Enable Binary Authorization
  enable_binary_authorization = true
}
""",
        "remediation": "Enable Binary Authorization for your GKE clusters to ensure only approved images are deployed.",
        "compliance": ["NIST SP 800-53", "CIS GCP Foundation"]
    },
    {
        "id": "SEC-GCP-005",
        "title": "Enable OS Login for VM instances",
        "description": "Use OS Login to manage SSH access to your instances using IAM permissions.",
        "impact": "MEDIUM",
        "terraform_example": """
resource "google_compute_project_metadata" "default" {
  metadata = {
    enable-oslogin = "TRUE"
  }
}

resource "google_compute_instance" "default" {
  name         = "secure-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"
  
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }
  
  network_interface {
    network = "default"
  }
  
  metadata = {
    enable-oslogin = "TRUE"
  }
}
""",
        "remediation": "Enable OS Login at the project level or instance level to manage SSH access via IAM.",
        "compliance": ["NIST SP 800-53", "CIS GCP Foundation"]
    }
]


def get_best_practices(category: Optional[str] = None) -> MCPResponse:
    """
    Get GCP best practices for Terraform.
    
    Args:
        category: Optional category filter
        
    Returns:
        MCPResponse with best practices
    """
    logger.info(f"Getting GCP best practices for category: {category}")
    
    # Filter practices by category if provided
    if category:
        practices = [p for p in GCP_BEST_PRACTICES if p["category"].lower() == category.lower()]
    else:
        practices = GCP_BEST_PRACTICES
        
    if not practices:
        return MCPResponse(
            content=f"No best practices found for category: {category}",
            metadata={
                "success": False,
                "error": f"No best practices found for category: {category}",
            }
        )
        
    # Format the response
    formatted_output = ["# GCP Terraform Best Practices\n"]
    
    for practice in practices:
        formatted_output.append(f"## {practice['title']}")
        formatted_output.append(f"{practice['description']}\n")
        formatted_output.append("### Terraform Example")
        formatted_output.append(f"```terraform\n{practice['terraform_example']}\n```\n")
        formatted_output.append(f"**Documentation:** [{practice['category']} Documentation]({practice['documentation_url']})\n")
        
    return MCPResponse(
        content="\n".join(formatted_output),
        metadata={
            "success": True,
            "count": len(practices),
            "practices": practices,
        }
    )


def get_security_recommendations(impact: Optional[str] = None) -> MCPResponse:
    """
    Get GCP security recommendations for Terraform.
    
    Args:
        impact: Optional impact filter (HIGH, MEDIUM, LOW)
        
    Returns:
        MCPResponse with security recommendations
    """
    logger.info(f"Getting GCP security recommendations with impact: {impact}")
    
    # Filter recommendations by impact if provided
    if impact:
        recommendations = [r for r in SECURITY_RECOMMENDATIONS if r["impact"].upper() == impact.upper()]
    else:
        recommendations = SECURITY_RECOMMENDATIONS
        
    if not recommendations:
        return MCPResponse(
            content=f"No security recommendations found for impact level: {impact}",
            metadata={
                "success": False,
                "error": f"No security recommendations found for impact level: {impact}",
            }
        )
        
    # Format the response
    formatted_output = ["# GCP Security Recommendations\n"]
    
    for rec in recommendations:
        formatted_output.append(f"## {rec['id']}: {rec['title']}")
        formatted_output.append(f"**Impact: {rec['impact']}**\n")
        formatted_output.append(f"{rec['description']}\n")
        formatted_output.append("### Terraform Example")
        formatted_output.append(f"```terraform\n{rec['terraform_example']}\n```\n")
        formatted_output.append("### Remediation")
        formatted_output.append(f"{rec['remediation']}\n")
        formatted_output.append("### Compliance")
        formatted_output.append(", ".join(rec["compliance"]) + "\n")
        
    return MCPResponse(
        content="\n".join(formatted_output),
        metadata={
            "success": True,
            "count": len(recommendations),
            "recommendations": recommendations,
        }
    )