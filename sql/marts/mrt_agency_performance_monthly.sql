-- Create agency performance monthly mart
DROP TABLE IF EXISTS marts.agency_performance_monthly;

CREATE TABLE marts.agency_performance_monthly AS
SELECT 
    DATE_TRUNC('month', created_date)::DATE AS month,
    agency,
    COUNT(*) AS requests,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resolution_hours) 
        FILTER (WHERE closed_date IS NOT NULL) AS median_resolution_hours,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY resolution_hours) 
        FILTER (WHERE closed_date IS NOT NULL) AS p90_resolution_hours
FROM core.nyc311_requests_clean
GROUP BY DATE_TRUNC('month', created_date)::DATE, agency
ORDER BY month, agency;

