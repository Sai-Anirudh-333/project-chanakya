"use client";

import { useEffect, useState } from "react";

export interface Report {
  id: number;
  topic: string;
  content: string;
  created_at: string;
  locations: string[];
  scout_data?: string;
  scholar_data?: string;
}

interface BriefingArchiveProps {
  onSelectReport?: (report: Report) => void;
}

export default function BriefingArchive({ onSelectReport }: BriefingArchiveProps) {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReports = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/reports?limit=10`);
      const data = await response.json();
      if (data.reports) {
        setReports(data.reports);
      }
    } catch (error) {
      console.error("Failed to fetch reports:", error);
    } finally {
      if (loading) setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchReports();
    
    // Auto-polling (Background heartbeat every 15 seconds)
    const intervalId = setInterval(() => {
      fetchReports();
    }, 15000);
    
    // Cleanup interval on dismount
    return () => clearInterval(intervalId);
  }, []);

  return (
    <section className="flex-1 glass-card rounded-lg p-4 flex flex-col mt-6 border-t border-terminal/30">
      <div className="flex justify-between items-center mb-4 opacity-70">
        <h2 className="text-sm font-bold flex items-center gap-2">
          <span className="w-2 h-2 bg-terminal rounded-full animate-pulse" /> 
          INTELLIGENCE ARCHIVE
        </h2>
        <button 
          onClick={fetchReports}
          className="text-xs hover:text-terminal transition-colors"
          title="Manual Sync"
        >
          [SYNC]
        </button>
      </div>
      
      <div className="space-y-4 overflow-y-auto h-[calc(100vh-500px)] custom-scrollbar pr-2">
        {loading ? (
          <div className="opacity-50 italic text-center text-xs py-10">Decrypting database records...</div>
        ) : reports.length === 0 ? (
          <div className="opacity-50 italic text-center text-xs py-10">No intelligence briefings archived yet.</div>
        ) : (
          reports.map((report) => {
            const date = new Date(report.created_at);
            const timeString = `${date.toISOString().split('T')[0]} ${date.toTimeString().split(' ')[0]}`;

            return (
              <div 
                key={report.id} 
                onClick={() => onSelectReport && onSelectReport(report)}
                className={`p-3 border border-terminal/20 bg-black/40 rounded group transition-all hover:bg-terminal/5 ${onSelectReport ? 'cursor-pointer' : ''}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-xs font-bold text-terminal/90 leading-tight">
                    {report.topic.toUpperCase()}
                  </h3>
                  <span className="text-[9px] opacity-50 whitespace-nowrap ml-2">
                    ID:{report.id.toString().padStart(4, '0')}
                  </span>
                </div>
                
                <p className="text-[10px] opacity-70 mb-3 line-clamp-3">
                  {report.content}
                </p>
                
                <div className="flex justify-between items-end border-t border-white/5 pt-2">
                  <span className="text-[8px] opacity-40 font-mono tracking-widest text-[#00ff41]">
                    {timeString}
                  </span>
                  
                  {report.locations.length > 0 && (
                    <div className="flex gap-1 flex-wrap justify-end max-w-[60%]">
                      {report.locations.slice(0, 3).map((loc, i) => (
                        <span key={i} className="text-[8px] px-1 bg-white/10 rounded truncate max-w-[60px]">
                          {loc}
                        </span>
                      ))}
                      {report.locations.length > 3 && (
                        <span className="text-[8px] px-1 bg-white/5 rounded">+{report.locations.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}
