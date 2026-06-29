import sys
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

ENDPOINT = "https://aistudiodemo2519002580.services.ai.azure.com/api/projects/aistudiodemo2519002580-project"
AGENT_NAME = "Retail-Router-Azure-x-Snowflake"
MODEL = "gpt-4o"

question = sys.argv[1] if len(sys.argv) > 1 else "What are the top 3 regions by revenue?"

cred = DefaultAzureCredential()
with AIProjectClient(endpoint=ENDPOINT, credential=cred) as pc:
    oai = pc.get_openai_client()
    print(f"Q: {question}\n")
    resp = oai.responses.create(
        model=MODEL,
        input=question,
        extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
    )
    print("R:", resp.output_text)
    oai.close()
