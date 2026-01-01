-- Build all marts in order
-- This file creates all mart tables

-- ============================================
-- 1. KPI Monthly Mart
-- ============================================
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

-- ============================================
-- 2. Top Complaints Monthly Mart
-- ============================================
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

-- ============================================
-- 3. Agency Performance Monthly Mart
-- ============================================
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
