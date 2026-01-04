'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ThemeBackground from '@/components/ThemeBackground';
import AuthModal from '@/components/AuthModal';
import Composer from '@/components/Composer';
import { useAuth } from '@/components/AuthProvider';
import { Sparkles, Terminal } from 'lucide-react';

export default function LandingPage() {
  const [showAuth, setShowAuth] = useState(false);
  const router = useRouter();
  const { user, isLoading } = useAuth();

  // Redirect to chat if already logged in
  useEffect(() => {
    if (!isLoading && user) {
      router.push('/chat');
    }
  }, [isLoading, user, router]);

  const handleInteraction = () => {
    setShowAuth(true);
  };

  return (
    <main className="min-h-screen flex flex-col relative overflow-hidden text-s8-text font-sans selection:bg-s8-accent/30">
      <ThemeBackground />

      {/* Navbar / Header (Minimal) */}
      <div className="absolute top-0 w-full p-4 flex justify-between items-center z-10">
        <div className="font-bold text-lg tracking-tight bg-gradient-to-r from-s8-accent to-s8-accent-2 bg-clip-text text-transparent opacity-80">
          LOGO
        </div>
        <button
          onClick={() => setShowAuth(true)}
          className="text-sm font-medium text-s8-text-muted hover:text-white transition-colors"
        >
          Sign In
        </button>
      </div>

      {/* Main Centered Content */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 animate-in fade-in zoom-in-95 duration-700">
        <div className="relative w-full max-w-2xl">
          {/* Logo & Text - Absolute positioned above */}
          <div className="absolute bottom-full left-0 right-0 pb-12 text-center space-y-6">
            {/* Logo / Icon */}
            <div className="flex justify-center">
              <div className="p-4 rounded-3xl bg-s8-surface/50 border border-white/5 shadow-2xl shadow-s8-accent/10 backdrop-blur-xl">
                <Terminal className="w-10 h-10 text-s8-accent" />
              </div>
            </div>

            <h2 className="text-2xl md:text-3xl font-medium text-white/90">
              What would you like to build?
            </h2>
          </div>

          {/* Interactive Fake Composer - Dead Center */}
          <div onClick={handleInteraction}>
            <Composer
              onSend={handleInteraction}
              centered={true}
              disabled={false}
            />
          </div>
        </div>
      </div>


      <AuthModal
        isOpen={showAuth}
        onClose={() => setShowAuth(false)}
      />
    </main >
  );
}
