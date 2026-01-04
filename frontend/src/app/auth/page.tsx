'use client';

import { useRouter } from 'next/navigation';
import ThemeBackground from '@/components/ThemeBackground';
import AuthModal from '@/components/AuthModal';

export default function AuthPage() {
    // Reuse the modal but keep it always open
    const router = useRouter();

    return (
        <main className="min-h-screen flex items-center justify-center p-4">
            <ThemeBackground />
            <AuthModal
                isOpen={true}
                onClose={() => router.push('/')}
                onLogin={() => router.push('/chat')}
            />
        </main>
    );
}
