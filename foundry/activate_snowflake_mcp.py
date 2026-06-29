"""
activate_snowflake_mcp.py
=========================
1. Tests Snowflake MCP connectivity (KEYPAIR_JWT) on the two candidate hosts.
2. Updates the Retail Router orchestrator agent with MCPTool.
3. Runs 2 end-to-end routing tests.

Auth Foundry : MCPTool.authorization = Bearer <JWT>
   (direct headers are blocked by the platform -- see note below)

Note SDK:
   MCPTool.headers is rejected by Foundry ("sensitive headers not allowed").
   MCPTool.authorization accepts an OAuth Bearer token -- use it with the JWT.
   If Snowflake also requires X-Snowflake-Authorization-Token-Type: KEYPAIR_JWT,
   create a GenericApiKey connection and pass project_connection_id.

Usage:
    $env:SNOWFLAKE_JWT = "eyJ..."
    python activate_snowflake_mcp.py
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

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
SUBSCRIPTION_ID = "6c7d993d-259c-4e7d-942f-9c2fe086a6c7"
RESOURCE_GROUP  = "aistudio"
ACCOUNT_NAME    = "aistudiodemo2519002580"
PROJECT_NAME    = "aistudiodemo2519002580-project"

MODEL       = "gpt-4o"
AGENT_NAME  = "Retail-Router-Azure-x-Snowflake"
CONN_NAME   = "fabric-retail-agent"
SNOW_CONN   = "snowflake-mcp-jwt"   # Foundry connection for the Snowflake JWT

MCP_PATH = "/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server"
CANDIDATE_HOSTS = [
    "QF36368.snowflakecomputing.com",
    "nfhtxdc-gg96899.snowflakecomputing.com",
]
SNOWFLAKE_MCP_LABEL = "snowflake_retail"

INSTRUCTIONS = """You are RETAIL ROUTER, an intelligent orchestrator for the Retail Group.

## Role
You analyze each question and route it to the appropriate specialized data tool.

## Routing Rules

### FABRIC TOOL (fabric_dataagent_preview)
AGGREGATED, STRATEGIC, KPI questions -- use this tool for:
- Global revenue, by region, by product category, by customer segment
- Seasonal trends, time-based evolutions, period comparisons
- Top N regions / products / segments (rankings)
- Gross/net margins, LTV (Lifetime Value), retention rates
- Cross-region or cross-segment comparative analyses
- Any global performance indicator (KPI, dashboard)

### SNOWFLAKE MCP TOOL (snowflake_retail -- RETAIL_CLIENT_ADVISOR)
DETAILED, OPERATIONAL questions -- use this tool for:
- A specific customer (by name, ID, email)
- A specific order or order line
- Named list of customers or products
- Raw transactional data, individual records
- Purchase history of a specific customer

## Behavior
1. Analyze the question: AGGREGATED -> Fabric | DETAILED -> Snowflake. When in doubt -> Fabric.
2. Respond in English, as a senior business analyst.
3. Structure data (bullet lists, text tables).
4. Cite the source: [Fabric Data - Power BI Semantic Model] or [Snowflake Data - RETAIL_DEMO].
5. If Snowflake is unavailable, inform the user and suggest Fabric if applicable.
"""


# ─────────────────────────── Connectivity test ───────────────────────────────

def test_mcp_host(host: str, jwt: str) -> tuple:
    """
    Tests the Snowflake MCP endpoint with KEYPAIR_JWT.
    Returns (ok: bool, tools: list, error: str).
    """
    url = f"https://{host}{MCP_PATH}"
    base_headers = {
        "Authorization": f"Bearer {jwt}",
        "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    init_payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "foundry-test", "version": "1.0"},
        },
    }).encode("utf-8")

    tools_payload = json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {},
    }).encode("utf-8")

    print(f"\n  -> Test: {url}")
    try:
        req = urllib.request.Request(url, data=init_payload, headers=base_headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            init_status = r.status
            init_body = r.read().decode("utf-8")
        print(f"     initialize -> HTTP {init_status} | body[:100]: {init_body[:100]}")

        req2 = urllib.request.Request(url, data=tools_payload, headers=base_headers, method="POST")
        with urllib.request.urlopen(req2, timeout=20) as r2:
            tools_status = r2.status
            tools_body = r2.read().decode("utf-8")
        print(f"     tools/list -> HTTP {tools_status}")

        try:
            data = json.loads(tools_body)
            tools = []
            if "result" in data and "tools" in data["result"]:
                tools = [t.get("name") for t in data["result"]["tools"]]
            elif "error" in data:
                return False, [], f"JSON-RPC error: {data['error']}"
            print(f"     Tools: {tools}")
            return True, tools, ""
        except json.JSONDecodeError:
            # SSE stream -- try to parse the first line
            lines = [l for l in tools_body.splitlines() if l.startswith("data:")]
            if lines:
                try:
                    data = json.loads(lines[0][5:].strip())
                    tools = [t.get("name") for t in data.get("result", {}).get("tools", [])]
                    print(f"     Tools (SSE): {tools}")
                    return True, tools, ""
                except Exception:
                    pass
            print(f"     body[:200]: {tools_body[:200]}")
            return True, [], "response not JSON but HTTP OK"

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")[:500]
        except Exception:
            pass
        msg = f"HTTP {e.code} {e.reason} | {body[:250]}"
        print(f"     FAIL: {msg}")
        return False, [], msg
    except Exception as e:
        msg = str(e)[:300]
        print(f"     FAIL: {msg}")
        return False, [], msg


# ─────────────────────────── Create Snowflake connection in Foundry ──────────

def create_snowflake_connection(jwt: str) -> str | None:
    """
    Creates (or updates) a GenericApiKey connection in Foundry
    that stores the Snowflake JWT. Returns the connection ID or None.

    The connection is used as project_connection_id in MCPTool
    if MCPTool.authorization is not sufficient (the platform injects the API key
    as an Authorization header automatically).
    """
    conn_url = (
        f"https://management.azure.com/subscriptions/{SUBSCRIPTION_ID}"
        f"/resourceGroups/{RESOURCE_GROUP}"
        f"/providers/Microsoft.CognitiveServices/accounts/{ACCOUNT_NAME}"
        f"/projects/{PROJECT_NAME}"
        f"/connections/{SNOW_CONN}?api-version=2025-04-01-preview"
    )
    body = {
        "properties": {
            "category": "ApiKey",
            "target": "https://nfhtxdc-gg96899.snowflakecomputing.com",
            "authType": "ApiKey",
            "credentials": {
                "key": f"Bearer {jwt}",
            },
            "metadata": {
                "type": "SnowflakeMCP",
                "label": SNOWFLAKE_MCP_LABEL,
            },
        }
    }
    body_file = os.path.join(os.path.dirname(__file__), "_snow_conn_body.json")
    with open(body_file, "w", encoding="utf-8") as f:
        json.dump(body, f)
    try:
        result = subprocess.run(
            ["az", "rest", "--method", "PUT", "--url", conn_url,
             "--headers", "Content-Type=application/json",
             "--body", f"@{body_file}", "--output", "json"],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(result.stdout)
        conn_id = data.get("id", "")
        print(f"  OK Snowflake connection created: {data.get('name')} (id={conn_id[:60]}...)")
        return conn_id
    except subprocess.CalledProcessError as e:
        print(f"  WARN Snowflake connection not created: {e.stderr[:300]}")
        return None
    finally:
        if os.path.exists(body_file):
            os.remove(body_file)


# ─────────────────────────── Main ────────────────────────────────────────────

def main():
    jwt = os.environ.get("SNOWFLAKE_JWT", "").strip()
    if not jwt:
        print("FAIL: SNOWFLAKE_JWT environment variable is missing.")
        sys.exit(1)

    print("=" * 70)
    print("Snowflake MCP Activation -- Retail Router (Microsoft Foundry)")
    print("=" * 70)
    print(f"  JWT: {jwt[:20]}... (masked)")

    # ── 1. MCP connectivity ───────────────────────────────────────────────────
    print("\n[1/4] Testing Snowflake MCP connectivity...")
    working_host = None
    discovered_tools = []

    for host in CANDIDATE_HOSTS:
        ok, tools, err = test_mcp_host(host, jwt)
        if ok:
            working_host = host
            discovered_tools = tools
            print(f"\n  OK Operational host: {host}")
            break
        else:
            print(f"  FAIL {host}: {err[:120]}")

    if not working_host:
        print("\n  WARN No host responded -- JWT invalid or MCP server absent.")
        print("  -> Continuing with nfhtxdc-gg96899 (reference in the repo).")
        working_host = CANDIDATE_HOSTS[1]

    mcp_url = f"https://{working_host}{MCP_PATH}"
    print(f"\n  MCP URL: {mcp_url}")
    print(f"  Discovered tools: {discovered_tools or '(not available outside Foundry)'}")

    # ── 2. Snowflake connection in Foundry ────────────────────────────────────
    print("\n[2/4] Creating Snowflake connection in Foundry...")
    snow_conn_id = create_snowflake_connection(jwt)

    # ── 3. Update the agent ───────────────────────────────────────────────────
    print("\n[3/4] Updating the orchestrator agent...")
    credential = DefaultAzureCredential()

    with AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential) as pc:
        conn = pc.connections.get(CONN_NAME)
        print(f"  OK Fabric Connection: {conn.name}")

        fabric_tool = MicrosoftFabricPreviewTool(
            fabric_dataagent_preview=FabricDataAgentToolParameters(
                project_connections=[ToolProjectConnection(project_connection_id=conn.id)]
            )
        )

        # MCP auth strategy:
        # 1. MCPTool.authorization = Bearer JWT (OAuth field of the API)
        # 2. Fallback: project_connection_id if the connection was created
        mcp_kwargs = dict(
            server_label=SNOWFLAKE_MCP_LABEL,
            server_url=mcp_url,
            server_description=(
                "Snowflake Retail Demo -- detailed customer data, orders, "
                "transactions. Cortex Agent RETAIL_CLIENT_ADVISOR in RETAIL_DEMO.PUBLIC."
            ),
            require_approval="never",
        )

        # Attempt 1: authorization field (Bearer JWT)
        mcp_kwargs_v1 = dict(mcp_kwargs)
        mcp_kwargs_v1["authorization"] = f"Bearer {jwt}"
        if discovered_tools:
            mcp_kwargs_v1["allowed_tools"] = discovered_tools

        # Attempt 2: project_connection_id
        mcp_kwargs_v2 = dict(mcp_kwargs)
        if snow_conn_id:
            mcp_kwargs_v2["project_connection_id"] = snow_conn_id
        if discovered_tools:
            mcp_kwargs_v2["allowed_tools"] = discovered_tools

        # Try v1 (authorization), then v2 (project_connection_id), then without auth
        agent = None
        for attempt_label, kwargs in [
            ("authorization=Bearer JWT", mcp_kwargs_v1),
            ("project_connection_id", mcp_kwargs_v2 if snow_conn_id else None),
            ("no auth (debug)", mcp_kwargs),
        ]:
            if kwargs is None:
                continue
            try:
                mcp_tool = MCPTool(**kwargs)

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
                print(f"  OK Agent created with strategy: [{attempt_label}]")
                break
            except Exception as e:
                print(f"  FAIL strategy [{attempt_label}]: {str(e)[:300]}")

        if agent is None:
            print("  FAIL Unable to create agent with MCP. Aborting.")
            sys.exit(1)

    print(f"\n  Agent ID: {agent.id}")
    print(f"  Tools   : [fabric_dataagent_preview, mcp(snowflake_retail)]")

    # ── 4. Routing tests ──────────────────────────────────────────────────────
    print("\n[4/4] End-to-end routing tests...")

    tests = [
        {
            "label": "TEST A -- Highest-spending customer (-> SNOWFLAKE expected)",
            "question": (
                "Give me the detailed profile of the highest-spending customer, "
                "with their name and their recent orders"
            ),
        },
        {
            "label": "TEST B -- Top 3 regions by revenue (-> FABRIC expected)",
            "question": "What are the top 3 regions by revenue?",
        },
    ]

    results = {}
    with AIProjectClient(endpoint=FOUNDRY_ENDPOINT, credential=credential) as pc:
        oai = pc.get_openai_client()
        try:
            for t in tests:
                print(f"\n  +-- {t['label']}")
                print(f"  |   Q: {t['question']}")
                try:
                    resp = oai.responses.create(
                        model=MODEL,
                        input=t["question"],
                        extra_body={
                            "agent_reference": {
                                "name": AGENT_NAME,
                                "type": "agent_reference",
                            }
                        },
                    )
                    text = getattr(resp, "output_text", str(resp))
                    safe = text.encode("ascii", "replace").decode("ascii")
                    print(f"  |   R ({len(text)} chars): {safe[:700]}")
                    results[t["label"]] = {"status": "OK", "response": text}
                except Exception as e:
                    err = str(e)
                    print(f"  |   FAIL: {err[:500]}")
                    results[t["label"]] = {"status": "ERROR", "response": err}
        finally:
            oai.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"  MCP host          : {working_host}")
    print(f"  MCP URL           : {mcp_url}")
    print(f"  MCP tools         : {discovered_tools or '(not discovered outside Foundry)'}")
    print(f"  Agent             : {agent.id if agent else 'FAILED'}")
    for lbl, res in results.items():
        icon = "OK" if res["status"] == "OK" else "FAIL"
        print(f"  [{icon}] {lbl}")

    return working_host, discovered_tools, results


if __name__ == "__main__":
    main()

