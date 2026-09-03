'use client';

import React from 'react';
import { FileText, Bookmark } from 'lucide-react';
import { SourceItem } from '@/lib/types';

interface SourcesListProps {
  sources: SourceItem[];
}

export const SourcesList: React.FC<SourcesListProps> = ({ sources }) => {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-slate-800/80">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 mb-2">
        <Bookmark className="h-3.5 w-3.5 text-blue-400" />
        <span>Sources & Cited References ({sources.length}):</span>
      </div>
      <ul className="space-y-1.5 pl-1">
        {sources.map((src, index) => (
          <li
            key={index}
            className="flex items-center text-xs text-slate-300 bg-slate-900/60 border border-slate-800 rounded-md px-2.5 py-1.5 hover:bg-slate-900 transition-colors"
          >
            <FileText className="h-3.5 w-3.5 text-slate-400 mr-2 flex-shrink-0" />
            <span className="font-mono text-blue-300 font-medium truncate max-w-[200px] sm:max-w-xs">
              {src.file}
            </span>
            {(src.page !== undefined || src.section) && (
              <span className="ml-2 px-1.5 py-0.5 rounded bg-blue-950/80 text-blue-300 text-[10px] font-mono border border-blue-800/50">
                {src.page !== undefined ? `Page ${src.page}` : ''}
                {src.page !== undefined && src.section ? ' • ' : ''}
                {src.section ? `Section ${src.section}` : ''}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};
