# This file is used to verify the correct infrastructure has been created in the terminal after 'terraform apply'

output "warehouse_name" {
    value       = snowflake_warehouse.wc2026_wh.name
    description = "Snowflake warehouse name"
}

output "database_name" {
    value       = snowflake_database.wc2026.name
    description = "Snowflake database name"
}

output "raw_schema" {
    value       = "${snowflake_database.wc2026.name}.${snowflake_schema.raw.name}"
    description = "Full path to RAW schema"
}

output "analytics_schema" {
    value       = "${snowflake_database.wc2026.name}.${snowflake_schema.analytics.name}"
    description = "Full path to ANALYTICS schema"
}

output "loader_role" {
    value       = snowflake_account_role.loader.name
    description = "Role used by Kafka consumer"
}

output "transformer_role" {
    value       = snowflake_account_role.transformer.name
    description = "Role used by dbt"
}