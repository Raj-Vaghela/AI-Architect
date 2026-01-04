"""Test script to verify chat deletion functionality."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import (
    create_conversation,
    add_message,
    delete_conversation,
    list_conversations_for_user,
    conversation_exists,
)


def test_delete_functionality():
    """Test chat deletion with ownership verification."""
    
    print("[TEST] Testing Chat Deletion Functionality\n")
    
    # Use real Supabase Auth user ID
    user1_id = "abf6afe8-9085-4bf2-974c-1c9266884e7b"
    user2_id = "362dfe2c-6ff3-4aaa-ae8b-06e256513fc2"
    
    print(f"[USER 1] {user1_id}")
    print(f"[USER 2] {user2_id}\n")
    
    # Test 1: Create conversation
    print("[TEST 1] Creating conversation for User 1...")
    conv_id = create_conversation(user1_id, "Test Conversation to Delete")
    print(f"[PASS] Created conversation: {conv_id}\n")
    
    # Test 2: Add messages
    print("[TEST 2] Adding messages...")
    add_message(conv_id, "user", "Test message 1")
    add_message(conv_id, "assistant", "Test response 1")
    print("[PASS] Messages added\n")
    
    # Test 3: Verify conversation exists
    print("[TEST 3] Verifying conversation exists...")
    assert conversation_exists(conv_id), "[FAIL] Conversation should exist"
    print("[PASS] Conversation exists\n")
    
    # Test 4: User 2 cannot delete User 1's conversation
    print("[TEST 4] Testing ownership protection...")
    deleted_by_user2 = delete_conversation(conv_id, user2_id)
    assert not deleted_by_user2, "[FAIL] User 2 should NOT be able to delete User 1's conversation"
    assert conversation_exists(conv_id), "[FAIL] Conversation should still exist"
    print("[PASS] User 2 CANNOT delete User 1's conversation\n")
    
    # Test 5: User 1 can delete their own conversation
    print("[TEST 5] User 1 deleting their own conversation...")
    deleted_by_user1 = delete_conversation(conv_id, user1_id)
    assert deleted_by_user1, "[FAIL] User 1 should be able to delete their conversation"
    print("[PASS] Conversation deleted successfully\n")
    
    # Test 6: Verify conversation no longer exists
    print("[TEST 6] Verifying conversation is gone...")
    assert not conversation_exists(conv_id), "[FAIL] Conversation should not exist after deletion"
    print("[PASS] Conversation no longer exists\n")
    
    # Test 7: Messages should be cascade deleted
    print("[TEST 7] Verifying messages were cascade deleted...")
    from app.db import get_conversation_messages
    messages = get_conversation_messages(conv_id)
    assert len(messages) == 0, "[FAIL] Messages should be cascade deleted"
    print("[PASS] Messages were cascade deleted (foreign key constraint works)\n")
    
    print("=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\n[SUCCESS] Chat deletion is working correctly!")
    print("[SUCCESS] Ownership protection is working!")
    print("[SUCCESS] Cascade deletion is working!\n")


if __name__ == "__main__":
    try:
        test_delete_functionality()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


