FROM python:3.10-slim

WORKDIR /app

# Install Terraform and other dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN curl -fsSL https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip -o terraform.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform.zip

# Install Checkov
RUN pip install --no-cache-dir checkov

# Copy and install the application
COPY . /app/
RUN pip install --no-cache-dir -e .

# Expose the port
EXPOSE 8080

# Run the MCP server
CMD ["uvicorn", "gcp_terraform_mcp_server.main:app", "--host", "0.0.0.0", "--port", "8080"]