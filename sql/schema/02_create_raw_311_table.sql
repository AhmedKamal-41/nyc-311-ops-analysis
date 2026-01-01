-- Create raw table for NYC 311 requests
CREATE TABLE IF NOT EXISTS raw.nyc311_requests (
    unique_key BIGINT PRIMARY KEY,
    created_date TIMESTAMP,
    closed_date TIMESTAMP NULL,
    agency TEXT,
    complaint_type TEXT,
    descriptor TEXT,
    status TEXT,
    borough TEXT,
    incident_zip TEXT,
    city TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

