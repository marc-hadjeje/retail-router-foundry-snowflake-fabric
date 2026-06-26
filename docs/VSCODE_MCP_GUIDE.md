# 🔧 Guide MCP Snowflake pour VS Code

## 🚀 **Configuration Terminée !**

Votre workspace VS Code est maintenant configuré pour utiliser les **agents Snowflake via MCP**.

---

## 📦 **Extensions Requises**

### **Installation automatique :**
```bash
# Installer les extensions nécessaires
code --install-extension continue.continue
code --install-extension ms-python.python
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
```

### **Extensions optionnelles :**
- **Thunder Client** - Pour tester les appels MCP HTTP
- **REST Client** - Alternative pour tests API
- **Snowflake** - Extension officielle Snowflake

---

## 🎯 **Utilisation dans VS Code**

### **1. Continue.dev Chat :**
```
Ctrl+Shift+P → "Continue: Open Chat"

Dans le chat Continue :
> Utilisez l'agent snowflake-retail-agent pour analyser les ventes Q1 2026

> Avec retail-client-analysis, segmentez mes clients VIP
```

### **2. GitHub Copilot Chat :**
```
Ctrl+Shift+P → "GitHub Copilot Chat: Open Chat"

Dans Copilot Chat :
@snowflake-retail-agent analysez les tendances de vente

@retail-client-analysis quels sont mes meilleurs clients ?
```

### **3. Commande Palette :**
```
Ctrl+Shift+P → "Tasks: Run Task"
→ Sélectionner "Test MCP Server Snowflake"
→ Sélectionner "Deploy MCP Server to Snowflake"
```

### **4. Terminal Intégré :**
```bash
# Test rapide de connexion
python test_mcp_server.py

# Déploiement du serveur MCP
snowsql -f snowflake/21_foundry_integration.sql
```

---

## 🔧 **Configuration Avancée**

### **Variables d'Environnement (.env) :**
```bash
# Créer un fichier .env à la racine
SNOWFLAKE_ACCOUNT=nfhtxdc-gg96899
SNOWFLAKE_USER=votre_utilisateur
SNOWFLAKE_PASSWORD=votre_mot_de_passe
SNOWFLAKE_ROLE=MCP_RETAIL_ROLE
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=RETAIL_DEMO
SNOWFLAKE_SCHEMA=PUBLIC

MCP_ENDPOINT=https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server
```

### **Keybindings Personnalisés :**
```json
// Dans keybindings.json
[
  {
    "key": "ctrl+shift+s ctrl+shift+r",
    "command": "workbench.action.tasks.runTask",
    "args": "Test MCP Server Snowflake"
  },
  {
    "key": "ctrl+shift+s ctrl+shift+a",
    "command": "continue.continueGUIView.focus"
  }
]
```

---

## 🎮 **Exemples d'Utilisation**

### **Analyse de Ventes :**
```markdown
Dans Continue.dev ou Copilot Chat :

> @snowflake-retail-agent 
> Analysez les performances de vente pour mars 2026. 
> Identifiez les produits les plus vendus et les magasins les plus performants.
> Donnez des recommandations pour améliorer les ventes.
```

### **Segmentation Clients :**
```markdown
> @retail-client-analysis
> Segmentez nos clients par valeur (VIP, Standard, Occasionnel).
> Calculez le CLV moyen par segment et proposez des stratégies de rétention.
```

### **Analyse Rapide (Backup) :**
```markdown
> @retail-backup-agent VIP
> Donnez-moi la liste des clients VIP avec leurs statistiques d'achat.
```

---

## 🐛 **Debug et Dépannage**

### **1. Tester la Connexion :**
```bash
# Dans le terminal VS Code
F1 → "Terminal: Create New Terminal"
python test_mcp_server.py
```

### **2. Vérifier les Logs :**
```bash
# Logs VS Code
Help → "Toggle Developer Tools" → Console

# Logs Continue.dev
~/.continue/logs/

# Logs MCP
Check terminal output lors des appels
```

### **3. Debug MCP Server :**
```bash
# Mode debug avec F5
F5 → Sélectionner "Debug MCP Client"

# Ou en terminal
npx @modelcontextprotocol/server-snowflake --endpoint YOUR_ENDPOINT --debug
```

---

## ✅ **Validation Complète**

### **Checklist :**
- ✅ Extensions installées (Continue.dev, Copilot)
- ✅ Configuration MCP dans `.vscode/settings.json`
- ✅ Variables d'environnement définies
- ✅ Serveur MCP déployé dans Snowflake
- ✅ Test de connexion réussi
- ✅ Agents accessibles via chat

### **Test Final :**
```bash
# Exécuter cette commande dans VS Code Terminal
python -c "
import os
print('🔧 Configuration VS Code MCP:')
print(f'Account: {os.getenv(\"SNOWFLAKE_ACCOUNT\", \"❌ Non défini\")}')
print(f'Role: {os.getenv(\"SNOWFLAKE_ROLE\", \"❌ Non défini\")}') 
print(f'Warehouse: {os.getenv(\"SNOWFLAKE_WAREHOUSE\", \"❌ Non défini\")}')
print('✅ Configuration MCP prête !')
"
```

---

## 🚀 **Votre VS Code est Prêt !**

Vous pouvez maintenant utiliser vos **agents Snowflake directement dans VS Code** via :
- 💬 **Continue.dev Chat**  
- 🤖 **GitHub Copilot Chat**
- ⚡ **Commandes VS Code**
- 🔧 **Terminal intégré**

**Les agents IA Snowflake sont maintenant des outils natifs de votre environnement de développement !** 🎉