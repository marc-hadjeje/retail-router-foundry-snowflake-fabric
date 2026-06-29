# README — Retail Orchestrator Agent (Microsoft Foundry x Snowflake)

## Architecture

```
User
    |
    v
+--------------------------------------------------------------+
|   RETAIL ROUTER (Microsoft Foundry -- gpt-4o)               |
|   Agent: Retail-Router-Azure-x-Snowflake:1                  |
|   Endpoint: aistudiodemo2519002580.services.ai.azure.com    |
|                                                              |
|   Routing Rule                                               |
|   +----------------------+---------------------------+       |
|   | AGGREGATED Question  | DETAILED Question         |       |
|   | KPI, trends,         | Specific customer, order, |       |
|   | top regions, margins | individual record         |       |
|   +----------+-----------+-------------+-------------+       |
+--------------|---------------------------|--------------------|
               |                           |
               v                           v
  +---------------------------+   +-----------------------------+
  |  FABRIC DATA AGENT        |   |  SNOWFLAKE MCP              |
  |  (Power BI Semantic       |   |  FOUNDRY_RETAIL_MCP_SERVER  |
  |   Model Retail)           |   |  (Cortex Agent + SQL)       |
  |  OK ACTIVE                |   |  OK ACTIVE (auth OK)        |
  +---------------------------+   +-----------------------------+
```

---

## Status (updated on 28/06/2026)

| Component | Status | Details |
|-----------|--------|---------|
| Foundry Agent | OK | Retail-Router-Azure-x-Snowflake:1 |
| Fabric Tool | OK | Real data from Power BI Semantic Model |
| MCP Snowflake deployment | OK | FOUNDRY_RETAIL_MCP_SERVER created and accessible |
| JWT auth -> MCP | OK | Bearer JWT accepted (without KEYPAIR_JWT header) |
| Fabric routing | OK | Test B succeeded with real data |
| Snowflake routing | OK (routing) | Test A routed to Snowflake MCP |
| Snowflake data | LIMITED | Cortex Agent without active SQL tools (warehouse quota exhausted) |

---

## IDs and resources

| Resource | ID / Value |
|-----------|-------------|
| Agent ID (Foundry) | `Retail-Router-Azure-x-Snowflake:1` |
| Model | `gpt-4o` |
| Fabric Connection | `fabric-retail-agent` (CustomKeys, metadata.type=AzureFabric) |
| Fabric Workspace ID | `b2a0ce4e-b85f-4b9e-86c6-95f57b5bac5f` |
| Fabric Artifact ID | `4e87c5ca-9b4f-4068-baf0-9f323f46fdb7` |
| Snowflake Account | `QF36368` (host alias: `nfhtxdc-gg96899.snowflakecomputing.com`) |
| Snowflake User | `FOUNDRY_AGENT_SVC` (role: SYSADMIN) |
| MCP Server Snowflake | `RETAIL_DEMO.PUBLIC.FOUNDRY_RETAIL_MCP_SERVER` |
| MCP URL | `https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/FOUNDRY_RETAIL_MCP_SERVER` |
| Cortex Agent Snowflake | `RETAIL_DEMO.PUBLIC.RETAIL_MCP_SERVER` |
| Subscription | `6c7d993d-259c-4e7d-942f-9c2fe086a6c7` |
| Resource Group | `aistudio` |
| AI Services Account | `aistudiodemo2519002580` |
| Project Name | `aistudiodemo2519002580-project` |

---

## Foundry Portal URL

```
https://ai.azure.com/agents?wsid=/subscriptions/6c7d993d-259c-4e7d-942f-9c2fe086a6c7/resourceGroups/aistudio/providers/Microsoft.CognitiveServices/accounts/aistudiodemo2519002580/projects/aistudiodemo2519002580-project
```

---

## Routing test results

### Test A -- Highest-spending customer profile (-> SNOWFLAKE MCP)

**Question:** "Give me the detailed profile of the highest-spending customer, with their name and their recent orders"

**Observed behavior:** Router routes to `snowflake_retail` (MCP). Cortex Agent responds
but without concrete data (warehouse SNOWFLAKE_LEARNING_WH exhausted by resource monitor).

**Response:**
```
The highest-spending customer is being identified in the database.
I am searching for their profile, name, and the details of their
recent orders. Once I have precise details, I will share them with you.
```

**Routing status:** OK (snowflake_retail tool called)
**Data status:** LIMITED (warehouse quota exhausted, no real SQL data)

---

### Test B -- Top 3 regions by revenue (-> FABRIC)

**Question:** "What are the top 3 regions by revenue?"

**Response (real data from Power BI Semantic Model):**
```
The 3 regions with the highest revenue over the last 12 months:

1. Occitanie: 81.56 M EUR
2. Grand Est: 77.79 M EUR
3. Provence-Alpes-Cote d'Azur: 72.61 M EUR

[Source: Fabric Data - Power BI Semantic Model]
```

**Status:** OK -- real data from the Power BI Semantic Model

---

## How to provide the Snowflake token (SNOWFLAKE_JWT)

The token is a Snowflake JWT (OAuth/Session format, not standard KEYPAIR_JWT).
It is provided via environment variable so it is never written in plaintext.

```powershell
# PowerShell -- set the variable BEFORE running the script
$env:SNOWFLAKE_JWT = "eyJraWQi..."
python add_snowflake_mcp.py
```

```bash
# Bash/Linux
export SNOWFLAKE_JWT="eyJraWQi..."
python add_snowflake_mcp.py
```

**NEVER** put the token in a source-controlled file or in CLI arguments.

---

## Snowflake MCP Architecture -- Technical details

### Snowflake Hosts

| Host | Behavior |
|------|-------------|
| `QF36368.snowflakecomputing.com` | 404 for the MCP path (legacy host not supported for REST MCP) |
| `nfhtxdc-gg96899.snowflakecomputing.com` | OK -- alias for account QF36368, supports REST MCP |

`SELECT CURRENT_ACCOUNT()` on `nfhtxdc-gg96899` returns `QF36368` -- they are the same account.

### Auth

The JWT provided has the format: `{"p":"...","iss":"SF:2019","exp":...}` (no `sub` claim).

- **With** header `X-Snowflake-Authorization-Token-Type: KEYPAIR_JWT` -> 401 (missing sub claim)
- **Without** this header -> 200 (JWT valid as OAuth/Session token)
- **In Foundry**: `MCPTool.authorization = jwt` (without "Bearer") -> Foundry sends `Authorization: Bearer <jwt>`

`MCPTool.headers` is rejected by Foundry ("sensitive headers not allowed -- use project_connection_id").

### Snowflake MCP Servers

There was an existing MCP server `retail_mcp_server` but owned by a role other than SYSADMIN (inaccessible).
A new MCP server `FOUNDRY_RETAIL_MCP_SERVER` was created by SYSADMIN with:

```sql
CREATE OR REPLACE MCP SERVER FOUNDRY_RETAIL_MCP_SERVER
FROM SPECIFICATION $$
tools:
  - name: "snowflake-retail-agent"
    type: "CORTEX_AGENT_RUN"
    title: "Retail Client Advisor"
    description: "Query customers, orders, transactions in RETAIL_DEMO"
    identifier: "RETAIL_DEMO.PUBLIC.RETAIL_MCP_SERVER"
$$
```

MCP server tools (verified via tools/list):
- `snowflake-retail-agent` (CORTEX_AGENT_RUN) -- Cortex Agent

Note: The `SYSTEM_EXECUTE_SQL` type was tried but requires a warehouse (quota exhausted).

### Data available in RETAIL_DEMO.PUBLIC

| Table | Rows | Description |
|-------|--------|-------------|
| CUSTOMERS | 10,000 | Customer profiles |
| ORDERS | 50,000 | Orders |
| CATEGORIES | -- | Product categories |
| + others | -- | -- |

---

## Activation / Token renewal

When the JWT expires or needs to be changed:

```powershell
cd "C:\Users\marchadjeje\OneDrive - Microsoft\Desktop\demo_snow_agents\foundry"
.venv\Scripts\activate
$env:SNOWFLAKE_JWT = "eyJ..."   # new token
python add_snowflake_mcp.py
```

This script:
1. Retrieves the existing Fabric connection
2. Redeploys the agent with the new JWT in MCPTool.authorization
3. Runs a Snowflake routing test

---

## Current limitations

| Limitation | Cause | Solution |
|------------|-------|----------|
| No real SQL data from Snowflake | Warehouse `SNOWFLAKE_LEARNING_WH` suspended (resource monitor quota exceeded) | Reload credits or lift the quota on the `CREDIT` resource monitor |
| Cortex Agent without SQL tools | RETAIL_MCP_SERVER created without tools (only DDL without tools works outside ACCOUNTADMIN) | ALTER AGENT ... ADD TOOLS (...) with available warehouse |
| FOUNDRY_AGENT_SVC not ACCOUNTADMIN | Role limited to SYSADMIN | Grant ACCOUNTADMIN or lift warehouse quota via ACCOUNTADMIN |
| retail_mcp_server inaccessible | Owned by a different role than SYSADMIN | GRANT USAGE by ACCOUNTADMIN |

---

## Available scripts

| Script | Role |
|--------|------|
| `create_router_agent.py` | Creates the orchestrator agent with Fabric (without Snowflake) |
| `add_snowflake_mcp.py` | Adds / renews the Snowflake MCP tool (JWT via env var) |
| `activate_snowflake_mcp.py` | Full script: connectivity test + agent creation + routing tests |

---

## SDK Note -- MCPTool.authorization vs MCPTool.headers

```python
# CORRECT: authorization = JWT without "Bearer"
mcp_tool = MCPTool(
    server_label="snowflake_retail",
    server_url="https://nfhtxdc-gg96899.../mcp-servers/FOUNDRY_RETAIL_MCP_SERVER",
    authorization=jwt,  # Foundry adds "Bearer " automatically
    allowed_tools=["snowflake-retail-agent"],
    require_approval="never",
)

# INCORRECT: headers rejected by Foundry
# mcp_tool = MCPTool(..., headers={"Authorization": f"Bearer {jwt}"})
# -> HttpResponseError: "Headers that can include sensitive information are not allowed"
#    Use project_connection_id instead.
```

---

## Venv and Installation

```powershell
cd "C:\Users\marchadjeje\OneDrive - Microsoft\Desktop\demo_snow_agents\foundry"
python -m venv .venv
.venv\Scripts\activate
pip install azure-ai-projects azure-ai-agents azure-identity
```

---

## Troubleshooting

**Q: 401 on Snowflake MCP from Foundry**
-> JWT expired or MCPTool.authorization misconfigured.
   Verify that the JWT is passed without the "Bearer" prefix in MCPTool.authorization.
   Re-run add_snowflake_mcp.py with a valid JWT.

**Q: "warehouse is required" or SQL error from Snowflake**
-> The warehouse SNOWFLAKE_LEARNING_WH has exceeded its credit quota.
   Contact ACCOUNTADMIN to lift the quota on the CREDIT resource monitor.

**Q: "MCP server does not exist or not authorized"**
-> FOUNDRY_RETAIL_MCP_SERVER is not accessible. Verify with:
   SHOW MCP SERVERS IN SCHEMA RETAIL_DEMO.PUBLIC  (role SYSADMIN)
   If empty, re-run activate_snowflake_mcp.py to recreate the server.

**Q: "retail_mcp_server does not exist or not authorized"**
-> This is the old MCP server (owned by a different role). Use FOUNDRY_RETAIL_MCP_SERVER.

**Q: QF36368.snowflakecomputing.com returns 404**
-> Use nfhtxdc-gg96899.snowflakecomputing.com (alias for account QF36368 for REST MCP).

**Q: I get "mcp_list_tools.failed" in Foundry**
-> Auth failed on the MCP. Check the JWT and the server URL.

**Q: No CustomKeys connection found for AzureFabric**
-> The Fabric connection is of the wrong type. Re-run create_router_agent.py.
