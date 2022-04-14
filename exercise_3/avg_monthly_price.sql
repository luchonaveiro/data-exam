SELECT
    coin_id,
    TO_CHAR(date, 'YYYY-MM-01') AS year_month,
    AVG(price) AS avg_price
FROM
    coin_raw
WHERE
    date >= '2022-01-01'
    AND date <= '2022-04-14'
GROUP BY
    1,
    2
ORDER BY
    1,
    2
