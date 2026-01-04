-- Migration: Create chat schema for conversation memory
-- Description: Creates chat.conversations and chat.messages tables for multi-turn chat memory
-- Date: 2025-12-28

-- Create chat schema if not exists
CREATE SCHEMA IF NOT EXISTS chat;

-- Create conversations table
CREATE TABLE IF NOT EXISTS chat.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    title TEXT
);

-- Create messages table
CREATE TABLE IF NOT EXISTS chat.messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES chat.conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON chat.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON chat.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON chat.conversations(created_at);

-- Add updated_at trigger for conversations
CREATE OR REPLACE FUNCTION chat.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON chat.conversations
    FOR EACH ROW
    EXECUTE FUNCTION chat.update_updated_at_column();

-- Comments for documentation
COMMENT ON SCHEMA chat IS 'Chat conversation memory for multi-turn agent conversations';
COMMENT ON TABLE chat.conversations IS 'Chat conversations with metadata';
COMMENT ON TABLE chat.messages IS 'Individual messages within conversations';
COMMENT ON COLUMN chat.messages.role IS 'Message role: user, assistant, or system';

