WITH step1 AS (
    SELECT 
        account_name,
        account_type,
        date,
        balance
    FROM master m1
    WHERE master_id = (
        SELECT MAX(master_id)
        FROM master m2 
        WHERE m1.account_name = m2.account_name
        AND m1.account_type = m2.account_type
        AND m1.date = m2.date
    )
    ORDER BY date
),
date_spine AS (
    SELECT *
    FROM GENERATE_SERIES(
        (SELECT MIN(date) FROM master), 
        CAST(CURRENT_DATE AS DATETIME),
        INTERVAL 1 DAY
    ) 
),
accounts AS (
    SELECT DISTINCT account_name, account_type
    FROM master
),
joined AS (
    SELECT 
        d.generate_series AS day,
        a.account_name,
        a.account_type,
        s.balance
    FROM date_spine d 
    CROSS JOIN accounts a
    LEFT JOIN step1 s ON d.generate_series = s.date
    AND a.account_name = s.account_name
    AND a.account_type = s.account_type
    ORDER BY d.generate_series
),
filled AS (
    SELECT 
        day,
        account_name,
        account_type,
        LAST_VALUE(balance IGNORE NULLS) OVER (
            PARTITION BY account_name, account_type
            ORDER BY day
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS balance
    FROM joined
)
SELECT day, SUM(balance) AS net_worth
FROM filled
GROUP BY day
ORDER BY day;