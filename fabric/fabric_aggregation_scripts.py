# Fabric Data Engineering - Scripts d'Agrégation Retail
# =====================================================
# Ces notebooks Fabric créent les données agrégées pour l'agent Fabric Data

# Configuration Fabric Lakehouse
lakehouse_name = "retail_analytics_lh"
workspace_id = "YOUR_WORKSPACE_ID"

# Import des libraries
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime, timedelta
import logging

# Configuration Spark
spark = SparkSession.builder.appName("RetailDataAggregation").getOrCreate()
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================================================================
# SCRIPT 1: AGRÉGATION MENSUELLE DES VENTES
# =================================================================

def create_monthly_sales_aggregation():
    """Crée les agrégations mensuelles des ventes"""
    
    logger.info("🔄 Début de l'agrégation mensuelle des ventes...")
    
    # Lecture des données sources depuis Snowflake (via Fabric connector)
    orders_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDERS") \
        .load()
    
    order_items_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDER_ITEMS") \
        .load()
    
    stores_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.STORES") \
        .load()
    
    # Jointure et calculs d'agrégation
    monthly_sales = orders_df.alias("o") \
        .join(order_items_df.alias("oi"), col("o.ORDER_ID") == col("oi.ORDER_ID")) \
        .join(stores_df.alias("s"), col("o.STORE_ID") == col("s.STORE_ID")) \
        .where(col("o.STATUS") != "Cancelled") \
        .groupBy(
            date_trunc("month", col("o.ORDER_DATE")).alias("sales_month"),
            col("s.STORE_ID"),
            col("s.NAME").alias("store_name"),
            col("s.CITY"),
            col("s.REGION"),
            col("s.STORE_TYPE")
        ) \
        .agg(
            countDistinct("o.ORDER_ID").alias("total_orders"),
            countDistinct("o.CUSTOMER_ID").alias("unique_customers"),
            sum("oi.LINE_TOTAL").alias("total_revenue"),
            avg("o.TOTAL_AMOUNT").alias("avg_order_value"),
            sum("oi.QUANTITY").alias("total_units_sold"),
            countDistinct("oi.PRODUCT_ID").alias("unique_products_sold"),
            sum("o.DISCOUNT_AMOUNT").alias("total_discounts"),
            sum("o.TAX_AMOUNT").alias("total_tax")
        ) \
        .withColumn("revenue_per_customer", col("total_revenue") / col("unique_customers")) \
        .withColumn("units_per_order", col("total_units_sold") / col("total_orders")) \
        .withColumn("created_date", current_timestamp())
    
    # Sauvegarde dans le Lakehouse
    monthly_sales.write \
        .mode("overwrite") \
        .format("delta") \
        .option("path", f"abfss://{lakehouse_name}@{storage_account}.dfs.core.windows.net/Tables/monthly_sales_summary") \
        .saveAsTable("monthly_sales_summary")
    
    logger.info(f"✅ Agrégation mensuelle terminée: {monthly_sales.count()} records créés")
    return monthly_sales

# =================================================================
# SCRIPT 2: ANALYSE DES SEGMENTS CLIENTS
# =================================================================

def create_customer_segment_aggregation():
    """Crée l'analyse agrégée par segment client"""
    
    logger.info("🔄 Début de l'analyse des segments clients...")
    
    # Lecture des données
    customers_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.CUSTOMERS") \
        .load()
    
    orders_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDERS") \
        .load()
    
    # Calcul des métriques par segment
    current_date = datetime.now()
    three_months_ago = current_date - timedelta(days=90)
    six_months_ago = current_date - timedelta(days=180)
    twelve_months_ago = current_date - timedelta(days=365)
    
    customer_segments = customers_df.alias("c") \
        .join(orders_df.alias("o"), col("c.CUSTOMER_ID") == col("o.CUSTOMER_ID"), "left") \
        .where(col("o.STATUS").isNull() | (col("o.STATUS") != "Cancelled")) \
        .groupBy(
            col("c.CUSTOMER_SEGMENT"),
            col("c.COUNTRY"),
            col("c.REGION")
        ) \
        .agg(
            countDistinct("c.CUSTOMER_ID").alias("total_customers"),
            countDistinct(
                when(col("o.ORDER_DATE") >= twelve_months_ago, col("c.CUSTOMER_ID"))
            ).alias("active_customers_12m"),
            countDistinct(
                when(col("o.ORDER_DATE") >= six_months_ago, col("c.CUSTOMER_ID"))
            ).alias("active_customers_6m"),
            countDistinct(
                when(col("o.ORDER_DATE") >= three_months_ago, col("c.CUSTOMER_ID"))
            ).alias("active_customers_3m"),
            sum(
                when(col("o.ORDER_DATE") >= twelve_months_ago, col("o.TOTAL_AMOUNT")).otherwise(0)
            ).alias("revenue_12m"),
            sum(
                when(col("o.ORDER_DATE") >= six_months_ago, col("o.TOTAL_AMOUNT")).otherwise(0)
            ).alias("revenue_6m"),
            sum(
                when(col("o.ORDER_DATE") >= three_months_ago, col("o.TOTAL_AMOUNT")).otherwise(0)
            ).alias("revenue_3m"),
            count(
                when(col("o.ORDER_DATE") >= twelve_months_ago, col("o.ORDER_ID"))
            ).alias("orders_12m"),
            avg(
                when(col("o.ORDER_DATE") >= twelve_months_ago, col("o.TOTAL_AMOUNT"))
            ).alias("avg_order_value_12m")
        ) \
        .withColumn("retention_rate_6m", col("active_customers_6m") / col("active_customers_12m")) \
        .withColumn("retention_rate_3m", col("active_customers_3m") / col("active_customers_6m")) \
        .withColumn("revenue_per_customer_12m", col("revenue_12m") / col("active_customers_12m")) \
        .withColumn("order_frequency_12m", col("orders_12m") / col("active_customers_12m")) \
        .withColumn("customer_lifetime_value", 
                   col("avg_order_value_12m") * col("order_frequency_12m") * 24) \
        .withColumn("created_date", current_timestamp())
    
    # Sauvegarde
    customer_segments.write \
        .mode("overwrite") \
        .format("delta") \
        .option("path", f"abfss://{lakehouse_name}@{storage_account}.dfs.core.windows.net/Tables/customer_segment_analysis") \
        .saveAsTable("customer_segment_analysis")
    
    logger.info(f"✅ Analyse segments clients terminée: {customer_segments.count()} segments analysés")
    return customer_segments

# =================================================================
# SCRIPT 3: PERFORMANCE PRODUITS ET CATÉGORIES
# =================================================================

def create_product_performance_aggregation():
    """Crée l'analyse de performance des produits et catégories"""
    
    logger.info("🔄 Début de l'analyse performance produits...")
    
    # Lecture des données
    products_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.PRODUCTS") \
        .load()
    
    categories_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.CATEGORIES") \
        .load()
    
    order_items_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDER_ITEMS") \
        .load()
    
    orders_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDERS") \
        .load()
    
    # Agrégation par catégorie et brand
    product_performance = products_df.alias("p") \
        .join(categories_df.alias("c"), col("p.CATEGORY_ID") == col("c.CATEGORY_ID")) \
        .join(order_items_df.alias("oi"), col("p.PRODUCT_ID") == col("oi.PRODUCT_ID")) \
        .join(orders_df.alias("o"), col("oi.ORDER_ID") == col("o.ORDER_ID")) \
        .where(col("o.STATUS") != "Cancelled") \
        .groupBy(
            col("c.CATEGORY_ID"),
            col("c.NAME").alias("category_name"),
            col("p.BRAND"),
            date_trunc("month", col("o.ORDER_DATE")).alias("sales_month")
        ) \
        .agg(
            countDistinct("p.PRODUCT_ID").alias("unique_products"),
            countDistinct("o.ORDER_ID").alias("total_orders"),
            sum("oi.QUANTITY").alias("total_units_sold"),
            sum("oi.LINE_TOTAL").alias("total_revenue"),
            sum(col("oi.QUANTITY") * col("p.COST")).alias("total_cost"),
            avg("oi.UNIT_PRICE").alias("avg_selling_price"),
            avg("p.PRICE").alias("avg_list_price"),
            avg("p.COST").alias("avg_cost"),
            sum("p.STOCK_QUANTITY").alias("total_stock"),
            countDistinct("o.CUSTOMER_ID").alias("unique_customers")
        ) \
        .withColumn("profit_margin", 
                   (col("total_revenue") - col("total_cost")) / col("total_revenue")) \
        .withColumn("inventory_turnover", 
                   col("total_cost") / col("total_stock")) \
        .withColumn("revenue_per_product", 
                   col("total_revenue") / col("unique_products")) \
        .withColumn("units_per_customer", 
                   col("total_units_sold") / col("unique_customers")) \
        .withColumn("created_date", current_timestamp())
    
    # Sauvegarde
    product_performance.write \
        .mode("overwrite") \
        .format("delta") \
        .option("path", f"abfss://{lakehouse_name}@{storage_account}.dfs.core.windows.net/Tables/product_category_performance") \
        .saveAsTable("product_category_performance")
    
    logger.info(f"✅ Analyse performance produits terminée: {product_performance.count()} records créés")
    return product_performance

# =================================================================
# SCRIPT 4: ANALYSE GÉOGRAPHIQUE
# =================================================================

def create_geographic_performance_aggregation():
    """Crée l'analyse de performance géographique"""
    
    logger.info("🔄 Début de l'analyse géographique...")
    
    # Lecture et jointure des données
    stores_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.STORES") \
        .load()
    
    orders_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDERS") \
        .load()
    
    customers_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.CUSTOMERS") \
        .load()
    
    # Agrégation géographique
    geographic_performance = stores_df.alias("s") \
        .join(orders_df.alias("o"), col("s.STORE_ID") == col("o.STORE_ID")) \
        .join(customers_df.alias("c"), col("o.CUSTOMER_ID") == col("c.CUSTOMER_ID")) \
        .where(col("o.STATUS") != "Cancelled") \
        .groupBy(
            col("s.COUNTRY"),
            col("s.REGION"),
            col("s.CITY"),
            date_trunc("quarter", col("o.ORDER_DATE")).alias("sales_quarter")
        ) \
        .agg(
            countDistinct("s.STORE_ID").alias("store_count"),
            countDistinct("o.ORDER_ID").alias("total_orders"),
            countDistinct("o.CUSTOMER_ID").alias("unique_customers"),
            sum("o.TOTAL_AMOUNT").alias("total_revenue"),
            avg("o.TOTAL_AMOUNT").alias("avg_order_value"),
            sum("s.SURFACE_M2").alias("total_surface_m2"),
            avg("s.SURFACE_M2").alias("avg_surface_m2")
        ) \
        .withColumn("revenue_per_store", col("total_revenue") / col("store_count")) \
        .withColumn("revenue_per_m2", col("total_revenue") / col("total_surface_m2")) \
        .withColumn("customers_per_store", col("unique_customers") / col("store_count")) \
        .withColumn("market_penetration", 
                   col("unique_customers") / 
                   when(col("city") == "Paris", 2200000)
                   .when(col("city") == "Lyon", 515695)
                   .when(col("city") == "Marseille", 870018)
                   .otherwise(100000)) \
        .withColumn("created_date", current_timestamp())
    
    # Sauvegarde
    geographic_performance.write \
        .mode("overwrite") \
        .format("delta") \
        .option("path", f"abfss://{lakehouse_name}@{storage_account}.dfs.core.windows.net/Tables/regional_store_performance") \
        .saveAsTable("regional_store_performance")
    
    logger.info(f"✅ Analyse géographique terminée: {geographic_performance.count()} regions analysées")
    return geographic_performance

# =================================================================
# SCRIPT 5: ANALYSE SAISONNIÈRE
# =================================================================

def create_seasonal_analysis():
    """Crée l'analyse des tendances saisonnières"""
    
    logger.info("🔄 Début de l'analyse saisonnière...")
    
    orders_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDERS") \
        .load()
    
    order_items_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.ORDER_ITEMS") \
        .load()
    
    products_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.PRODUCTS") \
        .load()
    
    categories_df = spark.read.format("snowflake") \
        .options(**snowflake_options) \
        .option("dbtable", "RETAIL_DEMO.MAIN.CATEGORIES") \
        .load()
    
    # Analyse saisonnière
    seasonal_analysis = orders_df.alias("o") \
        .join(order_items_df.alias("oi"), col("o.ORDER_ID") == col("oi.ORDER_ID")) \
        .join(products_df.alias("p"), col("oi.PRODUCT_ID") == col("p.PRODUCT_ID")) \
        .join(categories_df.alias("c"), col("p.CATEGORY_ID") == col("c.CATEGORY_ID")) \
        .where(col("o.STATUS") != "Cancelled") \
        .withColumn("year", year(col("o.ORDER_DATE"))) \
        .withColumn("month", month(col("o.ORDER_DATE"))) \
        .withColumn("quarter", quarter(col("o.ORDER_DATE"))) \
        .withColumn("week_of_year", weekofyear(col("o.ORDER_DATE"))) \
        .withColumn("day_of_week", dayofweek(col("o.ORDER_DATE"))) \
        .groupBy(
            col("c.CATEGORY_ID"),
            col("c.NAME").alias("category_name"),
            col("year"),
            col("month"),
            col("quarter"),
            col("week_of_year"),
            col("day_of_week")
        ) \
        .agg(
            sum("oi.LINE_TOTAL").alias("revenue"),
            sum("oi.QUANTITY").alias("units_sold"),
            countDistinct("o.ORDER_ID").alias("order_count"),
            countDistinct("o.CUSTOMER_ID").alias("customer_count")
        )
    
    # Calcul des index saisonniers
    seasonal_with_index = seasonal_analysis \
        .withColumn("monthly_avg_revenue", 
                   avg("revenue").over(Window.partitionBy("category_id", "year"))) \
        .withColumn("seasonal_index", col("revenue") / col("monthly_avg_revenue")) \
        .withColumn("yoy_growth", 
                   (col("revenue") - 
                    lag("revenue").over(Window.partitionBy("category_id", "month")
                                      .orderBy("year"))) / 
                   lag("revenue").over(Window.partitionBy("category_id", "month")
                                     .orderBy("year"))) \
        .withColumn("created_date", current_timestamp())
    
    # Sauvegarde
    seasonal_with_index.write \
        .mode("overwrite") \
        .format("delta") \
        .option("path", f"abfss://{lakehouse_name}@{storage_account}.dfs.core.windows.net/Tables/seasonal_analysis") \
        .saveAsTable("seasonal_analysis")
    
    logger.info(f"✅ Analyse saisonnière terminée: {seasonal_with_index.count()} patterns identifiés")
    return seasonal_with_index

# =================================================================
# ORCHESTRATION PRINCIPALE
# =================================================================

def run_all_aggregations():
    """Exécute toutes les agrégations dans l'ordre"""
    
    logger.info("🚀 Début du processus d'agrégation complet")
    
    try:
        # Configuration Snowflake
        global snowflake_options, storage_account
        snowflake_options = {
            "sfUrl": "YOUR_SNOWFLAKE_ACCOUNT.snowflakecomputing.com",
            "sfUser": "AGENT_USER",
            "sfPassword": "AgentDemo2024!",
            "sfDatabase": "RETAIL_DEMO",
            "sfSchema": "MAIN",
            "sfWarehouse": "RETAIL_WH"
        }
        storage_account = "YOUR_STORAGE_ACCOUNT"
        
        # Exécution des agrégations
        results = {}
        results['monthly_sales'] = create_monthly_sales_aggregation()
        results['customer_segments'] = create_customer_segment_aggregation()
        results['product_performance'] = create_product_performance_aggregation()
        results['geographic_performance'] = create_geographic_performance_aggregation()
        results['seasonal_analysis'] = create_seasonal_analysis()
        
        logger.info("🎉 Toutes les agrégations terminées avec succès!")
        
        # Résumé des résultats
        for name, df in results.items():
            count = df.count()
            logger.info(f"📊 {name}: {count} records créés")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'agrégation: {str(e)}")
        raise e

# Lancement automatique si exécuté directement
if __name__ == "__main__":
    run_all_aggregations()