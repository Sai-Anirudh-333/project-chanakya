"use client";

import dynamic from 'next/dynamic';

const StrategicMap = dynamic(() => import('./StrategicMap'), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex flex-col items-center justify-center relative bg-[#0b0c10]">
      <div className="absolute inset-0 opacity-20 pointer-events-none bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')]" />
      <p className="terminal-text text-sm mb-2 z-10">SATELLITE DOWNLINK PENDING...</p>
      <div className="flex gap-2 z-10">
         <div className="w-2 h-8 bg-terminal/40 animate-pulse" />
         <div className="w-2 h-12 bg-terminal/60 animate-pulse" />
         <div className="w-2 h-6 bg-terminal/80 animate-pulse" />
      </div>
    </div>
  )
});

export default function MapWrapper({ locations }: { locations: string[] }) {
  return <StrategicMap locations={locations} />;
}
