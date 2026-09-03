'use client';

import React from 'react';
import { Download, FileSpreadsheet, Presentation, FileText, Package } from 'lucide-react';
import { GeneratedFile } from '@/lib/types';
import { getFileUrl } from '@/lib/api';

interface FileCardProps {
  file: GeneratedFile;
}

export const FileCard: React.FC<FileCardProps> = ({ file }) => {
  const downloadUrl = getFileUrl(file.download_url);

  const getFileIcon = (type: string, name: string) => {
    const ext = name.split('.').pop()?.toLowerCase() || '';
    if (type === 'ppt' || ext === 'pptx' || ext === 'ppt') {
      return <Presentation className="h-4 w-4 text-amber-700" />;
    }
    if (type === 'excel' || ext === 'xlsx' || ext === 'xls' || ext === 'csv') {
      return <FileSpreadsheet className="h-4 w-4 text-emerald-700" />;
    }
    if (type === 'word' || type === 'report' || ext === 'docx' || ext === 'pdf') {
      return <FileText className="h-4 w-4 text-indigo-700" />;
    }
    return <Package className="h-4 w-4 text-slate-700" />;
  };

  const getFileTypeLabel = (type: string, name: string) => {
    const ext = name.split('.').pop()?.toUpperCase() || 'FILE';
    if (type === 'ppt') return `PowerPoint (${ext})`;
    if (type === 'excel') return `Excel Sheet (${ext})`;
    if (type === 'report') return `Audit Report (${ext})`;
    return `${type.toUpperCase()} (${ext})`;
  };

  return (
    <a
      href={downloadUrl}
      target="_blank"
      rel="noopener noreferrer"
      download={file.name}
      className="flex items-center justify-between p-3 rounded-xl bg-[#FAF9F6] border border-[#E5E2DC] hover:border-[#312E81] hover:bg-white hover:shadow-md transition-all group min-w-[240px]"
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="p-2 rounded-lg bg-white border border-[#E2DDD5] group-hover:border-[#C7D2FE] transition-colors">
          {getFileIcon(file.type, file.name)}
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold text-[#111318] truncate group-hover:text-[#312E81] transition-colors">
            {file.name}
          </p>
          <p className="text-[11px] text-[#525663] font-medium">
            {getFileTypeLabel(file.type, file.name)}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#312E81] text-white text-xs font-medium group-hover:bg-[#1E1B4B] transition-all ml-3 flex-shrink-0 shadow-xs">
        <Download className="h-3.5 w-3.5" />
        <span className="hidden xs:inline">Download</span>
      </div>
    </a>
  );
};

interface FileCardsRowProps {
  files: GeneratedFile[];
}

export const FileCardsRow: React.FC<FileCardsRowProps> = ({ files }) => {
  if (!files || files.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-[#E8E5DF]">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-[#525663] mb-2.5 uppercase tracking-wider font-sans">
        <Package className="h-3.5 w-3.5 text-[#312E81]" />
        <span>Generated Deliverables ({files.length})</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {files.map((file, idx) => (
          <FileCard key={idx} file={file} />
        ))}
      </div>
    </div>
  );
};
