'use client';

import React, { useEffect, useState } from 'react';
import { ShieldCheck, FileText, Wrench, X, RefreshCw, CheckCircle2, MessageSquare } from 'lucide-react';
import { ExplanationResponse } from '@/lib/types';
import { getExplanation } from '@/lib/api';

interface ProcessJournalProps {
  requestId: string | null;
  onClose: () => void;
}

export const ProcessJournal: React.FC<ProcessJournalProps> = ({
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
        setError(err.message || 'Failed to retrieve process journal trace');
      } finally {
        setLoading(false);
      }
    };

    fetchExplanation();
  }, [requestId]);

  if (!requestId) return null;

  return (
    <div className="surface-card rounded-2xl p-6 shadow-md animate-fade-slide-up border-[#DCD7CE] text-left">
      {/* Journal Title & Close Button */}
      <div className="flex items-center justify-between border-b border-[#DCD7CE] pb-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-[#EAE5DC] text-[#2C2B5B] border border-[#DCD7CE]">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-display-serif text-xl font-bold text-[#1C1B24]">
              Behind the answer
            </h3>
            <p className="text-[11px] font-mono text-[#666370]">
              Process ID: <span className="text-[#2C2B5B] font-semibold">{requestId}</span>
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="text-[#666370] hover:text-[#1C1B24] p-1.5 rounded-lg hover:bg-[#F5F2EB] transition-colors focus-visible:ring-2 focus-visible:ring-[#2C2B5B]"
          title="Close process journal"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {loading ? (
        <div className="py-8 text-center text-[#666370] flex flex-col items-center justify-center gap-2">
          <RefreshCw className="h-5 w-5 text-[#2C2B5B] animate-spin" />
          <span className="text-xs font-medium">Fetching Process Journal...</span>
        </div>
      ) : error ? (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-xl">
          <p className="font-semibold">Audit Trace Error</p>
          <p className="mt-1 text-[11px] text-rose-600">{error}</p>
        </div>
      ) : data ? (
        <div className="space-y-4">
          {/* Reasoning Narrative */}
          <div className="bg-[#EAE5DC] border border-[#DCD7CE] rounded-xl p-3.5 text-[#1C1B24] text-xs leading-relaxed font-sans text-left">
            <span className="font-bold text-[#2C2B5B] block mb-1">Process Narrative:</span>
            {data.answer_summary}
          </div>

          {/* Vertical Timeline */}
          <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#DCD7CE]">
            {/* Step 1: Question received */}
            <div className="relative flex items-start gap-3 text-xs">
              <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#2C2B5B] text-white flex items-center justify-center text-[10px] font-bold shadow-2xs">
                1
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-[#1C1B24] flex items-center gap-1.5">
                  <MessageSquare className="h-3.5 w-3.5 text-[#2C2B5B]" />
                  Question received
                </p>
                <p className="text-[11px] text-[#666370] italic mt-0.5 line-clamp-2">
                  "{data.query}"
                </p>
              </div>
            </div>

            {/* Step 2: Documents retrieved */}
            <div className="relative flex items-start gap-3 text-xs">
              <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#2C2B5B] text-white flex items-center justify-center text-[10px] font-bold shadow-2xs">
                2
              </div>
              <div className="min-w-0 w-full">
                <p className="font-semibold text-[#1C1B24] flex items-center gap-1.5">
                  <FileText className="h-3.5 w-3.5 text-[#2C2B5B]" />
                  Read {data.retrieved_docs?.length || 0} relevant documents
                </p>
                <div className="mt-1 space-y-1">
                  {data.retrieved_docs?.map((doc, idx) => (
                    <div
                      key={idx}
                      className="bg-[#F5F2EB] border border-[#DCD7CE] rounded-lg px-2.5 py-1 text-[11px] font-mono text-[#1C1B24] flex items-center justify-between"
                    >
                      <span className="truncate">{doc.file}</span>
                      {(doc.page !== undefined || doc.section) && (
                        <span className="text-[10px] text-[#2C2B5B] font-bold">
                          {doc.page !== undefined ? `p.${doc.page}` : ''} {doc.section ? `sec.${doc.section}` : ''}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Step 3: Local tools used */}
            <div className="relative flex items-start gap-3 text-xs">
              <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#2C2B5B] text-white flex items-center justify-center text-[10px] font-bold shadow-2xs">
                3
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-[#1C1B24] flex items-center gap-1.5">
                  <Wrench className="h-3.5 w-3.5 text-[#2C2B5B]" />
                  Executed {data.tools_called?.length || 0} local python tools
                </p>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {data.tools_called?.map((tool, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md bg-[#F5F2EB] border border-[#DCD7CE] font-mono text-[10px] font-bold text-[#2C2B5B]"
                    >
                      {tool.name}()
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Step 4: Deliverable & Audit Saved */}
            <div className="relative flex items-start gap-3 text-xs">
              <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-[#2C2B5B] text-white flex items-center justify-center text-[10px] font-bold shadow-2xs">
                4
              </div>
              <div>
                <p className="font-semibold text-[#1C1B24] flex items-center gap-1.5">
                  <CheckCircle2 className="h-3.5 w-3.5 text-[#2C2B5B]" />
                  Saved audit trail locally
                </p>
                <p className="text-[11px] text-[#666370]">
                  Verified compliance check & generated response artifacts.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
