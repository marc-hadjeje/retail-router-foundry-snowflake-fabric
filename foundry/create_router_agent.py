"""
create_router_agent.py
======================
Creates the orchestrator agent "Retail Router (Azure x Snowflake)" in Azure AI Foundry.

Prerequisites
-------------
- az login completed (subscription ME-MngEnvMCAP199555-marchadjeje-1)
- Python >=3.9, venv activated with: azure-ai-projects azure-ai-agents azure-identity
- The Fabric connection "fabric-retail-agent" must exist in the Foundry project
  (this script creates it if necessary via az rest)

Usage
-----
    cd "C:\\Users\\marchadjeje\\OneDrive - Microsoft\\Desktop\\demo_snow_agents\\foundry"
    .venv\\Scripts\\activate
    python create_router_agent.py

Existing resources
------------------
- AI Foundry Project : https://aistudiodemo2519002580.services.ai.azure.com/api/projects/aistudiodemo2519002580-project
- Model              : gpt-4o
- Fabric Agent       : Fabric Data Retail Agent (id=4e87c5ca-..., ws=b2a0ce4e-...)
- MCP Snowflake      : https://nfhtxdc-gg96899.snowflakecomputing.com/...
"""

import subprocess
import json
import os
import shutil
import sys

# Force UTF-8 on stdout/stderr to avoid UnicodeEncodeError on Windows console (cp1252)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    MicrosoftFabricPreviewTool,
    FabricDataAgentToolParameters,
    ToolProjectConnection,
)

# ─────────────────────────── Configuration ───────────────────────────────────

SUBSCRIPTION_ID  = "6c7d993d-259c-4e7d-942f-9c2fe086a6c7"
RESOURCE_GROUP   = "aistudio"
ACCOUNT_NAME     = "aistudiodemo2519002580"
PROJECT_NAME     = "aistudiodemo2519002580-project"
FOUNDRY_ENDPOINT = f"https://{ACCOUNT_NAME}.services.ai.azure.com/api/projects/{PROJECT_NAME}"

MODEL            = "gpt-4o"
AGENT_NAME       = "Retail-Router-Azure-x-Snowflake"
CONN_NAME        = "fabric-retail-agent"

FABRIC_WORKSPACE_ID = "b2a0ce4e-b85f-4b9e-86c6-95f57b5bac5f"
FABRIC_ARTIFACT_ID  = "4e87c5ca-9b4f-4068-baf0-9f323f46fdb7"

SNOWFLAKE_MCP_URL = (
    "https://nfhtxdc-gg96899.snowflakecomputing.com"
    "/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC"
    "/mcp-servers/retail_mcp_server"
)

# ─────────────────────────── Routing instructions ───────────────────────────

INSTRUCTIONS = """You are RETAIL ROUTER, an intelligent orchestrator for the Retail Group.

## Role
You analyze each question and route it to the appropriate specialized data tool.

## Routing Rules

### FABRIC TOOL (fabric_dataagent_preview)
AGGREGATED, STRATEGIC, KPI questions — use this tool for:
- Global revenue, by region, by product category, by customer segment
- Seasonal trends, time-based evolutions, period comparisons
- Top N regions / products / segments (rankings)
- Gross/net margins, LTV (Lifetime Value), retention rates
- Cross-region or cross-segment comparative analyses
- Any global performance indicator (KPI, dashboard)

### SNOWFLAKE MCP TOOL (snowflake_retail)
DETAILED, OPERATIONAL questions — use this tool for:
- A specific customer (by name, ID, email)
- A specific order or order line
- Named list of customers or products
- Raw transactional data, individual records
- Purchase history of a specific customer

## Behavior
1. Analyze the question: AGGREGATED → Fabric | DETAILED → Snowflake. When in doubt → Fabric.
2. Respond in English, as a senior business analyst.
3. Structure data (bullet lists, text tables).
4. Cite the source: [Fabric Data - Power BI Semantic Model] or [Snowflake Data - RETAIL_DEMO].
5. If Snowflake is unavailable (missing token), inform the user and suggest Fabric if applicable.
"""

# ─────────────────────────── Helpers ─────────────────────────────────────────

def ensure_fabric_connection() -> bool:
    """
    Creates the Fabric connection in the Foundry project if it does not yet exist.
    Returns True if OK, False otherwise.

    The connection must be of type CustomKeys with metadata.type = AzureFabric.
    This is the only format recognized by MicrosoftFabricPreviewTool.
    """
    conn_url = (
        f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}"
        f"/resourceGroups/{RESOURCE_GROUP}"
        f"/providers/Microsoft.CognitiveServices/accounts/{ACCOUNT_NAME}"
        f"/projects/{PROJECT_NAME}"
        f"/connections/{CONN_NAME}?api-version=2025-04-01-preview"
    )

    body = {
        "properties": {
            "category": "CustomKeys",
            "target": "https://fabric.microsoft.com",
            "authType": "CustomKeys",
            "credentials": {
                "keys": {
                    "workspace-id": FABRIC_WORKSPACE_ID,
                    "artifact-id":  FABRIC_ARTIFACT_ID,
                }
            },
            "metadata": {
                "type":        "AzureFabric",
                "workspaceId": FABRIC_WORKSPACE_ID,
                "artifactId":  FABRIC_ARTIFACT_ID,
            },
        }
    }

    body_file = os.path.join(os.path.dirname(__file__), "_fabric_conn_body.json")
    with open(body_file, "w", encoding="utf-8") as f:
        json.dump(body, f)

    # On Windows, "az" is a script (az.cmd) not found by CreateProcess without
    # an extension. Resolve the real path via shutil.which, with az.cmd fallback.
    az_exe = shutil.which("az") or shutil.which("az.cmd") or "az"

    try:
        result = subprocess.run(
            [
                az_exe, "rest", "--method", "PUT",
                "--url", conn_url,
                "--headers", "Content-Type=application/json",
                "--body", f"@{body_file}",
                "--output", "json",
            ],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(result.stdout)
        print(f"  ✓ Connection created/updated: {data['name']}")
        return True
    except FileNotFoundError:
        print("  ✗ 'az' (Azure CLI) not found in PATH. Install it or add it to the PATH.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Connection creation error: {e.stderr[:500]}")
        return False
    finally:
        if os.path.exists(body_file):
            os.remove(body_file)


# ─────────────────────────── Main ────────────────────────────────────────────

def main():
    print("=" * 70)
    print("Retail Router — Creating the orchestrator agent")
    print("=" * 70)

    credential = DefaultAzureCredential()

    # 1. Verify / create the Fabric connection
    print("\n[1/3] Checking the Fabric connection...")
    with AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential) as pc:
        try:
            conn = pc.connections.get(CONN_NAME)
            if conn.metadata and conn.metadata.get("type") == "AzureFabric":
                print(f"  ✓ Existing connection: {conn.name} (type={conn.type})")
            else:
                print(f"  ⚠ Connection exists but type is incorrect ({conn.type}). Recreating...")
                ensure_fabric_connection()
                conn = pc.connections.get(CONN_NAME)
        except Exception:
            print("  Connection absent, creating...")
            ok = ensure_fabric_connection()
            if not ok:
                print("  ✗ Unable to create the connection. Aborting.")
                sys.exit(1)
            conn = pc.connections.get(CONN_NAME)

    # 2. Build tools
    print("\n[2/3] Building the orchestrator agent...")

    fabric_tool = MicrosoftFabricPreviewTool(
        fabric_dataagent_preview=FabricDataAgentToolParameters(
            project_connections=[
                ToolProjectConnection(project_connection_id=conn.id)
            ]
        )
    )
    # NOTE: The Snowflake MCP tool is disabled by default (no token).
    # To enable it, run: python add_snowflake_mcp.py --token <your_PAT>
    # See README_FOUNDRY.md for details.

    # 3. Create the agent (version 1)
    with AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential) as pc:
        # Delete the old version if it exists
        try:
            pc.agents.delete_version(agent_name=AGENT_NAME, agent_version=1)
            print("  (old version deleted)")
        except Exception:
            pass

        agent = pc.agents.create_version(
            agent_name=AGENT_NAME,
            definition=PromptAgentDefinition(
                model=MODEL,
                instructions=INSTRUCTIONS,
                tools=[fabric_tool],
            ),
        )

    print(f"\n  ✓ Agent created!")
    print(f"    Agent ID   : {agent.id}")
    print(f"    Agent Name : {agent.name}")
    print(f"    Version    : {agent.version}")
    print(f"    Tools      : [fabric_dataagent_preview]")
    print(f"    Snowflake  : DISABLED (token required — see add_snowflake_mcp.py)")

    portal_url = (
        "https://ai.azure.com/agents"
        f"?wsid=/subscriptions/{SUBSCRIPTION_ID}"
        f"/resourceGroups/{RESOURCE_GROUP}"
        f"/providers/Microsoft.CognitiveServices/accounts/{ACCOUNT_NAME}"
        f"/projects/{PROJECT_NAME}"
    )
    print(f"\n  Portal URL: {portal_url}")

    print("\n[3/3] Quick routing test...")
    with AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential) as pc:
        oai = pc.get_openai_client()
        try:
            resp = oai.responses.create(
                model=MODEL,
                input="What are the top 3 regions by revenue?",
                extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
            )
            text = getattr(resp, "output_text", "")
            print(f"  ✓ Test passed! Response ({len(text)} chars):")
            safe = text.encode("ascii", "replace").decode("ascii")
            print(f"  {safe[:500]}...")
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
        finally:
            oai.close()

    print("\n" + "=" * 70)
    print("Done.")
    print("=" * 70)


if __name__ == "__main__":
    main()
