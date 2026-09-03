'use client';

import React, { useEffect, useState } from 'react';
import { ShieldCheck, FileText, Wrench, Info, X, RefreshCw, CheckCircle2 } from 'lucide-react';
import { ExplanationResponse } from '@/lib/types';
import { getExplanation } from '@/lib/api';

interface ExplanationPanelProps {
  requestId: string | null;
  onClose: () => void;
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({
  requestId,
  onClose,
}) => {
  const [data, setData] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!requestId) {
      setData(null);
      return;
    }

    const fetchExplanation = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getExplanation(requestId);
        setData(res);
      } catch (err: any) {
        setError(err.message || 'Failed to retrieve explanation trace');
      } finally {
        setLoading(false);
      }
    };

    fetchExplanation();
  }, [requestId]);

  if (!requestId) return null;

  return (
    <div className="card-editorial bg-white p-6 shadow-xl animate-fadeIn">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-[#E8E5DF] pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-[#EEF2FF] text-[#312E81] border border-[#C7D2FE]">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <h2 className="font-serif-display text-lg font-bold text-[#111318]">
              How this answer was formed
            </h2>
            <p className="text-[11px] font-mono text-[#717582]">
              Audit ID: <span className="text-[#312E81] font-semibold">{requestId}</span>
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="text-[#717582] hover:text-[#111318] p-1.5 rounded-lg hover:bg-[#F7F5F2] transition-colors"
          title="Close explanation panel"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {loading ? (
        <div className="py-8 text-center text-[#525663] flex flex-col items-center justify-center gap-2">
          <RefreshCw className="h-5 w-5 text-[#312E81] animate-spin" />
          <span className="text-xs font-medium">Fetching Audit Trail...</span>
        </div>
      ) : error ? (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-xl">
          <p className="font-semibold">Audit Trace Error</p>
          <p className="mt-1 text-[11px] text-rose-600">{error}</p>
        </div>
      ) : data ? (
        <div className="space-y-4 text-xs">
          {/* 1. Query */}
          <div>
            <label className="text-[11px] font-semibold text-[#525663] uppercase tracking-wider block mb-1">
              Original Task Query
            </label>
            <div className="bg-[#FAF9F6] border border-[#E5E2DC] rounded-xl p-3 text-[#111318] font-sans text-xs leading-relaxed italic">
              "{data.query}"
            </div>
          </div>

          {/* 2. Story (Short Reasoning Narrative) */}
          <div>
            <label className="text-[11px] font-semibold text-[#525663] uppercase tracking-wider flex items-center gap-1.5 mb-1">
              <Info className="h-3.5 w-3.5 text-[#312E81]" />
              Story & Synthesis Summary
            </label>
            <div className="bg-[#EEF2FF] border border-[#C7D2FE] rounded-xl p-3 text-[#1E1B4B] leading-relaxed font-sans text-xs">
              {data.answer_summary}
            </div>
          </div>

          {/* 3. Docs Used (List with icons) */}
          <div>
            <label className="text-[11px] font-semibold text-[#525663] uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <FileText className="h-3.5 w-3.5 text-[#312E81]" />
              Docs Used ({data.retrieved_docs?.length || 0})
            </label>
            <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
              {data.retrieved_docs && data.retrieved_docs.length > 0 ? (
                data.retrieved_docs.map((doc, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between bg-[#FAF9F6] border border-[#E5E2DC] rounded-lg px-3 py-2 text-[#111318] font-mono text-[11px]"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="h-3.5 w-3.5 text-[#312E81] flex-shrink-0" />
                      <span className="text-[#111318] font-medium truncate">{doc.file}</span>
                    </div>
                    {(doc.page !== undefined || doc.section) && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-white text-[#312E81] border border-[#E5E2DC] font-semibold flex-shrink-0">
                        {doc.page !== undefined ? `p.${doc.page}` : ''}
                        {doc.page !== undefined && doc.section ? ' • ' : ''}
                        {doc.section ? `sec.${doc.section}` : ''}
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-[#717582] italic text-[11px]">No external docs used.</p>
              )}
            </div>
          </div>

          {/* 4. Tools Called (Chips) */}
          <div>
            <label className="text-[11px] font-semibold text-[#525663] uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <Wrench className="h-3.5 w-3.5 text-[#312E81]" />
              Tools Called ({data.tools_called?.length || 0})
            </label>
            <div className="flex flex-wrap gap-2">
              {data.tools_called && data.tools_called.length > 0 ? (
                data.tools_called.map((tool, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FAF9F6] border border-[#E5E2DC] font-mono text-xs text-[#111318] shadow-2xs"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 flex-shrink-0" />
                    <span className="font-bold text-[#312E81]">{tool.name}()</span>
                  </div>
                ))
              ) : (
                <p className="text-[#717582] italic text-[11px]">No tools called.</p>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
