-- dim_third_place_standings.sql
-- Ranks all 12 third-place finishers to determine the 8 who advance
{{
    config(
        materialized='incremental',
        unique_key='TEAM_ID'
    )
}}

WITH third_place_teams AS (
    SELECT *
    FROM {{ ref('dim_group_standings') }}
    WHERE POSITION = 3
),

final AS (
    SELECT
        TEAM_ID,
        TEAM_NAME,
        FLAG_EMOJI,
        COUNTRY_CODE,
        CONFEDERATION,
        GROUP_NAME,
        PLAYED_GAMES,
        WON,
        DRAW,
        LOST,
        POINTS,
        GOALS_FOR,
        GOALS_AGAINST,
        GOAL_DIFF,
        INGESTED_AT
    FROM third_place_teams
    {% if is_incremental() %}
    WHERE INGESTED_AT > (SELECT MAX(INGESTED_AT) FROM {{ this }})
    {% endif %}
)

SELECT * FROM final
ORDER BY POINTS DESC, GOAL_DIFF DESC, GOALS_FOR DESC