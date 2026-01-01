-- Create cleaned core table from raw NYC 311 data
DROP TABLE IF EXISTS core.nyc311_requests_clean;

CREATE TABLE core.nyc311_requests_clean AS
SELECT 
    unique_key,
    created_date,
    closed_date,
    agency,
    complaint_type,
    descriptor,
    status,
    UPPER(borough) AS borough,
    incident_zip,
    city,
    latitude,
    longitude,
    CASE 
        WHEN closed_date IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (closed_date - created_date)) / 3600.0
        ELSE NULL
    END AS resolution_hours
FROM raw.nyc311_requests
WHERE created_date IS NOT NULL;

-- Add indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_nyc311_clean_created_date 
    ON core.nyc311_requests_clean(created_date);

CREATE INDEX IF NOT EXISTS idx_nyc311_clean_complaint_type 
    ON core.nyc311_requests_clean(complaint_type);

CREATE INDEX IF NOT EXISTS idx_nyc311_clean_borough 
    ON core.nyc311_requests_clean(borough);

