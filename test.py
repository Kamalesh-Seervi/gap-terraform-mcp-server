from fastmcp import Client

# point at your SSE endpoint
client = Client("http://127.0.0.1:8080/mcp/sse")

# invoke a tool
resp = client.request("terraform://workflow_guide")
print(resp["result"]["content"])