import MessageList from './MessageList';
import Composer from './Composer';
import { Menu, Wifi, WifiOff, PanelLeftOpen, PanelLeftClose } from 'lucide-react';

interface Message {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
}

interface ChatWindowProps {
    activeChat: unknown; // Simplified generic
    messages: Message[];
    isTyping: boolean;
    onSendMessage: (text: string) => void;
    onToggleSidebar: () => void;
    sidebarOpen: boolean;
    isConnected?: boolean;
}

export default function ChatWindow({
    messages,
    isTyping,
    onSendMessage,
    onToggleSidebar,
    sidebarOpen,
    isConnected = true
}: ChatWindowProps) {

    const isEmpty = messages.length === 0;

    return (
        <div className="flex-1 flex flex-col h-full bg-black/10 relative">
            {/* Header - Minimal */}
            <div className="absolute top-0 right-0 p-4 z-20 flex items-center gap-4">
                <div className={`px-2 py-0.5 rounded-full text-[10px] font-medium border flex items-center gap-1.5 ${isConnected
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-red-500/10 text-red-400 border-red-500/20'
                    }`}>
                    {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
                </div>
            </div>


            {/* Main Content Area */}
            <div className="flex-1 flex flex-col relative overflow-hidden">
                {isEmpty ? (
                    /* Empty State - Centered */
                    <div className="flex-1 flex flex-col items-center justify-center p-4 animate-in fade-in duration-500">
                        <div className="w-full max-w-2xl space-y-8 text-center pt-12">
                            <h2 className="text-3xl font-medium text-white/90">What are you working on?</h2>
                            <Composer onSend={onSendMessage} disabled={isTyping || !isConnected} centered={true} />
                        </div>
                    </div>
                ) : (
                    /* Active Chat State */
                    <>
                        <MessageList messages={messages} isTyping={isTyping} />
                        <div className="p-4 bg-gradient-to-t from-s8-bg via-s8-bg/80 to-transparent">
                            <div className="max-w-3xl mx-auto w-full">
                                <Composer onSend={onSendMessage} disabled={isTyping || !isConnected} />
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
