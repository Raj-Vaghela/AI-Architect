import { Message } from '@/lib/mockData';
import MessageBubble from './MessageBubble';
import { useRef, useEffect } from 'react';

interface MessageListProps {
    messages: Message[];
    isTyping?: boolean;
}

export default function MessageList({ messages, isTyping }: MessageListProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    return (
        <div className="flex-1 overflow-y-auto p-4 scrollbar-thin scrollbar-thumb-white/10 hover:scrollbar-thumb-white/20">
            <div className="max-w-3xl mx-auto w-full space-y-6">
                {messages.length === 0 ? (
                    <div className="h-[50vh] flex flex-col items-center justify-center text-s8-text-muted opacity-50">
                        <div className="text-4xl mb-4">👋</div>
                        <p>Start a conversation</p>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <MessageBubble key={msg.id} message={msg} />
                    ))
                )}

                {isTyping && (
                    <div className="flex items-center gap-2 text-s8-text-muted text-sm ml-4 animate-pulse">
                        <div className="w-2 h-2 bg-s8-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-s8-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-s8-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                )}

                <div ref={bottomRef} className="h-1" />
            </div>
        </div>
    );
}
