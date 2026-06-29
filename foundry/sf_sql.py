import json, urllib.request, urllib.error, sys, time, os

HOST = "nfhtxdc-gg96899.snowflakecomputing.com"
JWT = os.environ.get("SNOWFLAKE_JWT", "").strip()
if not JWT:
    sys.exit("Missing SNOWFLAKE_JWT environment variable. Set it before running this script.")

def run_sql(stmt, wh="SNOWFLAKE_LEARNING_WH"):
    url = f"https://{HOST}/api/v2/statements"
    body = json.dumps({
        "statement": stmt, "timeout": 60, "role": "SYSADMIN",
        "warehouse": wh, "database": "RETAIL_DEMO", "schema": "PUBLIC",
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {JWT}",
        "Content-Type": "application/json", "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=70) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:1000]

for stmt in sys.argv[1:]:
    print(f"\n### {stmt}")
    status, data = run_sql(stmt)
    print(f"HTTP {status}")
    if isinstance(data, dict):
        rows = data.get("data", [])
        cols = [c["name"] for c in data.get("resultSetMetaData", {}).get("rowType", [])]
        print("COLS:", cols)
        for row in rows[:50]:
            print(row)
    else:
        print(data)
