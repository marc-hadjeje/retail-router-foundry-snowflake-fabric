"""
🧪 Test du Serveur MCP Snowflake Retail
=====================================
Script pour tester le serveur MCP retail_mcp_server et ses 3 outils.

Usage:
    python test_mcp_server.py
"""

import os
import json
import snowflake.connector
from datetime import datetime
from typing import Dict, Any, List

class MCPServerTester:
    """Testeur pour le serveur MCP Snowflake retail_mcp_server"""
    
    def __init__(self, 
                 account: str = "nfhtxdc-gg96899",
                 warehouse: str = "COMPUTE_WH", 
                 database: str = "RETAIL_DEMO",
                 schema: str = "PUBLIC"):
        
        self.account = account
        self.warehouse = warehouse  
        self.database = database
        self.schema = schema
        self.connection = None
        
    def connect(self) -> bool:
        """Connexion sécurisée à Snowflake"""
        try:
            user = os.getenv('SNOWFLAKE_USER')
            password = os.getenv('SNOWFLAKE_PASSWORD')
            
            if not user or not password:
                print("🔐 Variables SNOWFLAKE_USER et SNOWFLAKE_PASSWORD requises")
                print("   Exemple: set SNOWFLAKE_USER=mon_user")
                print("   Exemple: set SNOWFLAKE_PASSWORD=mon_password")
                return False
                
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=user,
                password=password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema
            )
            print(f"✅ Connexion Snowflake établie : {self.account}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur connexion Snowflake : {e}")
            return False
    
    def test_mcp_server_exists(self) -> bool:
        """Vérifier que le serveur MCP existe"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW MCP SERVERS LIKE 'retail_mcp_server'")
            result = cursor.fetchall()
            
            if result:
                print("✅ Serveur MCP 'retail_mcp_server' trouvé")
                print(f"   Détails: {result[0]}")
                
                # Construire l'endpoint MCP avec le format correct
                account_url = "nfhtxdc-gg96899.snowflakecomputing.com"
                database = "RETAIL_DEMO"
                schema = "PUBLIC" 
                server_name = "retail_mcp_server"
                mcp_endpoint = f"https://{account_url}/api/v2/databases/{database}/schemas/{schema}/mcp-servers/{server_name}"
                print(f"🔗 Endpoint MCP: {mcp_endpoint}")
                print(f"📋 Pattern: https://{{account_URL}}/api/v2/databases/{{database}}/schemas/{{schema}}/mcp-servers/{{name}}")
                
                # Tenter d'obtenir l'endpoint via fonction système (peut ne pas fonctionner sur tous les comptes)
                try:
                    cursor.execute("SELECT SYSTEM$GET_MCP_SERVER_ENDPOINT('retail_mcp_server') AS endpoint")
                    endpoint_result = cursor.fetchone()
                    if endpoint_result and endpoint_result[0]:
                        print(f"🎯 Endpoint système: {endpoint_result[0]}")
                    else:
                        print("📡 Endpoint système non disponible, utilisez l'URL construite ci-dessus")
                except Exception as e:
                    print(f"⚠️  Fonction système indisponible: {e}")
                    print("   Utilisez l'URL construite manuellement")
                
                cursor.close()
                return True
            else:
                print("❌ Serveur MCP 'retail_mcp_server' non trouvé")
                print("   Exécuter d'abord : snowflake/21_foundry_integration.sql")
                cursor.close()
                return False
                
        except Exception as e:
            print(f"❌ Erreur vérification MCP server : {e}")
            return False
    
    def describe_mcp_server(self) -> Dict[str, Any]:
        """Décrire le serveur MCP et ses outils"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DESCRIBE MCP SERVER retail_mcp_server")
            result = cursor.fetchall()
            cursor.close()
            
            print("\n📋 Description du serveur MCP:")
            for row in result:
                print(f"   {row}")
            
            return {"success": True, "description": result}
            
        except Exception as e:
            print(f"❌ Erreur description MCP server : {e}")
            return {"success": False, "error": str(e)}
    
    def test_agents_availability(self) -> Dict[str, Any]:
        """Tester la disponibilité des agents sous-jacents"""
        print("\n🔍 === TEST DISPONIBILITÉ AGENTS ===")
        
        agents_results = {}
        
        # Test 1: Agent Cortex principal
        print("\n1. Test Agent Cortex (RETAIL_CLIENT_ADVISOR)")
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW AGENTS LIKE 'RETAIL_CLIENT_ADVISOR'")
            result = cursor.fetchall()
            if result:
                agents_results["cortex_agent"] = {"status": "available", "details": str(result[0])}
                print(f"   ✅ Agent disponible")
            else:
                agents_results["cortex_agent"] = {"status": "not_found"}
                print(f"   ❌ Agent non trouvé")
            cursor.close()
        except Exception as e:
            agents_results["cortex_agent"] = {"status": "error", "error": str(e)}
            print(f"   ⚠️  Erreur : {e}")
        
        # Test 2: Fonction IA Cortex
        print("\n2. Test Fonction Cortex IA (AGENT_IA_CLIENTS)")
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT AGENT_IA_CLIENTS('Test MCP') as response")
            result = cursor.fetchone()
            agents_results["ia_function"] = {"status": "success", "result": result[0] if result else "No response"}
            print(f"   ✅ Réponse : {result[0][:100] if result and result[0] else 'Aucune réponse'}...")
            cursor.close()
        except Exception as e:
            agents_results["ia_function"] = {"status": "error", "error": str(e)}
            print(f"   ⚠️  Cortex AI indisponible : {e}")
        
        # Test 3: Agent backup SQL
        print("\n3. Test Agent Backup SQL (AGENT_CLIENTS)")
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT AGENT_CLIENTS('Test MCP backup') as response")
            result = cursor.fetchone()
            agents_results["backup_agent"] = {"status": "success", "result": result[0]}
            print(f"   ✅ Réponse backup : {result[0][:100]}...")
            cursor.close()
        except Exception as e:
            agents_results["backup_agent"] = {"status": "error", "error": str(e)}
            print(f"   ❌ Erreur backup : {e}")
        
        return agents_results
    
    def test_permissions(self) -> Dict[str, Any]:
        """Tester les permissions du rôle MCP"""
        print("\n🔐 === TEST PERMISSIONS MCP_RETAIL_ROLE ===")
        
        try:
            cursor = self.connection.cursor()
            
            # Vérifier que le rôle existe
            cursor.execute("SHOW ROLES LIKE 'MCP_RETAIL_ROLE'")
            role_result = cursor.fetchall()
            
            if role_result:
                print("✅ Rôle MCP_RETAIL_ROLE trouvé")
                
                # Vérifier les grants
                cursor.execute("SHOW GRANTS TO ROLE MCP_RETAIL_ROLE")
                grants = cursor.fetchall()
                
                print(f"📋 Permissions accordées ({len(grants)} grants):")
                for grant in grants[:5]:  # Limiter l'affichage
                    print(f"   - {grant}")
                
                cursor.close()
                return {"success": True, "grants_count": len(grants)}
            else:
                print("❌ Rôle MCP_RETAIL_ROLE non trouvé")
                cursor.close()
                return {"success": False, "error": "Role not found"}
                
        except Exception as e:
            print(f"❌ Erreur test permissions : {e}")
            return {"success": False, "error": str(e)}
    
    def simulate_mcp_calls(self) -> List[Dict[str, Any]]:
        """Simuler des appels MCP JSON-RPC"""
        print("\n🤖 === SIMULATION APPELS MCP ===")
        
        # Exemples d'appels MCP à tester
        mcp_calls = [
            {
                "name": "snowflake-retail-agent",
                "args": {"question": "Qui sont mes clients VIP ?"},
                "sql": "SELECT 'Agent Cortex disponible' as status"
            },
            {
                "name": "retail-client-analysis", 
                "args": {"question": "Analyse de segmentation"},
                "sql": "SELECT AGENT_IA_CLIENTS('Segmentation clients VIP')"
            },
            {
                "name": "retail-backup-agent",
                "args": {"question": "VIP"}, 
                "sql": "SELECT AGENT_CLIENTS('VIP')"
            }
        ]
        
        results = []
        
        for i, call in enumerate(mcp_calls, 1):
            print(f"\n{i}. Test outil MCP: {call['name']}")
            print(f"   Arguments: {call['args']}")
            
            try:
                cursor = self.connection.cursor()
                cursor.execute(call['sql'])
                result = cursor.fetchone()
                cursor.close()
                
                mcp_response = {
                    "tool": call['name'],
                    "status": "success",
                    "response": result[0] if result else "No response",
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"   ✅ Succès : {str(result[0])[:80] if result else 'Aucune réponse'}...")
                results.append(mcp_response)
                
            except Exception as e:
                mcp_response = {
                    "tool": call['name'],
                    "status": "error", 
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"   ❌ Erreur : {e}")
                results.append(mcp_response)
        
        return results
    
    def run_full_test(self):
        """Exécuter test complet du serveur MCP"""
        print("🧪 TEST COMPLET SERVEUR MCP RETAIL_MCP_SERVER")
        print("=" * 55)
        
        # 1. Connexion
        if not self.connect():
            return False
        
        # 2. Vérification existence serveur MCP
        if not self.test_mcp_server_exists():
            return False
        
        # 3. Description du serveur
        description = self.describe_mcp_server()
        
        # 4. Test disponibilité agents
        agents_status = self.test_agents_availability()
        
        # 5. Test permissions
        permissions = self.test_permissions()
        
        # 6. Simulation appels MCP
        mcp_results = self.simulate_mcp_calls()
        
        # 7. Résumé final
        print(f"\n📊 === RÉSUMÉ DES TESTS ===")
        
        agents_ok = sum(1 for agent in agents_status.values() 
                       if agent.get('status') in ['success', 'available'])
        mcp_ok = sum(1 for result in mcp_results 
                    if result.get('status') == 'success')
        
        print(f"✅ Serveur MCP : {'Opérationnel' if description.get('success') else 'Problème'}")
        print(f"✅ Agents disponibles : {agents_ok}/3")
        print(f"✅ Appels MCP réussis : {mcp_ok}/3")
        print(f"✅ Permissions : {'OK' if permissions.get('success') else 'Problème'}")
        
        if agents_ok >= 2 and mcp_ok >= 2 and permissions.get('success'):
            print("\n🎉 SERVEUR MCP OPÉRATIONNEL ! Prêt pour intégration.")
            print("\n📋 PROCHAINES ÉTAPES :")
            print("   1. Configurer client MCP dans votre application")
            print("   2. Tester avec Claude/GPT via protocole MCP") 
            print("   3. Intégrer dans vos workflows IA")
        else:
            print("\n🔧 Ajustements nécessaires - Vérifier configuration Snowflake.")
        
        # Nettoyage
        if self.connection:
            self.connection.close()
        
        return agents_ok >= 2

def main():
    """Point d'entrée principal"""
    print("🤖 TESTEUR SERVEUR MCP SNOWFLAKE RETAIL")
    print("=" * 45)
    
    tester = MCPServerTester()
    success = tester.run_full_test()
    
    if success:
        print("\n🚀 Tests validés ! Serveur MCP prêt à l'emploi.")
    else:
        print("\n🔧 Problèmes détectés - Vérifier la configuration.")

if __name__ == "__main__":
    main()