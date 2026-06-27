{{
    config(
        materialized='incremental',
        unique_key='TEAM_ID'
    )
}}

WITH standings AS (
    SELECT * FROM {{ ref('stg_standings') }}
),

standings_to_teams AS (
    SELECT
        s.TEAM_ID,
        s.TEAM_NAME,
        s.GROUP_NAME,
        s.POSITION,
        s.PLAYED_GAMES,
        s.WON,
        s.DRAW,
        s.LOST,
        s.POINTS,
        s.GOALS_FOR,
        s.GOALS_AGAINST,
        s.GOAL_DIFF,
        s.INGESTED_AT,
        s.CREST_URL,
        t.COUNTRY_CODE,
        t.CONFEDERATION
    FROM standings s
    LEFT JOIN {{ ref('teams') }} t ON s.TEAM_ID = t.TEAM_ID
),

final AS (
    SELECT
        TEAM_ID,
        TEAM_NAME,
        CREST_URL,
        COUNTRY_CODE,
        CONFEDERATION,
        GROUP_NAME,
        POSITION,
        PLAYED_GAMES,
        WON,
        DRAW,
        LOST,
        POINTS,
        GOALS_FOR,
        GOALS_AGAINST,
        GOAL_DIFF,
        INGESTED_AT 
    FROM standings_to_teams
    -- Incremental Logic
    {% if is_incremental() %}
    WHERE INGESTED_AT > (SELECT MAX(INGESTED_AT) FROM {{ this }})
    {% endif %}
)

SELECT * FROM final
ORDER BY GROUP_NAME, POSITION