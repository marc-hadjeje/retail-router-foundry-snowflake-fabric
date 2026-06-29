import json, urllib.request, urllib.error, sys, os

HOST = "nfhtxdc-gg96899.snowflakecomputing.com"
JWT = os.environ.get("SNOWFLAKE_JWT", "").strip()
if not JWT:
    sys.exit("Missing SNOWFLAKE_JWT environment variable. Set it before running this script.")

def run_sql(stmt, wh="RETAIL_COMPUTE_WH"):
    url = f"https://{HOST}/api/v2/statements"
    body = json.dumps({
        "statement": stmt, "timeout": 120, "role": "SYSADMIN",
        "warehouse": wh, "database": "RETAIL_DEMO", "schema": "PUBLIC",
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {JWT}",
        "Content-Type": "application/json", "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=130) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:1500]

SPEC = r"""CREATE OR REPLACE AGENT RETAIL_DEMO.PUBLIC.RETAIL_MCP_SERVER
WITH PROFILE='{"display_name":"Retail Client Advisor"}'
COMMENT='Retail Demo MCP Agent - detailed data RETAIL_DEMO.PUBLIC'
FROM SPECIFICATION $$
models:
  orchestration: auto
instructions:
  response: |
    You are an expert retail customer advisor. ALWAYS respond in English,
    with a senior business analyst tone. Structure your responses (bullet lists,
    precise figures). Cite the source: [Snowflake Data - RETAIL_DEMO].
  orchestration: |
    For ALL questions about customers, orders, products, stores or sales,
    use EXCLUSIVELY the 'retail_analyst' tool which queries the semantic view
    RETAIL_DEMO.PUBLIC.RETAIL_SEMANTIC.
  system: |
    The data covers a retail business (RETAIL_DEMO):
    10,000 customers, 50,000 orders, 325,800 lines, 2,000 products, 100 stores.
    Tables: CUSTOMERS, ORDERS, ORDER_ITEMS, PRODUCTS, CATEGORIES, STORES.
    Total spent per customer = SUM(ORDERS.TOTAL_AMOUNT).
    ABSOLUTE PROHIBITION on using SNOWFLAKE_SAMPLE_DATA or TPCH:
    all data is in RETAIL_DEMO.PUBLIC via the semantic view.
tools:
  - tool_spec:
      type: cortex_analyst_text_to_sql
      name: retail_analyst
      description: "Detailed analysis of customers, orders, products, stores and sales in the Retail Demo. Generates SQL on RETAIL_DEMO.PUBLIC."
tool_resources:
  retail_analyst:
    semantic_view: RETAIL_DEMO.PUBLIC.RETAIL_SEMANTIC
    execution_environment:
      type: warehouse
      warehouse: RETAIL_COMPUTE_WH
      query_timeout: 90
$$;"""

print("Creating Cortex Agent RETAIL_MCP_SERVER bound to RETAIL_SEMANTIC...")
status, data = run_sql(SPEC)
print(f"HTTP {status}")
print(json.dumps(data, indent=2)[:1200] if isinstance(data, dict) else data)
