WITH lead_lag_data AS (
    SELECT
        *,
        response -> 'market_data' -> 'market_cap' ->> 'usd' AS market_cap,
        LAG(price, 1) OVER (PARTITION BY coin_id ORDER BY date) AS price_p1,
        LEAD(price, 1) OVER (PARTITION BY coin_id ORDER BY date) AS price_f1,
        ROW_NUMBER() OVER (PARTITION BY coin_id ORDER BY date DESC) AS rank
    FROM
        coin_raw
    WHERE
        date >= '2022-01-01'
        AND date <= '2022-04-14'
),
cumulative_drops_data AS (
    SELECT
        *,
        CASE WHEN price < price_p1 THEN
            1
        ELSE
            0
        END AS price_drop,
        SUM(
            CASE WHEN price < price_p1 THEN
                1
            ELSE
                0
            END) OVER (PARTITION BY coin_id ORDER BY date ROWS BETWEEN 2 PRECEDING AND 0 FOLLOWING) AS cumulative_drops,
        CASE WHEN SUM(
            CASE WHEN price < price_p1 THEN
                1
            ELSE
                0
            END) OVER (PARTITION BY coin_id ORDER BY date ROWS BETWEEN 2 PRECEDING AND 0 FOLLOWING) = 3
            AND price_f1 > price THEN
            1
        ELSE
            0
        END AS increase_after_consecutive_drops
    FROM
        lead_lag_data
)
SELECT
    coin_id,
    avg(
        CASE WHEN increase_after_consecutive_drops = 1 THEN
            price_f1 - price
        END) AS avg_nominal_increase,
    avg(
        CASE WHEN increase_after_consecutive_drops = 1 THEN
            (price_f1 - price) / price
        END) AS avg_percentage_increase,
    avg(
        CASE WHEN rank = 1 THEN
            cast(market_cap AS float)
        END) AS current_market_cap
FROM
    cumulative_drops_data
GROUP BY
    1
