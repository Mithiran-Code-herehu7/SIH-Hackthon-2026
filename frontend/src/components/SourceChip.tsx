'use client';

import React from 'react';
import { FileText, Bookmark } from 'lucide-react';
import { SourceItem } from '@/lib/types';

interface SourceChipProps {
  source: SourceItem;
}

export const SourceChip: React.FC<SourceChipProps> = ({ source }) => {
  return (
    <div className="flex items-center gap-2 bg-[#F7F5F2] hover:bg-[#EFECE6] border border-[#E2DDD5] rounded-lg px-3 py-1.5 transition-all text-xs flex-shrink-0 group">
      <FileText className="h-3.5 w-3.5 text-[#312E81] flex-shrink-0" />
      <span className="font-mono text-[11px] font-semibold text-[#111318] truncate max-w-[160px]">
        {source.file}
      </span>
      {(source.page !== undefined || source.section) && (
        <span className="px-1.5 py-0.5 rounded bg-[#EEF2FF] text-[#312E81] text-[10px] font-mono font-semibold border border-[#C7D2FE]">
          {source.page !== undefined ? `p.${source.page}` : ''}
          {source.page !== undefined && source.section ? ' • ' : ''}
          {source.section ? `sec.${source.section}` : ''}
        </span>
      )}
    </div>
  );
};

interface SourcesRowProps {
  sources: SourceItem[];
}

export const SourcesRow: React.FC<SourcesRowProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-[#E8E5DF]">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-[#525663] mb-2.5 uppercase tracking-wider font-sans">
        <Bookmark className="h-3.5 w-3.5 text-[#312E81]" />
        <span>Retrieved Sources & References ({sources.length})</span>
      </div>
      <div className="flex items-center gap-2 overflow-x-auto pb-1.5 scrollbar-thin">
        {sources.map((src, index) => (
          <SourceChip key={index} source={src} />
        ))}
      </div>
    </div>
  );
};
