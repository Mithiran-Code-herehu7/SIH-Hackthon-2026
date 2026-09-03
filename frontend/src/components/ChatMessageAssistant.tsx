'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Sparkles, HelpCircle, AlertCircle, ArrowUpRight } from 'lucide-react';
import { ChatMessageItem } from '@/lib/types';
import { SourcesRow } from './SourceChip';
import { FileCardsRow } from './FileCard';

interface ChatMessageAssistantProps {
  message: ChatMessageItem;
  onViewExplanation: (requestId: string) => void;
}

export const ChatMessageAssistant: React.FC<ChatMessageAssistantProps> = ({
  message,
  onViewExplanation,
}) => {
  return (
    <div className="flex justify-start my-5 animate-fadeIn">
      <div className="max-w-[95%] sm:max-w-[88%] card-editorial bg-white p-5 sm:p-6 w-full">
        {/* Card Header Tagline */}
        <div className="flex items-center justify-between gap-2 mb-3 pb-2 border-b border-[#E8E5DF] text-xs text-[#525663]">
          <div className="flex items-center gap-1.5 font-semibold text-[#111318]">
            <Sparkles className="h-4 w-4 text-[#312E81]" />
            <span className="font-serif-display text-sm font-bold text-[#111318]">
              Agentic Intelligence Synthesis
            </span>
          </div>
          <span className="font-mono text-[11px] text-[#717582]">{message.timestamp}</span>
        </div>

        {/* Loading State */}
        {message.isLoading ? (
          <div className="py-6 flex flex-col items-center justify-center gap-3 text-[#525663]">
            <div className="flex items-center gap-2">
              <div className="h-2.5 w-2.5 rounded-full bg-[#312E81] animate-bounce"></div>
              <div className="h-2.5 w-2.5 rounded-full bg-[#4338CA] animate-bounce [animation-delay:0.2s]"></div>
              <div className="h-2.5 w-2.5 rounded-full bg-[#6366F1] animate-bounce [animation-delay:0.4s]"></div>
            </div>
            <p className="text-xs font-medium font-sans text-[#525663] animate-pulse">
              Synthesizing RAG context & executing tool pipeline...
            </p>
          </div>
        ) : message.error ? (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2.5">
            <AlertCircle className="h-4 w-4 text-rose-600 flex-shrink-0" />
            <span>{message.error}</span>
          </div>
        ) : (
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Sources Row */}
        {!message.isLoading && message.sources && (
          <SourcesRow sources={message.sources} />
        )}

        {/* Generated Files Row */}
        {!message.isLoading && message.files && (
          <FileCardsRow files={message.files} />
        )}

        {/* "How was this generated?" text link */}
        {!message.isLoading && message.request_id && (
          <div className="mt-4 pt-3 border-t border-[#E8E5DF] flex items-center justify-between">
            <span className="text-[11px] font-mono text-[#717582]">
              Audit Ref: {message.request_id}
            </span>

            <button
              onClick={() => onViewExplanation(message.request_id!)}
              className="inline-flex items-center gap-1 text-xs font-semibold text-[#312E81] hover:text-[#1E1B4B] hover:underline transition-all group"
            >
              <HelpCircle className="h-3.5 w-3.5" />
              <span>How was this generated?</span>
              <ArrowUpRight className="h-3.5 w-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
