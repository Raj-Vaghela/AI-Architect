/**
 * React hook for managing conversations
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/components/AuthProvider';
import {
    getConversations,
    saveConversation,
    updateConversation as updateStoredConversation,
    deleteConversation as deleteStoredConversation
} from '@/lib/conversationStorage';
import { getConfig } from '@/lib/config';
import { getAuthHeaders } from '@/lib/auth-utils';
import type { StoredConversation } from '@/lib/types';

export function useConversations() {
    const { user } = useAuth();
    const [conversations, setConversations] = useState<StoredConversation[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // Load conversations when user changes
    useEffect(() => {
        if (!user?.id) {
            setConversations([]);
            setIsLoading(false);
            return;
        }

        async function loadConversations() {
            setIsLoading(true);
            try {
                // Try to fetch from backend
                const headers = await getAuthHeaders();
                const config = getConfig();
                const response = await fetch(`${config.backendUrl}/api/v1/chat`, {
                    headers,
                });

                if (response.ok) {
                    const data = await response.json();
                    const backendConversations: StoredConversation[] = data.conversations.map((conv: any) => ({
                        id: conv.id,
                        title: conv.title || 'New Conversation',
                        userId: user.id,
                        createdAt: conv.created_at,
                        lastUpdatedAt: conv.updated_at,
                    }));
                    
                    setConversations(backendConversations);
                    setIsLoading(false);
                    return;
                }
            } catch (error) {
                console.error('Failed to fetch conversations from backend:', error);
            }

            // Fallback to localStorage
            const loaded = getConversations(user.id);
            setConversations(loaded);
            setIsLoading(false);
        }

        loadConversations();
    }, [user?.id]);

    const addConversation = useCallback(
        (conversation: StoredConversation) => {
            if (!user?.id) return;

            saveConversation(user.id, conversation);
            setConversations(prev => [conversation, ...prev]);
        },
        [user?.id]
    );

    const updateConversation = useCallback(
        (conversationId: string, updates: Partial<StoredConversation>) => {
            if (!user?.id) return;

            updateStoredConversation(user.id, conversationId, updates);
            setConversations(prev =>
                prev.map(c => (c.id === conversationId ? { ...c, ...updates } : c))
            );
        },
        [user?.id]
    );

    const deleteConversation = useCallback(
        async (conversationId: string) => {
            if (!user?.id) return;

            try {
                // Delete from backend first
                const headers = await getAuthHeaders();
                const config = getConfig();
                const response = await fetch(`${config.backendUrl}/api/v1/chat/${conversationId}`, {
                    method: 'DELETE',
                    headers,
                });

                if (response.ok) {
                    // Delete from localStorage
                    deleteStoredConversation(user.id, conversationId);
                    // Update UI
                    setConversations(prev => prev.filter(c => c.id !== conversationId));
                    return;
                } else {
                    console.error('Failed to delete conversation from backend:', await response.text());
                }
            } catch (error) {
                console.error('Error deleting conversation:', error);
            }

            // Fallback: delete from localStorage only
            deleteStoredConversation(user.id, conversationId);
            setConversations(prev => prev.filter(c => c.id !== conversationId));
        },
        [user?.id]
    );

    const getConversationById = useCallback(
        (conversationId: string) => {
            return conversations.find(c => c.id === conversationId);
        },
        [conversations]
    );

    return {
        conversations,
        isLoading,
        addConversation,
        updateConversation,
        deleteConversation,
        getConversationById
    };
}
