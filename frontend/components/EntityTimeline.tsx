import { useEffect, useState } from "react";

export default function EntityTimeline() {
  const [entities, setEntities] = useState<{
    people: any[],
    organizations: any[],
    countries: any[]
  }>({
    people: [], organizations: [], countries: []
  });

  useEffect(() => {
    const fetchEntities = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/entities`);
        const data = await res.json();
        setEntities(data);
      } catch (e) {
        console.error("Failed to fetch entities", e);
      }
    };
    
    fetchEntities();
    const interval = setInterval(fetchEntities, 15000); // 15s polling to stay in sync with Autopilot
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-sm font-bold mb-4 opacity-70 flex items-center gap-2 shrink-0">
        <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" /> KNOWLEDGE GRAPH
      </h2>

      <div className="flex-1 overflow-y-auto space-y-4 custom-scrollbar pr-2">
        {entities.countries.length === 0 && entities.people.length === 0 && entities.organizations.length === 0 && (
          <div className="opacity-50 italic text-center text-xs py-4 font-mono">Building neural pathways...</div>
        )}

        {/* Countries */}
        {entities.countries.length > 0 && (
          <div>
            <h3 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Geo-Strategic Entities</h3>
            <div className="flex flex-wrap gap-1.5">
              {entities.countries.map(c => (
                <div key={c.id} className="flex items-center gap-1 px-2 py-1 bg-blue-500/10 border border-blue-500/20 rounded-md">
                  <span className="text-blue-400 text-xs font-mono">{c.name}</span>
                  <span className="bg-blue-500/20 text-blue-300 text-[9px] px-1 rounded-sm font-bold">{c.mentions}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Organizations */}
        {entities.organizations.length > 0 && (
          <div>
            <h3 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Factions & Organizations</h3>
            <div className="flex flex-wrap gap-1.5">
              {entities.organizations.map(o => (
                <div key={o.id} className="flex items-center gap-1 px-2 py-1 bg-purple-500/10 border border-purple-500/20 rounded-md">
                  <span className="text-purple-400 text-xs font-mono">{o.name}</span>
                  <span className="bg-purple-500/20 text-purple-300 text-[9px] px-1 rounded-sm font-bold">{o.mentions}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* People */}
        {entities.people.length > 0 && (
          <div>
            <h3 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Key Individuals</h3>
            <div className="flex flex-wrap gap-1.5">
              {entities.people.map(p => (
                <div key={p.id} className="flex items-center gap-1 px-2 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-md">
                  <span className="text-emerald-400 text-xs font-mono">{p.name}</span>
                  <span className="bg-emerald-500/20 text-emerald-300 text-[9px] px-1 rounded-sm font-bold">{p.mentions}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
