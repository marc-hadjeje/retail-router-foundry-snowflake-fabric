# 🔗 Guide de Partage Agent Snowflake
## Intégration avec Microsoft Foundry et autres plateformes

## 🎯 Options de Partage Disponibles

### **1. 🌉 Microsoft Foundry Agent Framework (RECOMMANDÉ)**
Intégration native avec l'écosystème Microsoft Foundry pour des agents d'entreprise.

#### **Avantages Foundry :**
- ✅ **Déploiement cloud** géré par Microsoft
- ✅ **Monitoring et observabilité** intégrés
- ✅ **Sécurité entreprise** (Azure AD, RBAC)
- ✅ **Scaling automatique** selon la demande
- ✅ **Intégration Microsoft 365** (Teams, Outlook)

#### **Configuration Foundry :**
```yaml
# agent.yaml pour Foundry
name: snowflake-retail-advisor
version: "1.0.0"
description: "Agent IA retail basé sur Snowflake Cortex"

connections:
  snowflake:
    type: snowflake
    account: ${SNOWFLAKE_ACCOUNT}
    database: RETAIL_DEMO
    role: FOUNDRY_AGENT_ROLE

tools:
  - name: retail_analysis
    type: snowflake_function
    function: WEB_AGENT_IA_CLIENTS
    description: "Analyse intelligente clients retail"

deployment:
  type: foundry_managed
  scaling: auto
  monitoring: enabled
```

#### **Code d'intégration Foundry :**
```python
# foundry_agent.py
from foundry_agent_framework import Agent, SnowflakeConnector

class RetailAdvisorAgent(Agent):
    def __init__(self):
        self.snowflake = SnowflakeConnector(
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            role='FOUNDRY_AGENT_ROLE'
        )
    
    async def process_message(self, message: str, context: dict):
        """Traiter les questions business retail"""
        result = await self.snowflake.call_function(
            'WEB_AGENT_IA_CLIENTS',
            [message]
        )
        return self.format_response(result)
```

---

### **2. 📱 API REST (Intégration Applications)**
Exposition via API Snowflake pour intégrations custom.

#### **Endpoint disponible :**
```http
POST https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/statements
Authorization: Bearer {snowflake_token}
Content-Type: application/json

{
  "statement": "SELECT WEB_AGENT_IA_CLIENTS('Analyse mes clients VIP')",
  "warehouse": "COMPUTE_WH",
  "database": "RETAIL_DEMO"
}
```

#### **Client Python exemple :**
```python
import requests
import json

class SnowflakeAgentClient:
    def __init__(self, account, token):
        self.base_url = f"https://{account}.snowflakecomputing.com/api/v2"
        self.token = token
    
    def ask_agent(self, question: str):
        response = requests.post(
            f"{self.base_url}/statements",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json={
                "statement": f"SELECT WEB_AGENT_IA_CLIENTS('{question}')",
                "warehouse": "COMPUTE_WH"
            }
        )
        return response.json()

# Usage
client = SnowflakeAgentClient("nfhtxdc-gg96899", "your-token")
result = client.ask_agent("Stratégie fidélisation VIP")
```

---

### **3. 🤖 Microsoft Teams Integration**
Bot Teams connecté à l'agent Snowflake.

#### **Bot Framework setup :**
```python
# teams_bot.py
from botbuilder.core import ActivityHandler, MessageFactory
from snowflake_agent_client import SnowflakeAgentClient

class RetailAdvisorBot(ActivityHandler):
    def __init__(self):
        self.agent_client = SnowflakeAgentClient()
    
    async def on_message_activity(self, turn_context):
        user_message = turn_context.activity.text
        
        # Appel à l'agent Snowflake
        agent_response = await self.agent_client.ask_agent(user_message)
        
        # Formatage pour Teams
        response_text = self.format_teams_response(agent_response)
        await turn_context.send_activity(
            MessageFactory.text(response_text)
        )
```

---

### **4. 🌐 Power Platform (Power Apps + Power Automate)**
Intégration avec l'écosystème Microsoft Power Platform.

#### **Power Automate Flow :**
```json
{
  "definition": {
    "triggers": {
      "manual": {
        "type": "Request",
        "inputs": {
          "schema": {
            "properties": {
              "question": {"type": "string"}
            }
          }
        }
      }
    },
    "actions": {
      "call_snowflake_agent": {
        "type": "Http",
        "inputs": {
          "method": "POST",
          "uri": "https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/statements",
          "headers": {
            "Authorization": "Bearer @{parameters('snowflake_token')}"
          },
          "body": {
            "statement": "SELECT WEB_AGENT_IA_CLIENTS('@{triggerBody()['question']}')"
          }
        }
      }
    }
  }
}
```

---

### **5. 📊 Power BI Custom Connector**
Agent accessible directement depuis Power BI.

#### **Connecteur M (Power Query) :**
```m
// SnowflakeAgent.pq
let
    CallSnowflakeAgent = (question as text) =>
    let
        Source = Snowflake.Databases("nfhtxdc-gg96899", "RETAIL_DEMO"),
        PublicSchema = Source{[Name="PUBLIC"]}[Data],
        AgentFunction = PublicSchema{[Name="WEB_AGENT_IA_CLIENTS",Kind="Function"]}[Data],
        Result = AgentFunction(question)
    in
        Result
in
    CallSnowflakeAgent
```

---

### **6. 🔄 Webhook Integration (Real-time)**
Notifications temps réel via webhooks.

#### **Webhook endpoint :**
```python
from flask import Flask, request, jsonify
from snowflake_agent_client import SnowflakeAgentClient

app = Flask(__name__)
agent = SnowflakeAgentClient()

@app.route('/webhook/retail-question', methods=['POST'])
def process_retail_question():
    data = request.json
    question = data.get('question')
    
    # Appel agent Snowflake
    result = agent.ask_agent(question)
    
    # Réponse webhook
    return jsonify({
        'status': 'success',
        'question': question,
        'agent_response': result,
        'timestamp': datetime.utcnow().isoformat()
    })
```

---

## 🚀 Déploiement Recommandé pour Foundry

### **Étape 1 : Préparer l'intégration**
```bash
# Exécuter le script d'intégration Foundry
# Dans Snowflake, exécuter :
snowflake/21_foundry_integration.sql
```

### **Étape 2 : Configuration Foundry Project**
```yaml
# foundry-project.yaml
project:
  name: retail-analytics-agents
  description: "Agents IA pour analytics retail"
  
agents:
  - name: snowflake-retail-advisor
    source: snowflake
    config_file: agent.yaml
    
data_sources:
  - name: retail_demo
    type: snowflake
    connection: snowflake_retail
```

### **Étape 3 : Déploiement**
```bash
# Via Foundry CLI
foundry agent deploy retail-analytics-agents
foundry agent test snowflake-retail-advisor "Analyse mes clients VIP"
```

---

## 📊 Monitoring et Analytics

### **Dashboard Foundry (automatique) :**
- ✅ **Utilisation agent** : Nombre de requêtes/jour
- ✅ **Performance** : Temps de réponse moyen
- ✅ **Qualité** : Scores de satisfaction utilisateur
- ✅ **Coûts** : Consommation Snowflake + Foundry

### **Métriques business :**
- ✅ **Questions populaires** : Top 10 des sujets
- ✅ **Utilisateurs actifs** : Adoption par équipe
- ✅ **Valeur créée** : Actions business générées

---

## 🔐 Sécurité et Gouvernance

### **Contrôles d'accès :**
- ✅ **Azure AD** : Authentification centralisée
- ✅ **RBAC Snowflake** : Rôle FOUNDRY_AGENT_ROLE
- ✅ **Audit trail** : Logs dans FOUNDRY_INTEGRATION_LOG
- ✅ **Data lineage** : Traçabilité des données utilisées

### **Compliance :**
- ✅ **RGPD** : Anonymisation automatique
- ✅ **SOC2** : Contrôles Foundry + Snowflake  
- ✅ **Encryption** : TLS 1.3 + chiffrement au repos

---

## 💡 Cas d'Usage Foundry Typiques

### **1. Assistant Teams pour Direction Commerciale**
```
👤 "Analyse performance Q1 vs objectifs"
🤖 [Agent analyse + graphiques Power BI intégrés]
```

### **2. Bot Slack pour équipes Marketing**  
```
👤 "/retail-agent Campagne VIP pour Noël"
🤖 [Recommandations + budget + ROI estimé]
```

### **3. App Power Apps pour terrain**
```
👤 [Manager magasin] "Performance de mon magasin"  
🤖 [Dashboard mobile + actions prioritaires]
```

**Votre agent Snowflake devient un service d'entreprise partageable ! 🎉**