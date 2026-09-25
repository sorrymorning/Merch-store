CREATE VIEW product_sales_mart AS
SELECT
    m.id AS merch_id,
    m.name AS product_name,
    m.price,
    SUM(ph.quantity) AS units_sold,
    COUNT(DISTINCT ph.user_id) AS buyers_count,
    SUM(ph.quantity * m.price) AS revenue
FROM purchase_history ph
JOIN merch m ON ph.merch_id = m.id
GROUP BY
    m.id,
    m.name,
    m.price;



SELECT *
FROM product_sales_mart
ORDER BY revenue DESC;