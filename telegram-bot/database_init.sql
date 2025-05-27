-- CogniCraft AI Database Schema
-- Run this in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX idx_users_telegram_id ON users(telegram_id);

-- Commands table (stores all command executions)
CREATE TABLE IF NOT EXISTS commands (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    command_type VARCHAR(50) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    file_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_commands_user_id ON commands(user_id);
CREATE INDEX idx_commands_type ON commands(command_type);
CREATE INDEX idx_commands_created_at ON commands(created_at DESC);

-- User states table (tracks current user state)
CREATE TABLE IF NOT EXISTS user_states (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_command VARCHAR(50),
    last_command_id INTEGER REFERENCES commands(id) ON DELETE SET NULL,
    state_data JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Function to update last_active timestamp
CREATE OR REPLACE FUNCTION update_user_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET last_active = NOW() 
    WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update last_active when user executes a command
CREATE TRIGGER update_last_active_on_command
AFTER INSERT ON commands
FOR EACH ROW
EXECUTE FUNCTION update_user_last_active();

-- Function to clean up old user states
CREATE OR REPLACE FUNCTION cleanup_old_states()
RETURNS void AS $$
BEGIN
    DELETE FROM user_states
    WHERE updated_at < NOW() - INTERVAL '7 days'
    AND current_command IS NULL;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security (RLS) - Optional but recommended
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE commands ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_states ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth setup)
-- Example: Allow authenticated users to read their own data
-- CREATE POLICY "Users can read own data" ON users
--     FOR SELECT USING (auth.uid()::text = telegram_id::text);

-- Sample data for testing (optional)
-- INSERT INTO users (telegram_id, username) VALUES 
-- (123456789, 'test_user');

-- Grant permissions (adjust based on your Supabase setup)
GRANT ALL ON users TO authenticated;
GRANT ALL ON commands TO authenticated;
GRANT ALL ON user_states TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;