{{
    config(
        materialized='incremental',
        unique_key-'PLAYER_NAME'
    )
}}

WITH events AS (
    SELECT * FROM {{ ref('stg_events') }}
),

goals_only AS (
    SELECT
        PLAYER_NAME,
        TEAM_NAME,
        TEAM_ID,
        EVENT_DETAIL
    FROM events
    WHERE EVENT_TYPE = 'GOAL' AND PLAYER_NAME IS NOT NULL
),

goal_counts AS (
    SELECT
        PLAYER_NAME,
        TEAM_NAME,
        TEAM_ID,
        COUNT(*) AS GOALS_SCORED,
        SUM(CASE WHEN EVENT_DETAIL = 'OWN_GOAL' THEN 1 ELSE 0 END) AS OWN_GOALS,
        SUM(CASE WHEN EVENT_DETAIL = 'PENALTY' THEN 1 ELSE 0 END) AS PENALTIES,
        SUM(CASE WHEN EVENT_DETAIL = 'NORMAL_GOAL' THEN 1 ELSE 0 END) AS NORMAL_GOALS
    FROM goals_only
    GROUP BY PLAYER_NAME, TEAM_NAME, TEAM_ID
),

scorers_to_teams AS (
    SELECT
        g.PLAYER_NAME,
        g.TEAM_NAME,
        g.GOALS_SCORED,
        -- g.OWN_GOALS,
        g.PENALTIES,
        g.NORMAL_GOALS,
        t.FLAG,
        t.COUNTRY_CODE
    FROM goal_counts g
    LEFT JOIN {{ ref('teams') }} t ON g.TEAM_ID = t.TEAM_ID
),

final AS (
    SELECT
        PLAYER_NAME,
        TEAM_NAME,
        FLAG,
        COUNTRY_CODE,
        GOALS_SCORED,
        -- OWN_GOALS,
        PENALTIES,
        NORMAL_GOALS,
        -- GOALS_SCORED - OWN_GOALS AS COMPETITIVE_GOALS
    FROM scorers_to_teams
    -- Incremental Logic: Only process new data after inital dbt run
    {% if is_incremental() %}
    WHERE PLAYER_NAME NOT IN (
        SELECT PLAYER_NAME FROM {{ this }}
        WHERE GOALS_SCORED >= (
            SELECT MAX(GOALS_SCORED) FROM {{ this }}
        )
    )
    OR PLAYER_NAME IN (
        SELECT PLAYER_NAME FROM {{ this }}
    )
    {% endif %}
)

SELECT * FROM final
ORDER BY GOALS_SCORED DESC