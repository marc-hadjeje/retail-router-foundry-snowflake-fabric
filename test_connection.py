#!/usr/bin/env python3
"""Test de connexion Snowflake minimal"""
import snowflake.connector

try:
    print("Test de connexion Snowflake...")
    
    conn = snowflake.connector.connect(
        account='nfhtxdc-gg96899',
        user='MARCHADJEJE',
        password='Ilana&Gabriel2026'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()[0]
    
    print(f"SUCCES! Version Snowflake: {version}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERREUR: {str(e)}")