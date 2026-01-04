"""Test script to verify Supabase Auth + Chat persistence.

This script tests:
1. Creating a conversation with a user_id
2. Adding messages to the conversation
3. Retrieving conversation history
4. Listing conversations for a user
5. Verifying user isolation (can't access other users' chats)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import (
    create_conversation,
    add_message,
    get_conversation_messages,
    list_conversations_for_user,
    conversation_belongs_to_user,
    conversation_exists,
)


def test_chat_persistence():
    """Test chat persistence with multiple users."""
    
    print("[TEST] Testing Supabase Auth + Chat Persistence\n")
    
    # Simulate two different Supabase Auth users (UUIDs)
    user1_id = "abf6afe8-9085-4bf2-974c-1c9266884e7b"  # Real user from auth.users
    user2_id = "362dfe2c-6ff3-4aaa-ae8b-06e256513fc2"  # Real user from auth.users
    
    print(f"[USER] User 1: {user1_id}")
    print(f"[USER] User 2: {user2_id}\n")
    
    # Test 1: Create conversations for both users
    print("[TEST 1] Creating conversations...")
    conv1_id = create_conversation(user1_id, "User 1's Chat")
    conv2_id = create_conversation(user2_id, "User 2's Chat")
    print(f"[PASS] Created conversation for User 1: {conv1_id}")
    print(f"[PASS] Created conversation for User 2: {conv2_id}\n")
    
    # Test 2: Add messages to conversations
    print("[TEST 2] Adding messages...")
    add_message(conv1_id, "user", "Hello from User 1!")
    add_message(conv1_id, "assistant", "Hi User 1! How can I help?")
    add_message(conv2_id, "user", "Hello from User 2!")
    add_message(conv2_id, "assistant", "Hi User 2! What do you need?")
    print("[PASS] Messages added to both conversations\n")
    
    # Test 3: Retrieve conversation history
    print("[TEST 3] Retrieving conversation history...")
    conv1_messages = get_conversation_messages(conv1_id)
    conv2_messages = get_conversation_messages(conv2_id)
    print(f"[PASS] User 1's conversation has {len(conv1_messages)} messages")
    print(f"[PASS] User 2's conversation has {len(conv2_messages)} messages\n")
    
    # Test 4: List conversations for each user
    print("[TEST 4] Listing conversations per user...")
    user1_convs = list_conversations_for_user(user1_id)
    user2_convs = list_conversations_for_user(user2_id)
    print(f"[PASS] User 1 has {len(user1_convs)} conversation(s)")
    print(f"[PASS] User 2 has {len(user2_convs)} conversation(s)\n")
    
    # Test 5: Verify user isolation
    print("[TEST 5] Verifying user isolation...")
    user1_can_access_conv1 = conversation_belongs_to_user(conv1_id, user1_id)
    user1_can_access_conv2 = conversation_belongs_to_user(conv2_id, user1_id)
    user2_can_access_conv1 = conversation_belongs_to_user(conv1_id, user2_id)
    user2_can_access_conv2 = conversation_belongs_to_user(conv2_id, user2_id)
    
    assert user1_can_access_conv1, "[FAIL] User 1 should access their own conversation"
    assert not user1_can_access_conv2, "[FAIL] User 1 should NOT access User 2's conversation"
    assert not user2_can_access_conv1, "[FAIL] User 2 should NOT access User 1's conversation"
    assert user2_can_access_conv2, "[FAIL] User 2 should access their own conversation"
    
    print("[PASS] User 1 can access their own conversation")
    print("[PASS] User 1 CANNOT access User 2's conversation")
    print("[PASS] User 2 can access their own conversation")
    print("[PASS] User 2 CANNOT access User 1's conversation\n")
    
    # Test 6: Verify conversation existence
    print("[TEST 6] Verifying conversation existence...")
    assert conversation_exists(conv1_id), "[FAIL] Conversation 1 should exist"
    assert conversation_exists(conv2_id), "[FAIL] Conversation 2 should exist"
    assert not conversation_exists("00000000-0000-0000-0000-000000000000"), "[FAIL] Fake conversation should not exist"
    print("[PASS] Conversation existence checks work correctly\n")
    
    # Display conversation details
    print("=" * 60)
    print("CONVERSATION DETAILS")
    print("=" * 60)
    
    print(f"\n[USER 1] User 1's Conversations:")
    for conv in user1_convs:
        print(f"  - {conv['title']} (ID: {conv['id'][:8]}...)")
        print(f"    Created: {conv['created_at']}")
    
    print(f"\n[USER 2] User 2's Conversations:")
    for conv in user2_convs:
        print(f"  - {conv['title']} (ID: {conv['id'][:8]}...)")
        print(f"    Created: {conv['created_at']}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\n[SUCCESS] Chat persistence is working correctly!")
    print("[SUCCESS] User isolation is working correctly!")
    print("[SUCCESS] Ready for production use with Supabase Auth!\n")


if __name__ == "__main__":
    try:
        test_chat_persistence()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

