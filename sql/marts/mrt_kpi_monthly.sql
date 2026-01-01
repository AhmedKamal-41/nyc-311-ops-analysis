-- Create KPI monthly mart
DROP TABLE IF EXISTS marts.kpi_monthly;

CREATE TABLE marts.kpi_monthly AS
SELECT 
    DATE_TRUNC('month', created_date)::DATE AS month,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE closed_date IS NULL) AS open_requests,
    COUNT(*) FILTER (WHERE closed_date IS NOT NULL) AS closed_requests,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resolution_hours) 
        FILTER (WHERE closed_date IS NOT NULL) AS median_resolution_hours,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY resolution_hours) 
        FILTER (WHERE closed_date IS NOT NULL) AS p90_resolution_hours
FROM core.nyc311_requests_clean
GROUP BY DATE_TRUNC('month', created_date)::DATE
ORDER BY month;

