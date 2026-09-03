'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ShieldCheck, ArrowUpRight, AlertCircle } from 'lucide-react';
import { ChatMessageItem } from '@/lib/types';
import { SourceReferenceSection } from './SourceReference';
import { DeliverablesSection } from './DeliverableCard';

interface AssistantResultProps {
  message: ChatMessageItem;
  onViewExplanation: (requestId: string) => void;
}

export const AssistantResult: React.FC<AssistantResultProps> = ({
  message,
  onViewExplanation,
}) => {
  const getResultTitle = () => {
    switch (message.mode) {
      case 'generate_ppt':
        return 'Executive Presentation Deck Synthesis';
      case 'generate_excel':
        return 'Telemetry & Operations Audit Spreadsheet';
      case 'generate_report':
        return 'Structured Technical Compliance Report';
      default:
        return 'Document Corpus Intelligence Overview';
    }
  };

  return (
    <div className="flex justify-start my-6 animate-fade-slide-up text-left">
      <div className="surface-card p-6 sm:p-8 w-full rounded-2xl border-[#DCD7CE]">
        {/* Eyebrow Label */}
        <div className="flex items-center justify-between gap-3 mb-4 pb-3 border-b border-[#DCD7CE]/80">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md bg-[#EAE5DC] text-[#2C2B5B] text-[10px] font-mono font-bold tracking-widest uppercase">
              WORKBENCH RESULT
            </span>
            <span className="text-xs text-[#666370] font-medium hidden sm:inline">• Verified On-Prem</span>
          </div>
          <span className="font-mono text-xs text-[#666370]">{message.timestamp}</span>
        </div>

        {/* Loading / Thinking State */}
        {message.isLoading ? (
          <div className="py-8 flex flex-col items-center justify-center gap-3 text-[#666370]">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-[#2C2B5B] animate-pulse"></div>
              <div className="h-3 w-3 rounded-full bg-[#2C2B5B] animate-pulse [animation-delay:0.2s]"></div>
              <div className="h-3 w-3 rounded-full bg-[#2C2B5B] animate-pulse [animation-delay:0.4s]"></div>
            </div>
            <p className="text-xs font-semibold text-[#1C1B24]">
              Reading the local workspace & executing python tools...
            </p>
          </div>
        ) : message.error ? (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2.5">
            <AlertCircle className="h-4 w-4 text-rose-600 flex-shrink-0" />
            <span>{message.error}</span>
          </div>
        ) : (
          <div>
            {/* Answer Title */}
            <h3 className="font-display-serif text-2xl font-bold text-[#1C1B24] mb-3 tracking-tight text-left">
              {getResultTitle()}
            </h3>

            {/* Answer Body */}
            <div className="markdown-body text-left">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* Sources Section */}
        {!message.isLoading && message.sources && (
          <SourceReferenceSection sources={message.sources} />
        )}

        {/* Deliverables Section */}
        {!message.isLoading && message.files && (
          <DeliverablesSection files={message.files} />
        )}

        {/* "See how this was formed" Text Link */}
        {!message.isLoading && message.request_id && (
          <div className="mt-5 pt-3 border-t border-[#DCD7CE]/80 flex items-center justify-between">
            <span className="text-[11px] font-mono text-[#666370]">
              Audit Trail ID: {message.request_id}
            </span>

            <button
              onClick={() => onViewExplanation(message.request_id!)}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#2C2B5B] hover:text-[#1C1B24] hover:underline transition-all group focus-visible:ring-2 focus-visible:ring-[#2C2B5B] rounded"
            >
              <ShieldCheck className="h-4 w-4 text-[#2C2B5B]" />
              <span>See how this was formed</span>
              <ArrowUpRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
