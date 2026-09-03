'use client';

import React, { useState } from 'react';
import { Download, FileSpreadsheet, Presentation, FileText, Package, Check } from 'lucide-react';
import { GeneratedFile } from '@/lib/types';
import { getFileUrl } from '@/lib/api';

interface DeliverableCardProps {
  file: GeneratedFile;
}

export const DeliverableCard: React.FC<DeliverableCardProps> = ({ file }) => {
  const [downloading, setDownloading] = useState(false);
  const downloadUrl = getFileUrl(file.download_url);

  const handleDownloadClick = () => {
    setDownloading(true);
    setTimeout(() => {
      setDownloading(false);
    }, 2000);
  };

  const getFileIcon = (type: string, name: string) => {
    const ext = name.split('.').pop()?.toLowerCase() || '';
    if (type === 'ppt' || ext === 'pptx' || ext === 'ppt') {
      return <Presentation className="h-4 w-4 text-[#2C2B5B]" />;
    }
    if (type === 'excel' || ext === 'xlsx' || ext === 'xls' || ext === 'csv') {
      return <FileSpreadsheet className="h-4 w-4 text-[#2C2B5B]" />;
    }
    if (type === 'word' || type === 'report' || ext === 'docx' || ext === 'pdf') {
      return <FileText className="h-4 w-4 text-[#2C2B5B]" />;
    }
    return <Package className="h-4 w-4 text-[#2C2B5B]" />;
  };

  const getFileTypeLabel = (type: string, name: string) => {
    const ext = name.split('.').pop()?.toUpperCase() || 'FILE';
    if (type === 'ppt') return `PowerPoint Deck (${ext})`;
    if (type === 'excel') return `Excel Spreadsheet (${ext})`;
    if (type === 'report') return `Audit Report (${ext})`;
    return `${type.toUpperCase()} Document (${ext})`;
  };

  return (
    <a
      href={downloadUrl}
      target="_blank"
      rel="noopener noreferrer"
      download={file.name}
      onClick={handleDownloadClick}
      className="flex items-center justify-between p-3 rounded-xl bg-[#F5F2EB] border border-[#DCD7CE] hover:border-[#2C2B5B] hover:bg-[#FAF8F4] hover:shadow-xs transition-all group min-w-[240px] focus-visible:ring-2 focus-visible:ring-[#2C2B5B]"
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className="p-2 rounded-lg bg-[#FAF8F4] border border-[#DCD7CE] group-hover:border-[#2C2B5B]/40 transition-colors">
          {getFileIcon(file.type, file.name)}
        </div>
        <div className="min-w-0 text-left">
          <p className="text-xs font-semibold text-[#1C1B24] truncate group-hover:text-[#2C2B5B] transition-colors">
            {file.name}
          </p>
          <p className="text-[11px] text-[#666370] font-medium">
            {getFileTypeLabel(file.type, file.name)}
          </p>
        </div>
      </div>

      <div
        className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ml-3 flex-shrink-0 active:scale-95 ${
          downloading
            ? 'bg-[#2C2B5B] text-white'
            : 'bg-[#2C2B5B] text-[#FAF8F4] hover:bg-[#1D1C40]'
        }`}
      >
        {downloading ? (
          <>
            <Check className="h-3.5 w-3.5" />
            <span className="hidden xs:inline">Downloaded</span>
          </>
        ) : (
          <>
            <Download className="h-3.5 w-3.5" />
            <span className="hidden xs:inline">Download</span>
          </>
        )}
      </div>
    </a>
  );
};

interface DeliverablesSectionProps {
  files: GeneratedFile[];
}

export const DeliverablesSection: React.FC<DeliverablesSectionProps> = ({ files }) => {
  if (!files || files.length === 0) return null;

  return (
    <div className="mt-5 pt-4 border-t border-[#DCD7CE]/80 text-left">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-[#666370] mb-2.5 uppercase tracking-wider font-sans">
        <Package className="h-3.5 w-3.5 text-[#2C2B5B]" />
        <span>Ready to use ({files.length})</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {files.map((file, idx) => (
          <DeliverableCard key={idx} file={file} />
        ))}
      </div>
    </div>
  );
};
