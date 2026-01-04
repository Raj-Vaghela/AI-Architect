import {
    Plus,
    LogOut,
    PanelLeftClose,
    PanelLeftOpen,
    MessageSquareText,
    UserCircle2,
    Trash2
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAuth } from './AuthProvider';
import { useState } from 'react';
import ConfirmationModal from './ConfirmationModal';

import type { StoredConversation } from '@/lib/types';

// Helper function to format relative time
function formatRelativeTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    // For older conversations, show the date
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

interface SidebarProps {
    conversations: StoredConversation[];
    activeId: string | null;
    onSelect: (id: string) => void;
    onNewChat: () => void;
    onDelete?: (id: string) => void;
    isOpen: boolean;
    isCollapsed?: boolean;
    onToggle: () => void;
}

export default function Sidebar({
    conversations,
    activeId,
    onSelect,
    onNewChat,
    onDelete,
    isOpen,
    isCollapsed = false,
    onToggle
}: SidebarProps) {
    const router = useRouter();
    const { user, signOut } = useAuth();
    const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
    const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

    if (!isOpen) {
        return null;
    }

    const handleSignOut = async () => {
        await signOut();
        router.push('/');
        setShowLogoutConfirm(false);
    };

    return (
        <>
            <div className={`flex-shrink-0 flex flex-col h-full border-r border-white/10 bg-black/20 backdrop-blur-md transition-all duration-300 ${isCollapsed ? 'items-center' : 'w-full'}`}>
                {/* Header */}
                <div className={`p-4 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'} border-b border-white/5 w-full`}>
                    {!isCollapsed && <div className="w-6 h-6" />} {/* Spacer */}
                    <button onClick={onToggle} className="text-s8-text-muted hover:text-white transition-colors">
                        {isCollapsed ? <PanelLeftOpen className="w-5 h-5" /> : <PanelLeftClose className="w-5 h-5" />}
                    </button>
                </div>

                {/* New Chat Action */}
                <div className="p-3 w-full">
                    <button
                        onClick={onNewChat}
                        className={`flex items-center gap-2 transition-all ${isCollapsed
                            ? 'justify-center w-10 h-10 p-0 rounded-full mx-auto bg-gradient-to-br from-s8-accent to-s8-accent-2 hover:opacity-90 shadow-lg shadow-s8-accent/20'
                            : 'glass-btn-secondary w-full justify-start hover:bg-white/10'}`}
                        title="New Chat"
                    >
                        <Plus className={isCollapsed ? "w-5 h-5 text-white" : "w-4 h-4"} />
                        {!isCollapsed && <span>New Chat</span>}
                    </button>
                </div>

                {/* Conversation List */}
                <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 scrollbar-thin scrollbar-thumb-white/10 hover:scrollbar-thumb-white/20 w-full">
                    {!isCollapsed && (
                        <div className="text-xs font-medium text-s8-text-muted mb-2 px-2 uppercase tracking-wider animate-in fade-in duration-300">
                            Recent
                        </div>
                    )}
                    {conversations.length === 0 ? (
                        !isCollapsed && (
                            <div className="px-2 py-4 text-xs text-s8-text-muted/50 text-center italic">
                                No conversations yet
                            </div>
                        )
                    ) : (
                        conversations.map((chat) => (
                            <div
                                key={chat.id}
                                className={`rounded-lg text-sm transition-all group flex items-center gap-2 overflow-hidden ${activeId === chat.id
                                    ? 'bg-white/10 text-white'
                                    : 'text-s8-text-muted hover:bg-white/5 hover:text-white'
                                    } ${isCollapsed ? 'justify-center w-10 h-10 p-0 mx-auto' : 'w-full'}`}
                            >
                                <button
                                    onClick={() => onSelect(chat.id)}
                                    className={`flex items-center gap-3 overflow-hidden ${isCollapsed ? 'justify-center w-10 h-10 p-0' : 'flex-1 text-left px-3 py-2'}`}
                                    title={isCollapsed ? `${chat.title}\n${formatRelativeTime(chat.createdAt)}` : undefined}
                                >
                                    <MessageSquareText className={`w-4 h-4 flex-shrink-0 ${activeId === chat.id ? 'text-white' : 'text-s8-text-muted group-hover:text-white'}`} />
                                    {!isCollapsed && (
                                        <div className="flex-1 min-w-0 overflow-hidden">
                                            <div className="truncate font-medium text-ellipsis">{chat.title}</div>
                                            <div className={`text-xs mt-0.5 ${activeId === chat.id ? 'text-white/60' : 'text-s8-text-muted/60'}`}>
                                                {formatRelativeTime(chat.createdAt)}
                                            </div>
                                        </div>
                                    )}
                                </button>
                                {!isCollapsed && onDelete && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setDeleteConfirmId(chat.id);
                                        }}
                                        className="p-2 opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 rounded transition-all"
                                        title="Delete conversation"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* User Section */}
                <div className={`p-4 border-t border-white/5 bg-black/10 w-full ${isCollapsed ? 'flex flex-col gap-4 items-center' : ''}`}>
                    <div className={`flex items-center gap-3 ${isCollapsed ? 'mb-0 justify-center' : 'mb-3'}`}>
                        {user?.email && user.email[0] ? (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-s8-accent to-s8-accent-2 flex items-center justify-center text-white font-bold text-xs ring-2 ring-white/10 flex-shrink-0">
                                {user.email[0].toUpperCase()}
                            </div>
                        ) : (
                            <UserCircle2 className="w-8 h-8 text-s8-text-muted" />
                        )}

                        {!isCollapsed && (
                            <div className="flex-1 overflow-hidden animate-in fade-in duration-300">
                                <div className="text-sm font-medium truncate">{user?.user_metadata?.full_name || 'User'}</div>
                                <div className="text-xs text-s8-text-muted truncate">{user?.email}</div>
                            </div>
                        )}
                    </div>

                    {/* Only show Logout button if collapsed or not (simplified) */}
                    <div className={`flex gap-1 animate-in fade-in duration-300 ${isCollapsed ? 'w-full justify-center' : ''}`}>
                        <button
                            onClick={() => setShowLogoutConfirm(true)}
                            className={`p-2 rounded-md hover:bg-red-500/10 text-s8-text-muted hover:text-red-400 transition-colors ${isCollapsed ? '' : 'flex-1 flex justify-center'}`}
                            title="Sign Out"
                        >
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            <ConfirmationModal
                isOpen={showLogoutConfirm}
                title="Sign Out"
                message="Are you sure you want to sign out?"
                confirmText="Sign Out"
                isDestructive={true}
                onConfirm={handleSignOut}
                onCancel={() => setShowLogoutConfirm(false)}
            />

            {deleteConfirmId && (
                <ConfirmationModal
                    isOpen={true}
                    title="Delete Conversation"
                    message="Are you sure you want to delete this conversation? This action cannot be undone."
                    confirmText="Delete"
                    isDestructive={true}
                    onConfirm={() => {
                        if (onDelete && deleteConfirmId) {
                            onDelete(deleteConfirmId);
                        }
                        setDeleteConfirmId(null);
                    }}
                    onCancel={() => setDeleteConfirmId(null)}
                />
            )}
        </>
    );
}
