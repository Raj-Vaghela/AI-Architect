import { GlobeDemo } from './GlobeDemo';

export default function ThemeBackground() {
    return (
        <div className="fixed inset-0 -z-50 bg-s8-bg overflow-hidden pointer-events-none">
            {/* 3D Globe Background with Blur */}
            <div className="absolute inset-0 z-0 opacity-40 blur-[1px] scale-[2.2] translate-y-[80%] translate-x-[30%]">
                <GlobeDemo />
            </div>

            {/* Noise Overlay */}
            <div
                className="absolute inset-0 opacity-[0.03] z-10"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3Cfilter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
                }}
            />
        </div>
    );
}
