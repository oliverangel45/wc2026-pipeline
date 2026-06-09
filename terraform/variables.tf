variable "snowflake_organization" {
  description = "Snowflake organization name"
  type        = string
  sensitive   = true
}

variable "snowflake_account" {
    description = "Snowflake account identifier"
    type        = string
    sensitive   = true
}

variable "snowflake_user" {
    description = "Snowflake admin username"
    type        = string
    sensitive   = true
}

variable "snowflake_password" {
    description = "Snowflake admin password"
    type        = string
    sensitive   = true
}
