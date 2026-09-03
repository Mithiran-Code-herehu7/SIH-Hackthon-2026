'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, ShieldAlert, Cpu, Eye, Sparkles, AlertCircle } from 'lucide-react';
import { ChatMessageItem } from '@/lib/types';
import { SourcesList } from './SourcesList';
import { FileDownloads } from './FileDownloads';

interface ChatMessageProps {
  message: ChatMessageItem;
  onViewExplanation: (requestId: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onViewExplanation,
}) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex gap-3 my-4 ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
    >
      {/* Assistant Avatar */}
      {!isUser && (
        <div className="flex-shrink-0 h-9 w-9 rounded-xl bg-slate-900 border border-slate-750 text-blue-400 flex items-center justify-center shadow-md shadow-blue-950/40">
          <Cpu className="h-5 w-5 text-cyan-400" />
        </div>
      )}

      {/* Message Bubble Container */}
      <div
        className={`max-w-[88%] sm:max-w-[80%] rounded-2xl p-4 text-slate-100 shadow-md ${
          isUser
            ? 'bg-blue-600/90 text-white rounded-tr-none border border-blue-500/50'
            : 'bg-slate-900/80 border border-slate-800 rounded-tl-none glass-panel'
        }`}
      >
        {/* Header bar of bubble */}
        <div className="flex items-center justify-between gap-2 mb-2 pb-1.5 border-b border-slate-800/50 text-[11px] text-slate-400">
          <div className="flex items-center gap-1.5 font-medium">
            {isUser ? (
              <span className="text-blue-100 font-semibold">Authorized User</span>
            ) : (
              <span className="text-cyan-400 font-semibold flex items-center gap-1">
                <Sparkles className="h-3 w-3" /> Agentic AI Assistant
              </span>
            )}
            {message.mode && (
              <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 uppercase tracking-wider text-[9px] font-mono border border-slate-700">
                Mode: {message.mode.replace('generate_', '')}
              </span>
            )}
          </div>
          <span className="text-slate-400 font-mono text-[10px]">{message.timestamp}</span>
        </div>

        {/* Loading Spinner Skeleton */}
        {message.isLoading ? (
          <div className="flex items-center gap-3 py-3 text-slate-300">
            <div className="h-4 w-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-sm font-medium animate-pulse">
              Analyzing on-premise document corpus & executing tools...
            </span>
          </div>
        ) : message.error ? (
          <div className="flex items-center gap-2 text-rose-400 text-sm py-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{message.error}</span>
          </div>
        ) : isUser ? (
          <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
        ) : (
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Sources List */}
        {!isUser && !message.isLoading && message.sources && (
          <SourcesList sources={message.sources} />
        )}

        {/* Generated Files Downloads */}
        {!isUser && !message.isLoading && message.files && (
          <FileDownloads files={message.files} />
        )}

        {/* Explanation / Audit Button */}
        {!isUser && !message.isLoading && message.request_id && (
          <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between">
            <span className="text-[10px] font-mono text-slate-400">
              Audit ID: {message.request_id}
            </span>
            <button
              onClick={() => onViewExplanation(message.request_id!)}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-950/60 text-blue-300 hover:bg-blue-900/80 hover:text-white border border-blue-800/60 transition-all text-xs font-medium"
            >
              <Eye className="h-3.5 w-3.5" />
              <span>View Explanation</span>
            </button>
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex-shrink-0 h-9 w-9 rounded-xl bg-blue-700 text-white flex items-center justify-center shadow-md">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
};
