'use client';

import React, { KeyboardEvent, useRef, useEffect } from 'react';
import { Send, Presentation, FileSpreadsheet, FileText, MessageSquare } from 'lucide-react';
import { TaskMode } from '@/lib/types';

interface ChatInputProps {
  onSend: (query: string, mode: TaskMode) => void;
  isLoading: boolean;
  selectedMode: TaskMode;
  onModeChange: (mode: TaskMode) => void;
  inputQuery: string;
  onQueryChange: (query: string) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  isLoading,
  selectedMode,
  onModeChange,
  inputQuery,
  onQueryChange,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [inputQuery]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!inputQuery.trim() || isLoading) return;
    onSend(inputQuery, selectedMode);
  };

  const modeOptions: { mode: TaskMode; label: string; icon: React.ReactNode }[] = [
    { mode: 'chat', label: 'Chat', icon: <MessageSquare className="h-3.5 w-3.5" /> },
    { mode: 'generate_ppt', label: 'Generate PPT', icon: <Presentation className="h-3.5 w-3.5" /> },
    { mode: 'generate_excel', label: 'Generate Excel', icon: <FileSpreadsheet className="h-3.5 w-3.5" /> },
    { mode: 'generate_report', label: 'Generate Report', icon: <FileText className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="w-full border-t border-[#E8E5DF] bg-[#FAF9F6]/95 p-3.5 sm:p-4 rounded-b-[1.25rem]">
      {/* Task Mode Pills */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          <span className="text-[11px] font-semibold text-[#525663] uppercase tracking-wider mr-1 hidden xs:inline">
            Task Mode:
          </span>
          {modeOptions.map((opt) => (
            <button
              key={opt.mode}
              onClick={() => onModeChange(opt.mode)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                selectedMode === opt.mode
                  ? 'bg-[#312E81] text-white shadow-xs'
                  : 'bg-white text-[#525663] hover:text-[#111318] hover:bg-[#F0EDE6] border border-[#E5E2DC]'
              }`}
            >
              <span>{opt.icon}</span>
              <span>{opt.label}</span>
            </button>
          ))}
        </div>

        <span className="text-[11px] text-[#717582] hidden sm:inline font-mono">
          <kbd className="px-1.5 py-0.5 rounded bg-white border border-[#E5E2DC] text-[#111318]">Enter</kbd> to send
        </span>
      </div>

      {/* Multi-line Query Input */}
      <div className="relative flex items-end gap-3 bg-white border border-[#E5E2DC] focus-within:border-[#312E81] focus-within:ring-2 focus-within:ring-[#C7D2FE] rounded-xl p-3 transition-all shadow-xs">
        <textarea
          ref={textareaRef}
          value={inputQuery}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your confidential docs. Or try a demo on the right..."
          rows={1}
          disabled={isLoading}
          className="w-full bg-transparent text-[#111318] placeholder-[#9CA3AF] text-sm focus:outline-none resize-none min-h-[42px] max-h-[160px] py-1 font-sans"
        />

        <button
          onClick={handleSubmit}
          disabled={!inputQuery.trim() || isLoading}
          className={`flex items-center justify-center h-10 w-10 rounded-xl font-medium transition-all flex-shrink-0 ${
            inputQuery.trim() && !isLoading
              ? 'button-primary shadow-md active:scale-95'
              : 'bg-[#E5E2DC] text-[#9CA3AF] cursor-not-allowed'
          }`}
          title="Send Task / Query"
        >
          {isLoading ? (
            <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <Send className="h-4 w-4" />
          )}
        </button>
      </div>
    </div>
  );
};
