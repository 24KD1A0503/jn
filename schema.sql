-- JatayuNetra Database Schema
CREATE EXTENSION IF NOT EXISTS postgis;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    token_id VARCHAR(50) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('tourist', 'police', 'hospital', 'tourism')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Demo users (passwords match the login credentials)
INSERT INTO users (token_id, username, full_name, email, password_hash, role) VALUES
('TOURIST-123', 'priya_sharma', 'Priya Sharma', 'priya@demo.com', 'Tourist@123', 'tourist'),
('POLICE-456', 'officer_singh', 'Officer Singh', 'singh@police.demo', 'Police@789', 'police'),
('HOSPITAL-789', 'dr_patel', 'Dr. Patel', 'patel@hospital.demo', 'Doctor@101', 'hospital'),
('TOURISM-101', 'tourism_admin', 'Tourism Admin', 'admin@tourism.demo', 'Tourism@202', 'tourism')
ON CONFLICT (username) DO NOTHING;