"use client";

import { useState } from "react";
import { Upload, X, FileText, CheckCircle, AlertCircle } from "lucide-react";

interface DocumentUploadProps {
  onClose: () => void;
}

export default function DocumentUpload({ onClose }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "success" | "error">("idle");
  const [statusMessage, setStatusMessage] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setUploadStatus("idle");
      setStatusMessage("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadStatus("idle");
    setStatusMessage("Uploading document...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/documents/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      setUploadStatus("success");
      setStatusMessage("Document successfully ingested by Scholar.");
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (error) {
      setUploadStatus("error");
      setStatusMessage("Failed to ingest document. Check server connection.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="glass-card p-6 rounded-lg border border-terminal/30 max-w-md w-full animate-fade-in relative shadow-[0_0_30px_rgba(0,255,65,0.1)]">
      <div className="flex justify-between items-start mb-6 border-b border-terminal/20 pb-4">
        <div>
          <h2 className="text-lg font-bold text-terminal tracking-wider flex items-center gap-2">
            <Upload className="w-5 h-5" /> DOCUMENT INGESTION
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-1 opacity-70">
            SECURE UPLOAD PORTAL FOR SCHOLAR AGENT
          </p>
        </div>
        <button 
          onClick={onClose}
          className="text-slate-500 hover:text-terminal transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="space-y-6">
        <div className="border-2 border-dashed border-terminal/30 rounded-lg p-8 text-center bg-black/20 hover:bg-black/40 transition-colors relative">
          <input 
            type="file" 
            accept=".pdf"
            onChange={handleFileChange}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
          
          <div className="flex flex-col items-center justify-center pointer-events-none">
            {file ? (
              <>
                <FileText className="w-12 h-12 text-terminal mb-3 opacity-80" />
                <p className="text-sm font-bold text-white mb-1 truncate max-w-[200px]">{file.name}</p>
                <p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </>
            ) : (
              <>
                <Upload className="w-12 h-12 text-slate-500 mb-3 opacity-50 pulse" />
                <p className="text-sm text-slate-300 font-mono mb-1">Select or Drag PDF</p>
                <p className="text-xs text-slate-500 font-mono">Max size 50MB</p>
              </>
            )}
          </div>
        </div>

        {statusMessage && (
          <div className={`p-3 rounded text-xs font-mono flex items-center gap-2 ${
            uploadStatus === 'success' ? 'bg-green-500/10 text-green-400 border border-green-500/30' : 
            uploadStatus === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/30' : 
            'bg-terminal/10 text-terminal border border-terminal/30'
          }`}>
            {uploadStatus === 'success' && <CheckCircle className="w-4 h-4" />}
            {uploadStatus === 'error' && <AlertCircle className="w-4 h-4" />}
            {uploadStatus === 'idle' && <div className="w-3 h-3 rounded-full bg-terminal animate-ping mr-1" />}
            {statusMessage}
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || isUploading || uploadStatus === 'success'}
          className={`w-full py-3 rounded text-sm font-bold tracking-widest transition-all ${
            !file || isUploading || uploadStatus === 'success'
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed opacity-50'
              : 'bg-terminal text-black hover:bg-[#00cc33] shadow-[0_0_15px_rgba(0,255,65,0.4)]'
          }`}
        >
          {isUploading ? "TRANSMITTING..." : "INITIATE INGESTION"}
        </button>
      </div>
    </div>
  );
}
