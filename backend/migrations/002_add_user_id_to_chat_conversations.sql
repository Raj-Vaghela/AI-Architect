-- Migration: Add user_id to chat conversations for per-user chat history
-- Description: Enables listing and access control of conversations by user.
-- NOTE: We keep user_id nullable to avoid breaking existing rows.
-- Apply with:
--   psql $SUPABASE_DB_URL -f migrations/002_add_user_id_to_chat_conversations.sql

ALTER TABLE chat.conversations
ADD COLUMN IF NOT EXISTS user_id TEXT;

-- Optional: backfill existing conversations to a default user bucket
-- (safe, but you can comment this out if you prefer NULLs)
UPDATE chat.conversations
SET user_id = 'legacy'
WHERE user_id IS NULL;

-- Indexes for fast listing
CREATE INDEX IF NOT EXISTS idx_conversations_user_created_at
ON chat.conversations (user_id, created_at DESC);

-- Helpful comment
COMMENT ON COLUMN chat.conversations.user_id IS 'Application user identifier owning this conversation (e.g., Supabase auth user id).';



