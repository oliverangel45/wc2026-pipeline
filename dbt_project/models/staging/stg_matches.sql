WITH raw_matches AS (
    SELECT *
    FROM {{ source('wc2026_raw', 'MATCHES') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY MATCH_ID
            ORDER BY LAST_UPDATED DESC
        ) AS row_num
    FROM raw_matches
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
        UTC_DATE::TIMESTAMP_TZ AS KICKOFF_TIME,
        LAST_UPDATED::TIMESTAMP_TZ AS LAST_UPDATED,
        INGESTED_AT
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final