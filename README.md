# bitsom_ba_25071252-fleximart-data-architecture

# FlexiMart Data Architecture Project

**Student Name:** SHRIPRASAD_PANDURANG_PATIL  
**Student ID:** 25071252  
**Email:** shrii2199patil@gmail.com  
**Date:** 2025-12-25

## Project Overview
This repository implements an end-to-end data pipeline for FlexiMart. It ingests raw CSV files, cleans and loads them into a relational database, supports business reporting through SQL queries, includes a MongoDB product catalog workflow, and builds a star-schema data warehouse for analytics.

## Repository Structure
├── data/  
│   ├── customers_raw.csv  
│   ├── products_raw.csv  
│   └── sales_raw.csv  
├── part1-database-etl/  
│   ├── README.md  
│   ├── etl_pipeline.py  
│   ├── schema_documentation.md  
│   ├── business_queries.sql  
│   ├── data_quality_report.txt  
│   └── requirements.txt  
├── part2-nosql/  
│   ├── README.md  
│   ├── nosql_analysis.md  
│   ├── mongodb_operations.js  
│   └── products_catalog.json  
└── part3-datawarehouse/  
    ├── README.md  
    ├── star_schema_design.md  
    ├── warehouse_schema.sql  
    ├── warehouse_data.sql  
    └── analytics_queries.sql  

## Technologies Used
- Python 3.x, pandas
- MySQL 8.0 (or PostgreSQL 14)
- MongoDB 6.0

## Setup Instructions

### Database Setup

```bash
# Create databases
mysql -u root -p -e "CREATE DATABASE fleximart;"
mysql -u root -p -e "CREATE DATABASE fleximart_dw;"

# Run Part 1 - ETL Pipeline
python part1-database-etl/etl_pipeline.py

# Run Part 1 - Business Queries
mysql -u root -p fleximart < part1-database-etl/business_queries.sql

# Run Part 3 - Data Warehouse
mysql -u root -p fleximart_dw < part3-datawarehouse/warehouse_schema.sql
mysql -u root -p fleximart_dw < part3-datawarehouse/warehouse_data.sql
mysql -u root -p fleximart_dw < part3-datawarehouse/analytics_queries.sql


### MongoDB Setup

mongosh < part2-nosql/mongodb_operations.js

## Key Learnings

[3-4 sentences on what you learned]

## Challenges Faced

1. [Challenge and solution]
2. [Challenge and solution]
