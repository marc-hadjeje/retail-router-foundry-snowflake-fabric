#!/usr/bin/env python3
"""
🔧 Installation automatique de l'environnement MCP pour VS Code
Configuration des agents Snowflake dans VS Code
"""

import os
import subprocess
import json
import sys
from pathlib import Path

def install_vscode_extensions():
    """Installer les extensions VS Code nécessaires"""
    extensions = [
        "continue.continue",
        "ms-python.python", 
        "GitHub.copilot",
        "GitHub.copilot-chat",
        "ms-toolsai.jupyter",
        "humao.rest-client"
    ]
    
    print("🚀 Installation des extensions VS Code...")
    for ext in extensions:
        try:
            result = subprocess.run(['code', '--install-extension', ext], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {ext} installé")
            else:
                print(f"⚠️ {ext} déjà installé ou erreur")
        except FileNotFoundError:
            print("❌ VS Code CLI non trouvé. Installer VS Code et l'ajouter au PATH")
            return False
    return True

def setup_environment_variables():
    """Créer le fichier .env avec les variables MCP"""
    env_content = """# Configuration MCP Snowflake pour VS Code
SNOWFLAKE_ACCOUNT=nfhtxdc-gg96899
SNOWFLAKE_ROLE=MCP_RETAIL_ROLE
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=RETAIL_DEMO
SNOWFLAKE_SCHEMA=PUBLIC

# Endpoint MCP Server
MCP_ENDPOINT=https://nfhtxdc-gg96899.snowflakecomputing.com/api/v2/databases/RETAIL_DEMO/schemas/PUBLIC/mcp-servers/retail_mcp_server

# À compléter avec vos credentials
# SNOWFLAKE_USER=votre_utilisateur
# SNOWFLAKE_PASSWORD=votre_mot_de_passe
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✅ Fichier .env créé")

def create_workspace_config():
    """Créer la configuration workspace VS Code"""
    workspace_config = {
        "folders": [
            {"path": "."}
        ],
        "settings": {
            "mcp.servers.snowflake-retail.enabled": True,
            "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
            "terminal.integrated.env.windows": {
                "SNOWFLAKE_ACCOUNT": "nfhtxdc-gg96899",
                "SNOWFLAKE_ROLE": "MCP_RETAIL_ROLE", 
                "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH"
            }
        },
        "extensions": {
            "recommendations": [
                "continue.continue",
                "GitHub.copilot",
                "GitHub.copilot-chat",
                "ms-python.python"
            ]
        }
    }
    
    with open('demo_snow_agents.code-workspace', 'w', encoding='utf-8') as f:
        json.dump(workspace_config, f, indent=2)
    print("✅ Workspace VS Code configuré")

def install_mcp_dependencies():
    """Installer les dépendances MCP"""
    try:
        # Installer le client MCP pour Node.js
        subprocess.run(['npm', 'install', '-g', '@modelcontextprotocol/server-snowflake'], 
                      check=True)
        print("✅ MCP Server Snowflake installé")
        
        # Installer les dépendances Python
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'python-dotenv', 'mcp', 'asyncio'], check=True)
        print("✅ Dépendances Python MCP installées")
        
    except subprocess.CalledProcessError:
        print("⚠️ Erreur lors de l'installation des dépendances MCP")
        print("   Installer manuellement avec:")
        print("   npm install -g @modelcontextprotocol/server-snowflake")
        print("   pip install python-dotenv mcp asyncio")

def main():
    """Installation complète de l'environnement MCP VS Code"""
    print("🔧 Configuration MCP Snowflake pour VS Code")
    print("=" * 50)
    
    # Vérifier si on est dans le bon répertoire
    if not Path('snowflake/21_foundry_integration.sql').exists():
        print("❌ Exécuter ce script depuis la racine du projet demo_snow_agents")
        return
    
    # Installation étape par étape
    print("\n1. 📦 Installation des extensions VS Code...")
    install_vscode_extensions()
    
    print("\n2. 🌍 Configuration des variables d'environnement...")
    setup_environment_variables()
    
    print("\n3. ⚙️ Configuration du workspace...")
    create_workspace_config()
    
    print("\n4. 📚 Installation des dépendances MCP...")
    install_mcp_dependencies()
    
    print("\n" + "=" * 50)
    print("✅ INSTALLATION TERMINÉE !")
    print("\n📋 PROCHAINES ÉTAPES :")
    print("1. Compléter le fichier .env avec vos credentials Snowflake")
    print("2. Exécuter : snowflake/21_foundry_integration.sql dans Snowflake") 
    print("3. Tester avec : python test_mcp_server.py")
    print("4. Ouvrir VS Code : code demo_snow_agents.code-workspace")
    print("5. Utiliser Continue.dev ou Copilot Chat avec vos agents !")
    print("\n🎉 Vos agents Snowflake sont prêts dans VS Code !")

if __name__ == "__main__":
    main()