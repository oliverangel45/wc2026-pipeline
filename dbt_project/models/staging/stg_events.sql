WITH raw_events AS (
    SELECT *
    FROM {{ source('wc2026_raw', 'EVENTS') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY EVENT_ID
            ORDER BY INGESTED_AT DESC
        ) AS row_num
    FROM raw_events
),

final AS (
    SELECT
        EVENT_ID,
        MATCH_ID,
        MINUTE,
        EXTRA_TIME_MINUTE,
        EVENT_TYPE,
        EVENT_DETAIL,
        TEAM_ID,
        TEAM_NAME,
        PLAYER_NAME,
        ASSIST_NAME,
        INGESTED_AT
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final