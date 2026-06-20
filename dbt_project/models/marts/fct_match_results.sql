{{
    config(
        materialized='incremental',
        unique_key-'MATCH_ID'
    )
}}

WITH matches AS (
    SELECT * FROM {{ ref('stg_matches') }}
),

final AS (
    SELECT
        MATCH_ID,
        HOME_TEAM,
        AWAY_TEAM,
        HOME_SCORE,
        AWAY_SCORE,
        STATUS,
        MATCHDAY,
        STAGE,
        KICKOFF_TIME,
        CONVERT_TIMEZONE('UTC', 'Europe/London', KICKOFF_TIME) AS KICKOFF_TIME_BST,
        LAST_UPDATED
    FROM matches
    {% if is_incremental() %}
    WHERE LAST_UPDATED > (SELECT MAX(LAST_UPDATED) FROM {{ this }})
    {% endif %}
)

SELECT * FROM final