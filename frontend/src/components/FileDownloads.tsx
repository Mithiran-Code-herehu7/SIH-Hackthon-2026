'use client';

import React from 'react';
import { Download, FileSpreadsheet, Presentation, FileText, Package } from 'lucide-react';
import { GeneratedFile } from '@/lib/types';
import { getFileUrl } from '@/lib/api';

interface FileDownloadsProps {
  files: GeneratedFile[];
}

export const FileDownloads: React.FC<FileDownloadsProps> = ({ files }) => {
  if (!files || files.length === 0) return null;

  const getFileIcon = (type: string, name: string) => {
    const ext = name.split('.').pop()?.toLowerCase() || '';
    if (type === 'ppt' || ext === 'pptx' || ext === 'ppt') {
      return <Presentation className="h-4 w-4 text-amber-400" />;
    }
    if (type === 'excel' || ext === 'xlsx' || ext === 'xls' || ext === 'csv') {
      return <FileSpreadsheet className="h-4 w-4 text-emerald-400" />;
    }
    if (type === 'word' || type === 'report' || ext === 'docx' || ext === 'pdf') {
      return <FileText className="h-4 w-4 text-blue-400" />;
    }
    return <Package className="h-4 w-4 text-cyan-400" />;
  };

  const getFileTypeLabel = (type: string, name: string) => {
    const ext = name.split('.').pop()?.toUpperCase() || 'FILE';
    if (type === 'ppt') return `PowerPoint (${ext})`;
    if (type === 'excel') return `Excel Spreadsheet (${ext})`;
    if (type === 'report') return `Technical Report (${ext})`;
    return `${type.toUpperCase()} (${ext})`;
  };

  return (
    <div className="mt-4 pt-3 border-t border-slate-800/80">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 mb-2">
        <Package className="h-3.5 w-3.5 text-cyan-400" />
        <span>Generated Artifacts & Files ({files.length}):</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {files.map((file, idx) => {
          const downloadUrl = getFileUrl(file.download_url);
          return (
            <a
              key={idx}
              href={downloadUrl}
              target="_blank"
              rel="noopener noreferrer"
              download={file.name}
              className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-850 transition-all group shadow-sm"
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="p-1.5 rounded-md bg-slate-950 border border-slate-800 group-hover:border-slate-700">
                  {getFileIcon(file.type, file.name)}
                </div>
                <div className="min-w-0">
                  <p className="text-xs font-medium text-slate-200 truncate group-hover:text-blue-300 transition-colors">
                    {file.name}
                  </p>
                  <p className="text-[10px] text-slate-400">
                    {getFileTypeLabel(file.type, file.name)}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1 px-2 py-1 rounded bg-blue-600/20 text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-all text-xs font-medium ml-2 flex-shrink-0">
                <Download className="h-3.5 w-3.5" />
                <span className="hidden xs:inline">Download</span>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
};
