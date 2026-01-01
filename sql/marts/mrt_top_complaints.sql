-- Create top complaints monthly mart
DROP TABLE IF EXISTS marts.top_complaints_monthly;

CREATE TABLE marts.top_complaints_monthly AS
WITH ranked_complaints AS (
    SELECT 
        DATE_TRUNC('month', created_date)::DATE AS month,
        borough,
        complaint_type,
        COUNT(*) AS requests,
        ROW_NUMBER() OVER (
            PARTITION BY DATE_TRUNC('month', created_date)::DATE, borough 
            ORDER BY COUNT(*) DESC
        ) AS rank
    FROM core.nyc311_requests_clean
    GROUP BY DATE_TRUNC('month', created_date)::DATE, borough, complaint_type
)
SELECT 
    month,
    borough,
    complaint_type,
    requests
FROM ranked_complaints
WHERE rank <= 10
ORDER BY month, borough, requests DESC;

