# 🔗 Guide d'Utilisation MCP Server Snowflake

## 📡 **Endpoint de Votre Serveur MCP**

```
https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server
```

### **🏗️ Structure de l'URL:**

```
https://{account_URL}/api/v2/databases/{database}/schemas/{schema}/mcp-servers/{name}
```

- **account_URL**: `nfhtxdc-gg96899.snowflakecomputing.com`
- **database**: `RETAIL_DEMO`
- **schema**: `PUBLIC`  
- **name**: `retail_mcp_server`

---

## 🛠️ **Configuration pour Différents Clients MCP**

### **1. Claude Desktop (Claude.app)**

Ajouter dans `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "snowflake-retail": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-snowflake",
        "--endpoint", "https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server",
        "--account", "nfhtxdc-gg96899",
        "--role", "MCP_RETAIL_ROLE",
        "--warehouse", "COMPUTE_WH"
      ],
      "env": {
        "SNOWFLAKE_USER": "votre_utilisateur",
        "SNOWFLAKE_PASSWORD": "votre_mot_de_passe"
      }
    }
  }
}
```

### **2. Continue.dev (VS Code)**

Dans `.continue/config.json`:
```json
{
  "models": [...],
  "customCommands": [...],
  "mcpServers": [
    {
      "name": "snowflake-retail",
      "transport": {
        "type": "http",
        "url": "https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server"
      },
      "auth": {
        "type": "snowflake",
        "role": "MCP_RETAIL_ROLE",
        "warehouse": "COMPUTE_WH"
      }
    }
  ]
}
```

### **3. Python MCP Client**

```python
import asyncio
from mcp import ClientSession
from mcp.client.snowflake import SnowflakeMCPClient

async def use_snowflake_agents():
    client = SnowflakeMCPClient(
        endpoint="https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server",
        account="nfhtxdc-gg96899",
        role="MCP_RETAIL_ROLE", 
        warehouse="COMPUTE_WH"
    )
    
    # Lister les outils disponibles
    tools = await client.list_tools()
    print(f"Outils disponibles: {[t.name for t in tools]}")
    
    # Appeler l'agent retail
    result = await client.call_tool(
        "snowflake-retail-agent",
        {"question": "Analysez les ventes du Q1 2026"}
    )
    print(f"Réponse: {result}")

# Exécuter
asyncio.run(use_snowflake_agents())
```

### **4. Curl/HTTP Direct**

```bash
curl -X POST \
  https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SNOWFLAKE_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "snowflake-retail-agent",
      "arguments": {
        "question": "Quels sont nos top clients VIP ?"
      }
    }
  }'
```

---

## 🔐 **Authentification**

### **Variables d'Environnement Requises:**
```bash
SNOWFLAKE_ACCOUNT=nfhtxdc-gg96899
SNOWFLAKE_USER=votre_utilisateur
SNOWFLAKE_PASSWORD=votre_mot_de_passe
SNOWFLAKE_ROLE=MCP_RETAIL_ROLE
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

### **Permissions Snowflake:**
```sql
-- Le rôle MCP_RETAIL_ROLE doit être accordé à votre utilisateur
GRANT ROLE MCP_RETAIL_ROLE TO USER votre_utilisateur;
```

---

## 🧪 **Test de Connectivité**

### **1. Test avec Script Python:**
```bash
python test_mcp_server.py
```

### **2. Test SQL Direct:**
```sql
-- Vérifier le serveur MCP
SHOW MCP SERVERS LIKE 'retail_mcp_server';

-- Tester les outils  
SELECT SYSTEM$CALL_MCP_TOOL(
  'retail_mcp_server',
  'snowflake-retail-agent', 
  '{"question": "Test de connexion"}'
);
```

---

## 🛠️ **Outils Disponibles via MCP**

| Outil | Type | Description | Usage |
|-------|------|-------------|-------|
| `snowflake-retail-agent` | CORTEX_AGENT_RUN | Agent IA principal avec Cortex AI | Analyses complexes, recommandations |
| `retail-client-analysis` | GENERIC | Analyse clients avec IA | Segmentation, profiling clients |
| `retail-backup-agent` | GENERIC | Agent SQL de backup | Fallback si Cortex indisponible |

---

## 🎯 **Exemples d'Appels**

### **Analyse des Ventes:**
```json
{
  "name": "snowflake-retail-agent",
  "arguments": {
    "question": "Analysez les tendances de vente du Q1 2026 et donnez des recommandations"
  }
}
```

### **Segmentation Clients:**
```json
{
  "name": "retail-client-analysis", 
  "arguments": {
    "question": "Identifiez les clients VIP et proposez des stratégies de fidélisation"
  }
}
```

### **Backup Query:**
```json
{
  "name": "retail-backup-agent",
  "arguments": {
    "question": "VIP"  
  }
}
```

---

## ✅ **Votre Serveur MCP est Prêt !**

🚀 **URL Complete**: `https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server`

🔧 **Configuration**: Voir `mcp_config.json` pour les détails complets  

🧪 **Test**: Exécuter `python test_mcp_server.py` pour validation

Les modèles IA peuvent maintenant utiliser vos agents Snowflake comme outils externes ! 🎉