import { User, Bot, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';
import { Message } from '@/lib/types';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
    message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === 'user';
    const [jsonExpanded, setJsonExpanded] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className={`flex w-full gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg ring-1 ring-white/10 ${isUser
                ? 'bg-gradient-to-br from-s8-accent to-s8-accent-2'
                : 'bg-s8-surface'
                }`}>
                {isUser ? (
                    <User className="w-5 h-5 text-white" />
                ) : (
                    <Bot className="w-5 h-5 text-s8-accent" />
                )}
            </div>

            {/* Content */}
            <div className={`flex flex-col max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
                <div className={`relative px-4 py-3 rounded-2xl ${isUser
                    ? 'glass bg-s8-accent/10 border-s8-accent/20 text-white rounded-tr-sm'
                    : 'glass bg-s8-surface/50 border-white/5 rounded-tl-sm'
                    }`}>
                    <div className="prose prose-invert prose-sm max-w-none">
                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                // Style headings
                                h1: ({ node, ...props }) => <h1 className="text-lg font-bold mb-2 text-s8-accent" {...props} />,
                                h2: ({ node, ...props }) => <h2 className="text-base font-bold mb-2 text-s8-accent" {...props} />,
                                h3: ({ node, ...props }) => <h3 className="text-sm font-semibold mb-1 text-s8-accent-2" {...props} />,
                                // Style lists
                                ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-1 my-2" {...props} />,
                                ol: ({ node, ...props }) => <ol className="list-decimal list-inside space-y-1 my-2" {...props} />,
                                li: ({ node, ...props }) => <li className="text-sm leading-relaxed" {...props} />,
                                // Style links
                                a: ({ node, ...props }) => <a className="text-s8-accent hover:text-s8-accent-2 underline" {...props} />,
                                // Style code
                                code: ({ node, inline, ...props }: any) =>
                                    inline ? (
                                        <code className="bg-black/30 px-1.5 py-0.5 rounded text-xs font-mono text-s8-accent" {...props} />
                                    ) : (
                                        <code className="block bg-black/40 p-3 rounded-lg text-xs font-mono overflow-x-auto my-2" {...props} />
                                    ),
                                // Style paragraphs
                                p: ({ node, ...props }) => <p className="text-sm leading-relaxed mb-2 last:mb-0" {...props} />,
                                // Style strong/bold
                                strong: ({ node, ...props }) => <strong className="font-semibold text-white" {...props} />,
                            }}
                        >
                            {message.content}
                        </ReactMarkdown>
                    </div>

                    {/* Metadata / JSON Expansion */}
                    {message.metadata?.deployment_plan && (
                        <div className="mt-4 rounded-lg overflow-hidden border border-white/10 bg-black/20">
                            <button
                                onClick={() => setJsonExpanded(!jsonExpanded)}
                                className="w-full flex items-center justify-between px-3 py-2 bg-white/5 hover:bg-white/10 transition-colors text-xs font-medium text-s8-text-muted"
                            >
                                <span>Deployment Plan Details</span>
                                {jsonExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                            </button>

                            {jsonExpanded && (
                                <div className="p-3 bg-black/40 font-mono text-xs overflow-x-auto">
                                    <pre className="text-emerald-400">
                                        {JSON.stringify(message.metadata.deployment_plan, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Actions (Timestamp, Copy) */}
                {!isUser && (
                    <div className="flex items-center gap-2 mt-1 ml-1">
                        <span className="text-[10px] text-s8-text-muted opacity-50">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        <button
                            onClick={handleCopy}
                            className="p-1 text-s8-text-muted opacity-0 hover:opacity-100 transition-opacity"
                        >
                            {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
