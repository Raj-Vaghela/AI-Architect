import { Send } from 'lucide-react';
import { KeyboardEvent, useState, useRef, useEffect } from 'react';

interface ComposerProps {
    onSend: (text: string) => void;
    disabled?: boolean;
    centered?: boolean;
}

export default function Composer({ onSend, disabled, centered = false }: ComposerProps) {
    const [text, setText] = useState('');
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if (!text.trim() || disabled) return;
        onSend(text);
        setText('');

        // Reset height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Auto-resize
    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
        }
    }, [text]);

    return (
        <div className={`w-full transition-all duration-500 ${centered ? 'p-0' : 'px-0'}`}>
            <div className={`
        relative glass bg-s8-surface/60 focus-within:bg-s8-surface/80 focus-within:ring-1 focus-within:ring-s8-accent/50 transition-all
        ${centered ? 'rounded-[2rem] shadow-2xl py-2' : 'rounded-xl shadow-lg py-2'}
      `}>
                <div className="flex items-end gap-2 pl-4 pr-3">
                    <textarea
                        ref={textareaRef}
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask anything"
                        disabled={disabled}
                        rows={1}
                        className={`
                w-full bg-transparent text-s8-text placeholder:text-s8-text-muted/50 
                resize-none focus:outline-none max-h-[200px] overflow-y-auto scrollbar-thin scrollbar-thumb-white/10
                py-3 pl-2
            `}
                    />

                    <button
                        onClick={handleSend}
                        disabled={!text.trim() || disabled}
                        className={`mb-1.5 p-2 rounded-full transition-all flex-shrink-0 ${text.trim() && !disabled
                            ? 'bg-s8-text text-s8-bg hover:opacity-90'
                            : 'bg-white/10 text-s8-text-muted cursor-not-allowed'
                            }`}
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </div>
            </div>

            <div className="text-center mt-3 text-[11px] text-s8-text-muted/40 font-medium">
                This is a AI bot, it can make mistakes.
            </div>
        </div>
    );
}
