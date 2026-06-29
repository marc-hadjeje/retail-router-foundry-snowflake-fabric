"""
add_snowflake_mcp.py
====================
Adds (or renews) the Snowflake MCP tool to the Retail Router orchestrator agent.

Prerequisites
-------------
- The "Retail-Router-Azure-x-Snowflake" agent must already exist (via create_router_agent.py)
- The FOUNDRY_RETAIL_MCP_SERVER MCP server must be deployed in Snowflake
  (created by activate_snowflake_mcp.py -- CREATE MCP SERVER FROM SPECIFICATION)
- The Snowflake JWT must be provided via the SNOWFLAKE_JWT environment variable

Usage
-----
    cd "C:\\Users\\marchadjeje\\OneDrive - Microsoft\\Desktop\\demo_snow_agents\\foundry"
    .venv\\Scripts\\activate

    # REQUIRED: pass the JWT via environment variable (never in plaintext)
    $env:SNOWFLAKE_JWT = "eyJ..."
    python add_snowflake_mcp.py

Snowflake MCP Architecture
--------------------------
Host     : nfhtxdc-gg96899.snowflakecomputing.com (alias for account QF36368)
           QF36368.snowflakecomputing.com returns 404 for the MCP path
Server   : RETAIL_DEMO.PUBLIC.FOUNDRY_RETAIL_MCP_SERVER (owner: SYSADMIN)
           Note: retail_mcp_server already existed but is owned by a different role
Tools MCP: snowflake-retail-agent (type: CORTEX_AGENT_RUN -> RETAIL_DEMO.PUBLIC.RETAIL_MCP_SERVER)

Snowflake MCP Auth
------------------
MCPTool.authorization = <JWT_TOKEN> (without "Bearer" prefix)
Foundry automatically prepends "Bearer " before the token when calling MCP.
Header sent: Authorization: Bearer <JWT>
The JWT is of type Snowflake OAuth/Session (not standard KEYPAIR_JWT).

IMPORTANT: Never commit this token to Git.
"""

import os
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
    MCPTool,
)

# ─────────────────────────── Configuration ───────────────────────────────────

FOUNDRY_ENDPOINT = (
    "https://aistudiodemo2519002580.services.ai.azure.com"
    "/api/projects/aistudiodemo2519002580-project"
)
MODEL       = "gpt-4o"
AGENT_NAME  = "Retail-Router-Azure-x-Snowflake"
CONN_NAME   = "fabric-retail-agent"

SNOWFLAKE_MCP_URL = (
    "https://nfhtxdc-gg96899.snowflakecomputing.com"
    "/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC"
    "/mcp-servers/FOUNDRY_RETAIL_MCP_SERVER"
)
SNOWFLAKE_MCP_LABEL         = "snowflake_retail"
SNOWFLAKE_MCP_ALLOWED_TOOLS = ["snowflake-retail-agent"]

INSTRUCTIONS = """You are RETAIL ROUTER, an intelligent orchestrator for the Retail Group.

## Role
You analyze each question and route it to the appropriate specialized data tool.

## Routing Rules

### FABRIC TOOL (fabric_dataagent_preview)
AGGREGATED, STRATEGIC, KPI questions:
- Global revenue, by region, by product category, by customer segment
- Seasonal trends, time-based evolutions, period comparisons
- Top N regions / products / segments (rankings)
- Gross/net margins, LTV (Lifetime Value), retention rates
- Cross-region or cross-segment comparative analyses
- Any global performance indicator (KPI, dashboard)

### SNOWFLAKE MCP TOOL (snowflake_retail -- RETAIL_CLIENT_ADVISOR)
DETAILED, OPERATIONAL questions:
- A specific customer (by name, ID, email)
- A specific order or order line
- Named list of customers or products
- Raw transactional data, individual records
- Purchase history of a specific customer

## Behavior
1. Analyze the question: AGGREGATED -> Fabric | DETAILED -> Snowflake. When in doubt -> Fabric.
2. Call ONLY ONE tool by default. Call BOTH tools only if the question
   explicitly combines a DETAILED need (a specific customer/order) AND an
   AGGREGATED need (KPI, region, segment). Never cross-reference sources "to verify".
3. Respond in English, as a senior business analyst.
4. Structure data (bullet lists, text tables).
5. Cite the source: [Fabric Data - Power BI Semantic Model] or [Snowflake Data - RETAIL_DEMO].
6. If Snowflake returns an error (warehouse quota exhausted), inform the user and suggest Fabric.
"""


# ─────────────────────────── Main ────────────────────────────────────────────

def main():
    jwt = os.environ.get("SNOWFLAKE_JWT", "").strip()
    if not jwt:
        print("FAIL: SNOWFLAKE_JWT environment variable is missing.")
        print("  Set it before running this script:")
        print('  $env:SNOWFLAKE_JWT = "eyJ..."')
        sys.exit(1)

    print("=" * 70)
    print("Adding Snowflake MCP to the Retail Router agent")
    print("=" * 70)
    print(f"  Snowflake MCP URL : {SNOWFLAKE_MCP_URL}")
    print(f"  JWT provided      : {jwt[:20]}... (masked)")

    credential = DefaultAzureCredential()

    with AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential) as pc:
        conn = pc.connections.get(CONN_NAME)
        print(f"\n  OK Fabric Connection: {conn.name}")

        fabric_tool = MicrosoftFabricPreviewTool(
            fabric_dataagent_preview=FabricDataAgentToolParameters(
                project_connections=[
                    ToolProjectConnection(project_connection_id=conn.id)
                ]
            )
        )

        # MCPTool.authorization = JWT without "Bearer" prefix
        # Foundry adds "Bearer " automatically.
        # MCPTool.headers is rejected by Foundry ("sensitive headers not allowed").
        mcp_tool = MCPTool(
            server_label=SNOWFLAKE_MCP_LABEL,
            server_url=SNOWFLAKE_MCP_URL,
            server_description=(
                "Snowflake Retail Demo -- customer details, orders, transactions. "
                "Cortex Agent RETAIL_MCP_SERVER in RETAIL_DEMO.PUBLIC."
            ),
            authorization=jwt,  # JWT without "Bearer" -- Foundry adds it
            allowed_tools=SNOWFLAKE_MCP_ALLOWED_TOOLS,
            require_approval="never",
        )

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
                tools=[fabric_tool, mcp_tool],
            ),
        )

    print(f"\n  OK Agent updated: {agent.id}")
    print(f"     Tools: [fabric_dataagent_preview, mcp(snowflake_retail)]")
    print(f"     Snowflake MCP tools: {SNOWFLAKE_MCP_ALLOWED_TOOLS}")

    print("\n  Snowflake routing test:")
    with AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential) as pc:
        oai = pc.get_openai_client()
        try:
            resp = oai.responses.create(
                model=MODEL,
                input="Give me the detailed profile of the highest-spending customer.",
                extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
            )
            text = getattr(resp, "output_text", "")
            safe = text.encode("ascii", "replace").decode("ascii")
            print(f"  Response: {safe[:500]}")
        except Exception as e:
            print(f"  FAIL Snowflake test: {e}")
            print("  -> Check that the JWT is valid and FOUNDRY_RETAIL_MCP_SERVER is deployed")
        finally:
            oai.close()

    print("\n" + "=" * 70)
    print("Done.")
    print("=" * 70)


if __name__ == "__main__":
    main()
