-- Fast Food Nutrition Agent - Supabase Database Schema
-- Production-ready PostgreSQL schema for Streamlit Share deployment

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- User preferences (JSONB for flexibility)
    dietary_restrictions TEXT[] DEFAULT '{}',
    favorite_restaurants TEXT[] DEFAULT '{}',
    default_calorie_target INTEGER DEFAULT 1200,
    preferred_cooking_methods TEXT[] DEFAULT '{}',
    disliked_items TEXT[] DEFAULT '{}',
    
    -- Statistics
    total_meals_tracked INTEGER DEFAULT 0,
    avg_daily_calories NUMERIC(10, 2) DEFAULT 0,
    avg_meal_rating NUMERIC(3, 2) DEFAULT 0,
    
    -- Metadata
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_calorie_target CHECK (default_calorie_target BETWEEN 300 AND 2000),
    CONSTRAINT valid_avg_rating CHECK (avg_meal_rating BETWEEN 0 AND 5)
);

-- Meal History Table
CREATE TABLE IF NOT EXISTS meal_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    
    -- Meal details
    restaurant VARCHAR(255) NOT NULL,
    calories INTEGER NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    
    -- Additional meal data (JSONB for future extensibility)
    meal_data JSONB DEFAULT '{}',
    
    -- Timestamps
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    CONSTRAINT valid_calories CHECK (calories BETWEEN 0 AND 5000)
);

-- API Usage Tracking (for cost control)
CREATE TABLE IF NOT EXISTS api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Usage details
    profile_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    model VARCHAR(100) NOT NULL,
    tokens_used INTEGER NOT NULL,
    estimated_cost NUMERIC(10, 6) NOT NULL,
    
    -- Request metadata
    request_type VARCHAR(50) NOT NULL, -- 'recommendation', 'insight', 'profile_analysis'
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- Timestamps
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Index for cost monitoring
    CONSTRAINT valid_cost CHECK (estimated_cost >= 0)
);

-- Error Logs (for monitoring)
CREATE TABLE IF NOT EXISTS error_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Error details
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    
    -- Context
    profile_id UUID REFERENCES user_profiles(id) ON DELETE SET NULL,
    user_input TEXT,
    
    -- Metadata
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    severity VARCHAR(20) DEFAULT 'error' CHECK (severity IN ('warning', 'error', 'critical'))
);

-- System Metrics (for monitoring)
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Metrics
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(20, 6) NOT NULL,
    metric_unit VARCHAR(50),
    
    -- Metadata
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tags JSONB DEFAULT '{}'
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_meal_history_profile_id ON meal_history(profile_id);
CREATE INDEX IF NOT EXISTS idx_meal_history_timestamp ON meal_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp ON api_usage(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_profile_id ON api_usage(profile_id);
CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_error_logs_severity ON error_logs(severity) WHERE resolved = FALSE;
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_profiles_name ON user_profiles(profile_name);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update profile statistics
CREATE OR REPLACE FUNCTION update_profile_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update statistics for the profile
    UPDATE user_profiles
    SET 
        total_meals_tracked = (
            SELECT COUNT(*) FROM meal_history WHERE profile_id = NEW.profile_id
        ),
        avg_daily_calories = (
            SELECT COALESCE(AVG(calories), 0) FROM meal_history WHERE profile_id = NEW.profile_id
        ),
        avg_meal_rating = (
            SELECT COALESCE(AVG(rating), 0) FROM meal_history WHERE profile_id = NEW.profile_id AND rating IS NOT NULL
        ),
        last_active = CURRENT_TIMESTAMP
    WHERE id = NEW.profile_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update profile stats when meal is added
CREATE TRIGGER update_stats_on_meal_insert
    AFTER INSERT ON meal_history
    FOR EACH ROW
    EXECUTE FUNCTION update_profile_stats();

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE error_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_metrics ENABLE ROW LEVEL SECURITY;

-- For now, allow all operations (since we're using service role key)
-- In production with auth, you'd restrict these policies
CREATE POLICY "Enable all access for service role" ON user_profiles FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON meal_history FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON api_usage FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON error_logs FOR ALL USING (true);
CREATE POLICY "Enable all access for service role" ON system_metrics FOR ALL USING (true);

-- Views for easy querying

-- Daily usage summary
CREATE OR REPLACE VIEW daily_usage_summary AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_requests,
    SUM(tokens_used) as total_tokens,
    SUM(estimated_cost) as total_cost,
    COUNT(DISTINCT profile_id) as unique_users,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_requests
FROM api_usage
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Profile activity summary
CREATE OR REPLACE VIEW profile_activity_summary AS
SELECT 
    p.profile_name,
    p.total_meals_tracked,
    p.avg_daily_calories,
    p.avg_meal_rating,
    COUNT(m.id) as recent_meals_count,
    MAX(m.timestamp) as last_meal_logged
FROM user_profiles p
LEFT JOIN meal_history m ON p.id = m.profile_id 
    AND m.timestamp > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY p.id, p.profile_name, p.total_meals_tracked, p.avg_daily_calories, p.avg_meal_rating
ORDER BY last_meal_logged DESC NULLS LAST;

-- Error rate monitoring
CREATE OR REPLACE VIEW error_rate_summary AS
SELECT 
    DATE(timestamp) as date,
    error_type,
    severity,
    COUNT(*) as error_count,
    COUNT(CASE WHEN resolved THEN 1 END) as resolved_count
FROM error_logs
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY DATE(timestamp), error_type, severity
ORDER BY date DESC, error_count DESC;

-- Cost monitoring view
CREATE OR REPLACE VIEW cost_monitoring AS
SELECT 
    DATE_TRUNC('day', timestamp) as day,
    model,
    COUNT(*) as request_count,
    SUM(tokens_used) as total_tokens,
    SUM(estimated_cost) as daily_cost,
    AVG(estimated_cost) as avg_cost_per_request
FROM api_usage
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', timestamp), model
ORDER BY day DESC, daily_cost DESC;

-- Comments for documentation
COMMENT ON TABLE user_profiles IS 'Stores user profile data including preferences and statistics';
COMMENT ON TABLE meal_history IS 'Tracks all meal recommendations and user ratings';
COMMENT ON TABLE api_usage IS 'Monitors OpenAI API usage for cost control';
COMMENT ON TABLE error_logs IS 'Stores application errors for monitoring and debugging';
COMMENT ON TABLE system_metrics IS 'Tracks system performance metrics';

COMMENT ON COLUMN user_profiles.dietary_restrictions IS 'Array of dietary restrictions (e.g., vegetarian, gluten-free)';
COMMENT ON COLUMN user_profiles.favorite_restaurants IS 'Array of frequently visited restaurants';
COMMENT ON COLUMN api_usage.estimated_cost IS 'Estimated cost in USD for the API call';
COMMENT ON COLUMN error_logs.severity IS 'Error severity level: warning, error, or critical';

