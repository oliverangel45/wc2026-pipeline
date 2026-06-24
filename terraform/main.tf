terraform {
    required_providers {
      snowflake = {
        source  = "Snowflake-Labs/snowflake"
        version = "~> 0.100"
      }
    }
}

provider "snowflake" {
    organization_name = var.snowflake_organization
    account_name      = var.snowflake_account
    user              = var.snowflake_user
    password          = var.snowflake_password
    role              = "ACCOUNTADMIN"
    warehouse         = "COMPUTE_WH"
}

resource "snowflake_warehouse" "wc2026_wh" {
    name           = "WC2026_WH"
    warehouse_size = "X-SMALL"
    auto_suspend   = 120
    auto_resume    = true
    comment        = "Warehouse for WC2026 Pipeline"
}

resource "snowflake_database" "wc2026" {
    name    = "WC2026"
    comment = "Database for WC2026 Pipeline"
}

resource "snowflake_schema" "raw" {
    database = snowflake_database.wc2026.name
    name     = "RAW"
    comment  = "Raw data landed by Kafka Consumer"
}

resource "snowflake_schema" "analytics" {
    database = snowflake_database.wc2026.name
    name     = "ANALYTICS"
    comment  = "Schema for WC2026 dbt modelled data"
}

# ROLES

resource "snowflake_account_role" "loader" {
    name    = "LOADER"
    comment = "Loads raw data from Kafka Consumer into RAW schema"
}

resource "snowflake_account_role" "transformer" {
    name    = "TRANSFORMER"
    comment = "Loads dbt modelled data into ANALYTICS schema"
}

# LOADER Role Grants

resource "snowflake_grant_privileges_to_account_role" "loader_warehouse" {
  account_role_name  = snowflake_account_role.loader.name
  privileges = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.wc2026_wh.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "loader_database" {
  account_role_name  = snowflake_account_role.loader.name
  privileges = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.wc2026.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "loader_raw_schema" {
  account_role_name  = snowflake_account_role.loader.name
  privileges = ["USAGE", "CREATE TABLE"]
  on_schema {
    schema_name = "\"${snowflake_database.wc2026.name}\".\"${snowflake_schema.raw.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "loader_raw_write" {
  account_role_name  = snowflake_account_role.loader.name
  privileges = ["INSERT", "UPDATE", "SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.wc2026.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}

# TRANSFORMER Role Grants

resource "snowflake_grant_privileges_to_account_role" "transformer_warehouse" {
  account_role_name  = snowflake_account_role.transformer.name
  privileges = ["USAGE"]
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.wc2026_wh.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_database" {
  account_role_name  = snowflake_account_role.transformer.name
  privileges = ["USAGE"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.wc2026.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_raw_schema" {
  account_role_name  = snowflake_account_role.transformer.name
  privileges = ["USAGE"]
  on_schema {
    schema_name = "\"${snowflake_database.wc2026.name}\".\"${snowflake_schema.raw.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_raw_read" {
  account_role_name  = snowflake_account_role.transformer.name
  privileges = ["SELECT"]
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema          = "\"${snowflake_database.wc2026.name}\".\"${snowflake_schema.raw.name}\""
    }
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_analytics_schema" {
  account_role_name  = snowflake_account_role.transformer.name
  privileges = ["USAGE", "CREATE TABLE", "CREATE VIEW"]
  on_schema {
    schema_name = "\"${snowflake_database.wc2026.name}\".\"${snowflake_schema.analytics.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "transformer_create_schema_on_db" {
  account_role_name = snowflake_account_role.transformer.name
  privileges        = ["CREATE SCHEMA"]
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.wc2026.name
  }
}

# TABLES

resource "snowflake_table" "raw_matches" {
  database = snowflake_database.wc2026.name
  schema   = snowflake_schema.raw.name
  name     = "MATCHES"
  comment  = "Raw match data from football-data.org"

  column {
    name     = "MATCH_ID"
    type     = "NUMBER"
    nullable = false
  }
  column {
    name = "HOME_TEAM"
    type = "VARCHAR(100)"
  }
  column {
    name = "AWAY_TEAM"
    type = "VARCHAR(100)"
  }
  column {
    name = "HOME_SCORE"
    type = "NUMBER"
  }
  column {
    name = "AWAY_SCORE"
    type = "NUMBER"
  }
  column {
    name = "STATUS"
    type = "VARCHAR(50)"
  }
  column {
    name = "MATCHDAY"
    type = "NUMBER"
  }
  column {
    name = "STAGE"
    type = "VARCHAR(100)"
  }
  column {
    name = "UTC_DATE"
    type = "TIMESTAMP_TZ"
  }
  column {
    name = "LAST_UPDATED"
    type = "TIMESTAMP_TZ"
  }
  column {
    name = "RAW_PAYLOAD"
    type = "VARIANT"
  }
  column {
    name    = "INGESTED_AT"
    type    = "TIMESTAMP_TZ"
    default {
      constant = "CURRENT_TIMESTAMP()"
    }
  }
}

resource "snowflake_table" "raw_standings" {
  database = snowflake_database.wc2026.name
  schema   = snowflake_schema.raw.name
  name     = "STANDINGS"
  comment  = "Raw group standings from football-data.org"

  column {
    name     = "TEAM_ID"
    type     = "NUMBER"
    nullable = false
  }
  column {
    name = "TEAM_NAME"
    type = "VARCHAR(100)"
  }
  column {
    name = "GROUP_NAME"
    type = "VARCHAR(10)"
  }
  column {
    name = "POSITION"
    type = "NUMBER"
  }
  column {
    name = "PLAYED_GAMES"
    type = "NUMBER"
  }
  column {
    name = "WON"
    type = "NUMBER"
  }
  column {
    name = "DRAW"
    type = "NUMBER"
  }
  column {
    name = "LOST"
    type = "NUMBER"
  }
  column {
    name = "POINTS"
    type = "NUMBER"
  }
  column {
    name = "GOALS_FOR"
    type = "NUMBER"
  }
  column {
    name = "GOALS_AGAINST"
    type = "NUMBER"
  }
  column {
    name = "GOAL_DIFF"
    type = "NUMBER"
  }
  column {
    name = "RAW_PAYLOAD"
    type = "VARIANT"
  }
  column {
    name    = "INGESTED_AT"
    type    = "TIMESTAMP_TZ"
    default {
      constant = "CURRENT_TIMESTAMP()"
    }
  }
}

resource "snowflake_table" "raw_events" {
  database = snowflake_database.wc2026.name
  schema   = snowflake_schema.raw.name
  name     = "EVENTS"
  comment  = "Raw match events - goals, cards, substitutions"

  column {
    name     = "EVENT_ID"
    type     = "VARCHAR(100)"
    nullable = false
  }
  column {
    name     = "MATCH_ID"
    type     = "NUMBER"
    nullable = false
  }
  column {
    name = "MINUTE"
    type = "NUMBER"
  }
  column {
    name = "EXTRA_TIME_MINUTE"
    type = "NUMBER"
  }
  column {
    name = "EVENT_TYPE"
    type = "VARCHAR(50)"
  }
  column {
    name = "EVENT_DETAIL"
    type = "VARCHAR(100)"
  }
  column {
    name = "TEAM_ID"
    type = "NUMBER"
  }
  column {
    name = "TEAM_NAME"
    type = "VARCHAR(100)"
  }
  column {
    name = "PLAYER_NAME"
    type = "VARCHAR(100)"
  }
  column {
    name = "ASSIST_NAME"
    type = "VARCHAR(100)"
  }
  column {
    name = "RAW_PAYLOAD"
    type = "VARIANT"
  }
  column {
    name    = "INGESTED_AT"
    type    = "TIMESTAMP_TZ"
    default {
      constant = "CURRENT_TIMESTAMP()"
    }
  }
}