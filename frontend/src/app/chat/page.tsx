'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ThemeBackground from '@/components/ThemeBackground';
import Sidebar from '@/components/Sidebar';
import ChatWindow from '@/components/ChatWindow';
import { useAuth } from '@/components/AuthProvider';
import { useConversations } from '@/hooks/useConversations';
import { backendAPI, BackendAPIError } from '@/lib/backend';
import type { Message } from '@/lib/types';

function generateTitle(firstMessage: string): string {
    // Generate a short title from the first message
    const trimmed = firstMessage.trim();
    if (trimmed.length <= 50) return trimmed;
    return trimmed.substring(0, 47) + '...';
}

export default function ChatPage() {
    const router = useRouter();
    const { user, isLoading: authLoading } = useAuth();
    const {
        conversations,
        isLoading: conversationsLoading,
        addConversation,
        updateConversation,
        deleteConversation
    } = useConversations();

    // State
    const [activeChatId, setActiveChatId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Redirect if not logged in
    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/');
        }
    }, [authLoading, user, router]);

    // Load messages when conversation changes
    useEffect(() => {
        if (!activeChatId) {
            setMessages([]);
            return;
        }

        loadConversationHistory(activeChatId);
    }, [activeChatId]);

    async function loadConversationHistory(conversationId: string) {
        try {
            setError(null);
            const response = await backendAPI.getHistory(conversationId);

            const loadedMessages: Message[] = response.messages.map(msg => ({
                id: msg.id,
                role: msg.role,
                content: msg.content,
                timestamp: new Date(msg.created_at),
                metadata: undefined // Backend doesn't return metadata in history
            }));

            setMessages(loadedMessages);
        } catch (err) {
            console.error('Error loading conversation history:', err);
            if (err instanceof BackendAPIError && err.status === 404) {
                // Conversation not found - remove from local storage
                setError('Conversation not found');
                setActiveChatId(null);
            } else {
                setError('Failed to load conversation history');
            }
        }
    }

    const handleSendMessage = async (text: string) => {
        if (!user) return;

        setError(null);

        // If no active conversation, create one first
        if (!activeChatId) {
            await handleNewChat(text);
            return;
        }

        // Optimistic User Message
        const userMsg: Message = {
            id: `temp-${Date.now()}`,
            role: 'user',
            content: text,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setIsTyping(true);

        try {
            const response = await backendAPI.sendMessage(activeChatId, text);

            // Replace optimistic message with real one
            setMessages(prev => {
                const withoutTemp = prev.filter(m => m.id !== userMsg.id);
                return [
                    ...withoutTemp,
                    {
                        id: `${Date.now()}-user`,
                        role: 'user' as const,
                        content: text,
                        timestamp: new Date()
                    },
                    {
                        id: `${Date.now()}-assistant`,
                        role: 'assistant' as const,
                        content: response.response,
                        timestamp: new Date(),
                        metadata: {
                            type: response.response_type,
                            deployment_plan: response.deployment_plan || undefined
                        }
                    }
                ];
            });

            // Update conversation's lastUpdatedAt
            updateConversation(activeChatId, {
                lastUpdatedAt: new Date().toISOString()
            });
        } catch (err) {
            console.error('Error sending message:', err);
            setError(err instanceof BackendAPIError ? err.message : 'Failed to send message');

            // Remove optimistic message on error
            setMessages(prev => prev.filter(m => m.id !== userMsg.id));
        } finally {
            setIsTyping(false);
        }
    };

    const handleNewChat = async (firstMessage?: string) => {
        if (!user) return;

        try {
            setError(null);
            setIsTyping(true);

            // Create conversation on backend
            const response = await backendAPI.startConversation();
            const conversationId = response.conversation_id;

            // Generate title
            const title = firstMessage ? generateTitle(firstMessage) : 'New conversation';

            // Store in localStorage
            addConversation({
                id: conversationId,
                title,
                userId: user.id,
                createdAt: new Date().toISOString(),
                lastUpdatedAt: new Date().toISOString()
            });

            // Set as active
            setActiveChatId(conversationId);
            setMessages([]);

            // If there was a first message, send it
            if (firstMessage) {
                // Wait for activeChatId to be set, then send
                setTimeout(async () => {
                    const userMsg: Message = {
                        id: `temp-${Date.now()}`,
                        role: 'user',
                        content: firstMessage,
                        timestamp: new Date()
                    };

                    setMessages([userMsg]);

                    try {
                        const msgResponse = await backendAPI.sendMessage(conversationId, firstMessage);

                        setMessages([
                            {
                                id: `${Date.now()}-user`,
                                role: 'user',
                                content: firstMessage,
                                timestamp: new Date()
                            },
                            {
                                id: `${Date.now()}-assistant`,
                                role: 'assistant',
                                content: msgResponse.response,
                                timestamp: new Date(),
                                metadata: {
                                    type: msgResponse.response_type,
                                    deployment_plan: msgResponse.deployment_plan || undefined
                                }
                            }
                        ]);
                    } catch (err) {
                        console.error('Error sending initial message:', err);
                        setError('Failed to send first message');
                        setMessages([]);
                    } finally {
                        setIsTyping(false);
                    }
                }, 100);
            } else {
                setIsTyping(false);
            }
        } catch (err) {
            console.error('Error creating conversation:', err);
            setError('Failed to create new conversation');
            setIsTyping(false);
        }
    };

    const handleSelectConversation = (conversationId: string) => {
        setActiveChatId(conversationId);
    };

    const handleDeleteConversation = async (conversationId: string) => {
        // If deleting the active conversation, clear it
        if (activeChatId === conversationId) {
            setActiveChatId(null);
            setMessages([]);
        }
        
        // Delete from backend and localStorage
        await deleteConversation(conversationId);
    };

    // Show loading while checking auth
    if (authLoading || conversationsLoading) {
        return (
            <main className="flex h-screen w-full items-center justify-center text-s8-text font-sans">
                <ThemeBackground />
                <div className="text-xl">Loading...</div>
            </main>
        );
    }

    // If not logged in (should redirect, but show nothing meanwhile)
    if (!user) {
        return null;
    }

    return (
        <main className="flex h-screen w-full overflow-hidden relative text-s8-text font-sans selection:bg-s8-accent/30">
            <ThemeBackground />

            {/* Sidebar Wrapper */}
            <div
                className={`
                    flex-shrink-0 bg-transparent h-full z-30 transition-all duration-300 ease-in-out
                    fixed lg:relative
                    ${sidebarOpen ? 'translate-x-0 lg:w-64' : '-translate-x-full lg:translate-x-0 lg:w-20'}
                `}
            >
                <div className={`h-full ${sidebarOpen ? 'w-64' : 'w-20'} transition-all duration-300`}>
                    <Sidebar
                        conversations={conversations}
                        activeId={activeChatId}
                        onSelect={handleSelectConversation}
                        onNewChat={() => handleNewChat()}
                        onDelete={handleDeleteConversation}
                        isOpen={true}
                        isCollapsed={!sidebarOpen}
                        onToggle={() => setSidebarOpen(!sidebarOpen)}
                    />
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col min-w-0 bg-black/5 relative z-10 w-full">
                <ChatWindow
                    activeChat={null}
                    messages={messages}
                    isTyping={isTyping}
                    onSendMessage={handleSendMessage}
                    onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
                    sidebarOpen={sidebarOpen}
                />

                {/* Error Toast */}
                {error && (
                    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-50 bg-red-500/90 text-white px-4 py-2 rounded-lg shadow-lg">
                        {error}
                    </div>
                )}
            </div>

            {/* Mobile Overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-20 lg:hidden backdrop-blur-sm"
                    onClick={() => setSidebarOpen(false)}
                />
            )}
        </main>
    );
}
