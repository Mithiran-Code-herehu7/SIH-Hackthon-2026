'use client';

import React, { KeyboardEvent, useRef, useEffect } from 'react';
import { Send, Presentation, FileSpreadsheet, FileText, MessageSquare } from 'lucide-react';
import { TaskMode } from '@/lib/types';

interface ChatComposerProps {
  onSend: (query: string, mode: TaskMode) => void;
  isLoading: boolean;
  selectedMode: TaskMode;
  onModeChange: (mode: TaskMode) => void;
  inputQuery: string;
  onQueryChange: (query: string) => void;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({
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
    { mode: 'chat', label: 'Ask a question', icon: <MessageSquare className="h-3.5 w-3.5" /> },
    { mode: 'generate_ppt', label: 'Build PPT deck', icon: <Presentation className="h-3.5 w-3.5" /> },
    { mode: 'generate_excel', label: 'Create Excel sheet', icon: <FileSpreadsheet className="h-3.5 w-3.5" /> },
    { mode: 'generate_report', label: 'Compile report', icon: <FileText className="h-3.5 w-3.5" /> },
  ];

  return (
    <div className="w-full border-t border-[#DCD7CE] bg-[#F5F2EB]/95 p-3.5 sm:p-4 rounded-b-2xl">
      {/* Mode Pills with Natural Labels */}
      <div className="flex items-center justify-between gap-2 mb-2.5">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          <span className="text-[11px] font-semibold text-[#666370] uppercase tracking-wider mr-1 hidden xs:inline font-sans">
            Action Mode:
          </span>
          {modeOptions.map((opt) => (
            <button
              key={opt.mode}
              onClick={() => onModeChange(opt.mode)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold transition-all ${
                selectedMode === opt.mode
                  ? 'bg-[#2C2B5B] text-[#FAF8F4] shadow-2xs'
                  : 'bg-[#FAF8F4] text-[#666370] hover:text-[#1C1B24] hover:bg-[#EAE5DC] border border-[#DCD7CE]'
              }`}
            >
              <span>{opt.icon}</span>
              <span>{opt.label}</span>
            </button>
          ))}
        </div>

        <span className="text-[11px] text-[#666370] hidden sm:inline font-mono">
          <kbd className="px-1.5 py-0.5 rounded bg-[#FAF8F4] border border-[#DCD7CE] text-[#1C1B24]">Enter</kbd> to send
        </span>
      </div>

      {/* Multi-line Query Input */}
      <div className="relative flex items-end gap-3 bg-[#FAF8F4] border border-[#DCD7CE] focus-within:border-[#2C2B5B] focus-within:ring-2 focus-within:ring-[#2C2B5B]/20 rounded-2xl p-3 transition-all shadow-2xs">
        <textarea
          ref={textareaRef}
          value={inputQuery}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your indexed confidential docs or request a deliverable..."
          rows={1}
          disabled={isLoading}
          className="w-full bg-transparent text-[#1C1B24] placeholder-[#9CA3AF] text-sm focus:outline-none resize-none min-h-[42px] max-h-[160px] py-1 font-sans"
        />

        <button
          onClick={handleSubmit}
          disabled={!inputQuery.trim() || isLoading}
          className={`flex items-center justify-center h-10 w-10 rounded-xl font-medium transition-all flex-shrink-0 ${
            inputQuery.trim() && !isLoading
              ? 'btn-retro shadow-xs active:scale-95'
              : 'bg-[#DCD7CE] text-[#8C8780] cursor-not-allowed'
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
