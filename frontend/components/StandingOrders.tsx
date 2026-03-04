"use client";
import { useState, useEffect } from 'react';
import { Trash2, Plus, RefreshCw } from "lucide-react";

// Define the Typescript interface (must match Pydantic's TopicResponse)
interface Topic {
    id: number;
    topic: string;
    created_at: string;
}

export default function StandingOrders() {
    // State to hold the topics from the DB
    const [topics, setTopics] = useState<Topic[]>([]);
    
    // State for the text input box
    const [newTopicText, setNewTopicText] = useState("");
    
    // Loading state for UI feedback
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // 1. GET fetch function
    const fetchTopics = async () => {
        setIsLoading(true);
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/topics`);
            if (res.ok) {
                const data = await res.json();
                setTopics(data);
            }
        } catch (err) {
            console.error("Failed to fetch topics:", err);
        } finally {
            setIsLoading(false);
        }
    }

    // Load topics on mount
    useEffect(() => {
        fetchTopics();
    }, []);

    // 2. POST fetch function
    const handleAddTopic = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTopicText.trim()) return;

        setIsSubmitting(true);
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/topics`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ topic: newTopicText }),
            });

            if (res.ok) {
                setNewTopicText(""); // Clear input
                await fetchTopics(); // Refresh list to get the new ID
            } else {
                console.error("Failed to add topic", await res.text());
            }
        } catch (err) {
            console.error("Error adding topic:", err);
        } finally {
            setIsSubmitting(false);
        }
    };

    // 3. DELETE fetch function
    const handleDeleteTopic = async (id: number) => {
        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/topics/${id}`, {
                method: "DELETE"
            });

            if (res.ok) {
                // Optimistically remove from UI, or re-fetch
                setTopics(topics.filter(t => t.id !== id));
            } else {
                console.error("Failed to delete topic");
            }
        } catch (err) {
            console.error("Error deleting topic:", err);
        }
    };

    return (
        <div className="glass-card border border-terminal/30 p-6 rounded-lg text-white shadow-2xl max-w-2xl w-full relative overflow-hidden">
            <div className="scanline opacity-50" />
            <div className="flex justify-between items-center mb-6 border-b border-white/10 pb-4 relative z-10">
                <div>
                    <h2 className="text-sm font-bold tracking-widest text-[#00ff41] flex items-center gap-2">
                        <span className="w-2 h-2 bg-[#00ff41] rounded-full animate-pulse" /> 
                        OPERATIONAL DIRECTIVES
                    </h2>
                    <p className="text-[10px] text-[#00ff41]/50 mt-1 font-mono uppercase tracking-wider">Configure autopilot intelligence gathering targets.</p>
                </div>
                <button 
                    onClick={fetchTopics}
                    className="p-2 hover:bg-[#00ff41]/10 rounded transition-colors text-[#00ff41]/60 hover:text-[#00ff41] border border-transparent hover:border-[#00ff41]/30"
                    title="Manual Sync"
                >
                    <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
            </div>
            
            {/* Input Form Here */}
            <form onSubmit={handleAddTopic} className="flex gap-3 mb-6 relative z-10">
                <input 
                    type="text" 
                    value={newTopicText}
                    onChange={(e) => setNewTopicText(e.target.value)}
                    placeholder="INPUT NEW STRATEGIC DIRECTIVE..."
                    className="flex-1 bg-black/40 border border-[#00ff41]/20 rounded px-4 py-2 text-sm text-[#00ff41] focus:outline-none focus:border-[#00ff41]/60 focus:bg-[#00ff41]/5 transition-all placeholder-[#00ff41]/30 font-mono"
                    disabled={isSubmitting}
                />
                <button 
                    type="submit"
                    disabled={isSubmitting || !newTopicText.trim()}
                    className="bg-[#00ff41]/10 border border-[#00ff41]/30 hover:bg-[#00ff41] hover:text-black text-[#00ff41] px-6 py-2 rounded text-xs font-bold transition-all disabled:opacity-30 disabled:hover:bg-[#00ff41]/10 disabled:hover:text-[#00ff41] flex items-center gap-2 tracking-widest"
                >
                    <Plus className="w-4 h-4" />
                    <span>ADD</span>
                </button>
            </form>

            {/* List of Topics Here */}
            <div className="space-y-3 font-mono text-sm relative z-10">
                {isLoading && topics.length === 0 ? (
                    <div className="text-center py-8 text-[#00ff41]/50 text-[10px] italic tracking-widest">Decrypting active directives...</div>
                ) : topics.length === 0 ? (
                    <div className="text-center py-8 text-[#00ff41]/40 bg-black/20 rounded border border-[#00ff41]/10 border-dashed text-[10px] tracking-widest uppercase">
                        No operational directives designated.
                    </div>
                ) : (
                    <ul className="grid gap-2">
                        {topics.map((item) => (
                            <li 
                                key={item.id} 
                                className="group flex justify-between items-center p-3 bg-black/40 hover:bg-[#00ff41]/5 border border-[#00ff41]/20 rounded transition-all"
                            >
                                <span className="text-[#00ff41]/90 leading-relaxed pr-4 text-xs">
                                    <span className="text-[#00ff41]/30 mr-2">▶</span>
                                    {item.topic}
                                </span>
                                <button
                                    onClick={() => handleDeleteTopic(item.id)}
                                    className="p-1.5 text-[#00ff41]/40 hover:text-red-400 hover:bg-red-400/10 rounded transition-all opacity-100 sm:opacity-0 group-hover:opacity-100 flex-shrink-0"
                                    title="Revoke Order"
                                    aria-label="Revoke Order"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}
