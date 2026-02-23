"use client";

import { useState, useEffect } from "react";
import MapWrapper from "../components/MapWrapper";
import BriefingArchive from "../components/BriefingArchive";
import EntityTimeline from "../components/EntityTimeline";

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [activeLocations, setActiveLocations] = useState<string[]>([]);
  const [scoutFeed, setScoutFeed] = useState<any[]>([]);
  const [scholarFeed, setScholarFeed] = useState<string>("");
  const [forecast, setForecast] = useState<any>(null);
  const [isForecasting, setIsForecasting] = useState(false);

  const handleSend = async () => {
    if (!query) return;
    const newMessages = [...messages, { role: "user", text: query }];
    setMessages(newMessages);
    setQuery("");
    setIsTyping(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        // Memory Optimization: We ONLY send the new query. 
        // The Python backend maintains the array history and handles the sliding window!
        body: JSON.stringify({ query: query, session_id: "default" }),
      });
      const data = await response.json();
      
      // Extract the last AI message from the LangGraph response
      let aiText = "NO_RESPONSE_RECEIVED";
      if (data.messages && data.messages.length > 0) {
        // The last message is usually the AI's synthesized response
        const lastMessage = data.messages[data.messages.length - 1];
        aiText = lastMessage.text || lastMessage.content;
      }

      setMessages((prev) => [...prev, { role: "chanakya", text: aiText }]);
      
      if (data.locations && Array.isArray(data.locations)) {
        setActiveLocations(data.locations);
      } else {
        setActiveLocations([]); // Clear if no new locations found
      }
      
      if (data.scout_data) {
        try {
          const parsedScout = JSON.parse(data.scout_data);
          if (Array.isArray(parsedScout)) {
            setScoutFeed(parsedScout);
          }
        } catch (e) {
          console.error("Failed to parse scout data", e);
        }
      } else {
        setScoutFeed([]);
      }

      if (data.scholar_data) {
        setScholarFeed(data.scholar_data);
      } else {
        setScholarFeed("");
      }
    } catch (error) {
      setMessages((prev) => [...prev, { role: "error", text: "CONNECTION INTERRUPTED" }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSelectReport = (report: any) => {
    // When a user clicks an archived report, pull it up in the central chat view!
    setMessages([
      { role: "user", text: `RETRIEVE ARCHIVE ID: ${report.id.toString().padStart(4, '0')} [${report.topic}]` },
      { role: "chanakya", text: report.content }
    ]);
    setActiveLocations(report.locations || []);
    
    // Also inject the historical scout/scholar context that generated this report!
    if (report.scout_data) {
      try {
        const parsedScout = JSON.parse(report.scout_data);
        if (Array.isArray(parsedScout)) {
          setScoutFeed(parsedScout);
        }
      } catch (e) {
        console.error("Failed to parse archived scout data", e);
      }
    } else {
        setScoutFeed([]); // Clear it if none exists
    }

    if (report.scholar_data) {
      setScholarFeed(report.scholar_data);
    } else {
      setScholarFeed("");
    }
    setForecast(null); // Clear forecast when selecting a new report
  };

  const runForecast = async () => {
    // We want to forecast based on the AI's synthesized response, not raw documents.
    const lastAiMessage = messages.slice().reverse().find(m => m.role === 'chanakya');
    if (!lastAiMessage || !lastAiMessage.text) return;

    setIsForecasting(true);
    setForecast(null);
    
    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/forecast`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ context: lastAiMessage.text })
        });
        const data = await response.json();
        setForecast(data);
    } catch (e) {
        console.error("Forecast failed:", e);
    } finally {
        setIsForecasting(false);
    }
  };

  return (
    <div className="relative min-h-screen grid-bg overflow-hidden flex flex-col p-4 md:p-8">
      <div className="scanline" />

      {/* HEADER */}
      <header className="flex justify-between items-center mb-8 glass-card p-4 rounded-lg border-l-4 border-terminal">
        <div>
          <h1 className="text-2xl font-bold tracking-widest terminal-text">PROJECT CHANAKYA</h1>
          <p className="text-xs opacity-50 font-mono tracking-tighter">OSINT / STRATEGIC DECISION SUPPORT / v1.0.0</p>
        </div>
        <div className="flex gap-4">
          <div className="flex flex-col items-end">
            <span className="text-[10px] opacity-60">SYSTEM STATUS</span>
            <span className="text-xs terminal-text animate-pulse">OPERATIONAL</span>
          </div>
          <div className="w-12 h-12 rounded-full border border-terminal/30 flex items-center justify-center">
            <div className="w-2 h-2 bg-terminal rounded-full animate-ping" />
          </div>
        </div>
      </header>

      {/* MAIN GRID */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-12 gap-6">
        
        {/* LEFT COLUMN: INTEL FEED */}
        <div className="md:col-span-3 flex flex-col gap-6">
          <section className="glass-card rounded-lg p-4 border-t border-white/5 h-[40vh] flex flex-col">
            <h2 className="text-sm font-bold mb-4 opacity-70 flex items-center gap-2 shrink-0">
              <span className="w-2 h-2 bg-intel-amber rounded-full" /> SCOUT FEED
            </h2>
            <div className="flex-1 space-y-4 font-mono text-xs opacity-60 overflow-y-auto custom-scrollbar pr-2">
              {scoutFeed.length === 0 ? (
                <div className="opacity-50 italic text-center py-10">Awaiting surveillance intercept...</div>
              ) : (
                scoutFeed.map((item, idx) => {
                  let hostname = item.link;
                  try {
                    hostname = new URL(item.link).hostname.replace('www.', '');
                  } catch (e) {}
                  return (
                    <div key={idx} className="p-2 border-l border-intel-amber/30 bg-intel-amber/5">
                      <span className="text-[10px] block opacity-40 mb-1 truncate uppercase">{hostname}</span>
                      <a href={item.link} target="_blank" rel="noopener noreferrer" className="hover:text-intel-amber transition-colors">
                        {item.title}
                      </a>
                    </div>
                  );
                })
              )}
            </div>
          </section>

          <section className="glass-card rounded-lg p-4 border-t border-white/5 h-[40vh] flex flex-col overflow-hidden">
             <EntityTimeline />
          </section>
        </div>

        {/* CENTER COLUMN: CHAT & STRATEGIC VIEW */}
        <div className="md:col-span-6 flex flex-col gap-6 h-[calc(100vh-160px)]">
          {/* STRATEGIC VIEW (Interactive Map) */}
          <div className="h-64 shrink-0 glass-card rounded-lg border border-terminal/20 relative overflow-hidden">
            <MapWrapper locations={activeLocations} />
          </div>

          {/* CHANAKYA INTERFACE */}
          <div className="flex-1 min-h-0 glass-card rounded-lg flex flex-col overflow-hidden border-b-4 border-terminal">
            <div className="p-4 shrink-0 border-b border-white/5 bg-white/2 flex justify-between items-center">
              <span className="text-xs font-bold tracking-widest opacity-80">INTELLIGENCE BRIEFING</span>
              <div className="flex items-center gap-4">
                {messages.length > 0 && messages[messages.length - 1].role === 'chanakya' && (
                  <button 
                    onClick={runForecast}
                    disabled={isForecasting}
                    className="bg-terminal/20 text-terminal border border-terminal/30 px-3 py-1 rounded text-[10px] hover:bg-terminal hover:text-black transition-colors disabled:opacity-30"
                  >
                    RUN STRATEGIC FORECAST
                  </button>
                )}
                <span className="text-[10px] terminal-text">ENCRYPTION: AES-256</span>
              </div>
            </div>
            
            <div className="flex-1 p-4 overflow-y-auto space-y-4 font-mono text-sm custom-scrollbar">
              {messages.length === 0 && (
                <p className="text-center py-20 opacity-30 text-xs italic">Awaiting strategic inquiry...</p>
              )}
              {messages.map((m, idx) => (
                <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-lg ${
                    m.role === 'user' 
                      ? 'bg-terminal/10 border border-terminal/30 text-terminal' 
                      : 'bg-white/5 border border-white/10'
                  }`}>
                    <span className="text-[9px] block mb-1 opacity-50 uppercase">{m.role}</span>
                    <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
                  </div>
                </div>
              ))}
              
              {/* STRATEGIC FORECAST SCENARIOS */}
              {isForecasting && (
                <div className="text-intel-amber animate-pulse mt-4 text-center">
                  Executing Red Team Analysis...
                </div>
              )}
              {forecast && (
                <div className="mt-6 mb-4 space-y-3 pt-4 border-t border-white/10">
                    <h3 className="text-xs font-bold tracking-widest opacity-80 mb-2">SCENARIO FORECAST</h3>
                    <div className="p-3 border border-green-500/30 bg-green-500/10 rounded-lg">
                        <h4 className="font-bold text-green-400 mb-1">OPTIMISTIC</h4>
                        <p className="opacity-80 leading-relaxed text-xs">{forecast.optimistic}</p>
                    </div>
                    <div className="p-3 border border-yellow-500/30 bg-yellow-500/10 rounded-lg">
                        <h4 className="font-bold text-yellow-400 mb-1">BASE CASE</h4>
                        <p className="opacity-80 leading-relaxed text-xs">{forecast.base_case}</p>
                    </div>
                    <div className="p-3 border border-red-500/30 bg-red-500/10 rounded-lg">
                        <h4 className="font-bold text-red-400 mb-1">PESSIMISTIC</h4>
                        <p className="opacity-80 leading-relaxed text-xs">{forecast.pessimistic}</p>
                    </div>
                </div>
              )}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white/5 border border-white/10 p-3 rounded-lg flex gap-1">
                    <div className="w-1.5 h-1.5 bg-terminal rounded-full animate-bounce [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 bg-terminal rounded-full animate-bounce [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 bg-terminal rounded-full animate-bounce" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 shrink-0 border-t border-white/5 bg-white/2 flex gap-4">
              <input 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder="INPUT STRATEGIC QUERY..."
                className="flex-1 bg-black/40 border border-white/10 rounded px-4 py-2 text-sm focus:outline-none focus:border-terminal/50 font-mono"
              />
              <button 
                onClick={handleSend}
                className="bg-terminal text-black font-bold px-6 py-2 rounded text-xs hover:bg-[#00cc33] transition-colors"
              >
                EXECUTE
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: REPOSITORY */}
        <div className="md:col-span-3 flex flex-col gap-6">
          <section className="glass-card rounded-lg p-4 h-[40vh] flex flex-col">
            <h2 className="text-sm font-bold mb-4 opacity-70 flex items-center gap-2 shrink-0">
              <span className="w-2 h-2 bg-terminal rounded-full" /> SCHOLAR INTEL
            </h2>
            
            <div className="flex-1 space-y-3 overflow-y-auto font-mono text-[10px] custom-scrollbar pr-2 opacity-70">
              {!scholarFeed ? (
                <div className="opacity-50 italic text-center py-10">Awaiting internal document retrieval...</div>
              ) : (
                <div className="p-3 border-l-2 border-terminal/30 bg-terminal/5 whitespace-pre-wrap">
                  {scholarFeed.slice(0, 1000)}... {/* Trim to prevent massive walls of text */}
                </div>
              )}
            </div>
          </section>

          {/* POSTGRESQL BRIEFING ARCHIVE */}
          <BriefingArchive onSelectReport={handleSelectReport} />
        </div>

      </div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.1);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 255, 65, 0.2);
          border-radius: 10px;
        }
      `}</style>
    </div>
  );
}

