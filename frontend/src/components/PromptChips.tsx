import { Sparkles } from 'lucide-react';

interface PromptChipsProps {
    chips: string[];
    onSelect: (chip: string) => void;
}

export default function PromptChips({ chips, onSelect }: PromptChipsProps) {
    return (
        <div className="flex flex-wrap gap-2 justify-center">
            {chips.map((chip, idx) => (
                <button
                    key={idx}
                    onClick={() => onSelect(chip)}
                    className="glass-btn-secondary text-sm flex items-center gap-2 px-3 py-1.5 hover:bg-white/10 opacity-80 hover:opacity-100"
                >
                    <Sparkles className="w-3 h-3 text-s8-accent-2" />
                    {chip}
                </button>
            ))}
        </div>
    );
}
