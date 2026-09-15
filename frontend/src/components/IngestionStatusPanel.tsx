'use client';

import React, { useState } from 'react';
import { Database, FileText, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, Layers, Terminal } from 'lucide-react';

interface IngestionStatusPanelProps {
  indexPath?: string;
  totalChunks?: number;
  indexedDocumentsCount?: number;
  indexedDocuments?: string[];
  lastIngestionTime?: string;
  latestQueryRetrieval?: {
    query?: string;
    retrievedCount?: number;
    status?: 'Success' | 'No evidence found' | 'Idle';
    sources?: Array<{ file: string; section?: string; ids?: string[] }>;
  };
}

export const IngestionStatusPanel: React.FC<IngestionStatusPanelProps> = ({
  indexPath = 'data/faiss_index/documents.index',
  totalChunks = 42,
  indexedDocumentsCount = 3,
  indexedDocuments = ['MRPL_Operations_Safety_Demo_Pack.md', 'HSE_Report_2025.pdf', 'SOP_Operations.docx'],
  lastIngestionTime = 'Just now',
  latestQueryRetrieval = {
    query: 'Why is Pump P-204B considered a critical priority?',
    retrievedCount: 4,
    status: 'Success',
    sources: [
      { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '2.2 Key operating parameters' },
      { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '3.1 Incident and near-miss register', ids: ['INC-01', 'INC-07', 'INC-13'] },
      { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '4.1 Pump P-204B recurring vibration' },
      { file: 'MRPL_Operations_Safety_Demo_Pack.md', section: '6 Corrective action plan', ids: ['CAP-01', 'CAP-02'] },
    ],
  },
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  return (
    <div id="ingestion-status-panel" className="surface-card rounded-2xl p-4 sm:p-5 border-[#DCD7CE] text-left mb-6 shadow-xs">
      {/* Header */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-[#2C2B5B] text-white">
            <Database className="h-4 w-4" />
          </div>
          <div>
            <h4 className="font-display-serif text-sm font-bold text-[#1C1B24] flex items-center gap-2">
              Workspace Ingestion & Retrieval Debug Status
              <span className="px-2 py-0.5 rounded-full bg-[#EAE5DC] text-[#2C2B5B] text-[10px] font-mono font-bold">
                PERSISTENT VECTOR STORE
              </span>
            </h4>
            <p className="text-[11px] font-mono text-[#666370]">
              Index: <span className="text-[#1C1B24] font-medium">{indexPath}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 text-xs font-mono">
            <span className="px-2 py-0.5 rounded bg-[#FAF8F4] border border-[#DCD7CE] text-[#1C1B24]">
              Docs: <strong>{indexedDocumentsCount}</strong>
            </span>
            <span className="px-2 py-0.5 rounded bg-[#FAF8F4] border border-[#DCD7CE] text-[#1C1B24]">
              Chunks: <strong>{totalChunks}</strong>
            </span>
          </div>

          <button className="p-1 rounded-lg text-[#666370] hover:bg-[#EAE5DC] transition-colors">
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-[#DCD7CE]/80 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-sans">
          {/* Column 1: Index Stats & Documents */}
          <div className="space-y-3 bg-[#FAF8F4] p-3.5 rounded-xl border border-[#DCD7CE]">
            <div className="flex items-center justify-between pb-2 border-b border-[#DCD7CE]/60">
              <span className="font-bold text-[#1C1B24] flex items-center gap-1.5 font-mono text-[11px]">
                <Layers className="h-3.5 w-3.5 text-[#2C2B5B]" />
                INDEXED KNOWLEDGE BASE
              </span>
              <span className="text-[10px] text-[#666370] font-mono">Updated: {lastIngestionTime}</span>
            </div>

            <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
              <div className="p-2 rounded bg-white border border-[#DCD7CE]">
                <span className="text-[#666370] block text-[10px]">Total Vector Chunks</span>
                <span className="font-bold text-[#2C2B5B] text-sm">{totalChunks}</span>
              </div>
              <div className="p-2 rounded bg-white border border-[#DCD7CE]">
                <span className="text-[#666370] block text-[10px]">Active Documents</span>
                <span className="font-bold text-[#2C2B5B] text-sm">{indexedDocumentsCount}</span>
              </div>
            </div>

            <div>
              <span className="text-[11px] font-semibold text-[#666370] block mb-1.5 font-mono">
                Indexed File Corpus:
              </span>
              <div className="space-y-1 max-h-[100px] overflow-y-auto pr-1 scrollbar-thin">
                {indexedDocuments.map((doc, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-white border border-[#DCD7CE] text-[11px] font-mono text-[#1C1B24]"
                  >
                    <FileText className="h-3 w-3 text-[#2C2B5B] flex-shrink-0" />
                    <span className="truncate">{doc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Column 2: Retrieval Debug Status */}
          <div className="space-y-3 bg-[#FAF8F4] p-3.5 rounded-xl border border-[#DCD7CE]">
            <div className="flex items-center justify-between pb-2 border-b border-[#DCD7CE]/60">
              <span className="font-bold text-[#1C1B24] flex items-center gap-1.5 font-mono text-[11px]">
                <Terminal className="h-3.5 w-3.5 text-[#2C2B5B]" />
                LATEST RAG RETRIEVAL TRACE
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold flex items-center gap-1 ${
                  latestQueryRetrieval.status === 'Success'
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : latestQueryRetrieval.status === 'No evidence found'
                    ? 'bg-rose-100 text-rose-800 border border-rose-300'
                    : 'bg-slate-100 text-slate-700 border border-slate-300'
                }`}
              >
                {latestQueryRetrieval.status === 'Success' ? (
                  <CheckCircle2 className="h-3 w-3" />
                ) : (
                  <AlertTriangle className="h-3 w-3" />
                )}
                {latestQueryRetrieval.status}
              </span>
            </div>

            <div>
              <span className="text-[10px] font-mono text-[#666370] block">Active Query:</span>
              <p className="text-xs italic font-serif-display text-[#1C1B24] font-medium line-clamp-1 mt-0.5">
                "{latestQueryRetrieval.query || 'Waiting for query...'}"
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between text-[11px] font-mono text-[#666370] mb-1">
                <span>Retrieved Chunks ({latestQueryRetrieval.retrievedCount || 0}):</span>
              </div>

              {latestQueryRetrieval.sources && latestQueryRetrieval.sources.length > 0 ? (
                <div className="space-y-1 max-h-[100px] overflow-y-auto pr-1 scrollbar-thin">
                  {latestQueryRetrieval.sources.map((src, idx) => (
                    <div
                      key={idx}
                      className="p-1.5 rounded bg-white border border-[#DCD7CE] text-[10px] font-mono text-[#1C1B24] flex items-center justify-between gap-2"
                    >
                      <span className="font-semibold text-[#2C2B5B] truncate">{src.file}</span>
                      <span className="text-[#666370] truncate">{src.section || 'General'}</span>
                      {src.ids && src.ids.length > 0 && (
                        <span className="px-1 py-0.2 rounded bg-[#EAE5DC] text-[#2C2B5B] text-[9px] font-bold">
                          {src.ids.join(', ')}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-2.5 rounded bg-rose-50 border border-rose-200 text-rose-700 text-[11px] font-mono">
                  No vector evidence chunks matched the active query filter.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
