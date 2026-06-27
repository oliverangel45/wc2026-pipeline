WITH raw_standings AS (
    SELECT *
    FROM {{ source('wc2026_raw', 'STANDINGS') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY TEAM_ID
            ORDER BY INGESTED_AT DESC
        ) AS row_num
    FROM raw_standings
),

final AS (
    SELECT
        TEAM_ID,
        TEAM_NAME,
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
        RAW_PAYLOAD:raw_payload:team:crest::STRING AS CREST_URL,
        INGESTED_AT
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final