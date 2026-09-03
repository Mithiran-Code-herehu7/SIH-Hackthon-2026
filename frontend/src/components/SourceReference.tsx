'use client';

import React from 'react';
import { FileText, Bookmark } from 'lucide-react';
import { SourceItem } from '@/lib/types';

interface SourceReferenceProps {
  source: SourceItem;
}

export const SourceReferenceItem: React.FC<SourceReferenceProps> = ({ source }) => {
  return (
    <div className="flex items-center gap-2 bg-[#F5F2EB] hover:bg-[#EAE5DC] border border-[#DCD7CE] rounded-lg px-3 py-1.5 transition-all text-xs flex-shrink-0 group">
      <FileText className="h-3.5 w-3.5 text-[#2C2B5B] flex-shrink-0" />
      <span className="font-mono text-[11px] font-semibold text-[#1C1B24] truncate max-w-[170px]">
        {source.file}
      </span>
      {(source.page !== undefined || source.section) && (
        <span className="px-1.5 py-0.2 rounded bg-[#EAE5DC] text-[#2C2B5B] text-[10px] font-mono font-medium border border-[#DCD7CE]">
          {source.page !== undefined ? `p.${source.page}` : ''}
          {source.page !== undefined && source.section ? ' • ' : ''}
          {source.section ? `sec.${source.section}` : ''}
        </span>
      )}
    </div>
  );
};

interface SourceReferenceSectionProps {
  sources: SourceItem[];
}

export const SourceReferenceSection: React.FC<SourceReferenceSectionProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-5 pt-4 border-t border-[#DCD7CE]/80 text-left">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-[#666370] mb-2.5 uppercase tracking-wider font-sans">
        <Bookmark className="h-3.5 w-3.5 text-[#2C2B5B]" />
        <span>From your files ({sources.length})</span>
      </div>
      <div className="flex items-center gap-2 overflow-x-auto pb-1.5 scrollbar-thin">
        {sources.map((src, index) => (
          <SourceReferenceItem key={index} source={src} />
        ))}
      </div>
    </div>
  );
};
