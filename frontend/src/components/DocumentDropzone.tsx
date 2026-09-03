'use client';

import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { FileText, CheckCircle2, Trash2, FolderPlus } from 'lucide-react';
import { ingestFiles } from '@/lib/api';
import { IngestResponse } from '@/lib/types';

interface DocumentDropzoneProps {
  onIngestSuccess: (data: IngestResponse) => void;
  onError: (errorMsg: string) => void;
}

interface SelectedFileItem {
  id: string;
  file: File;
}

export const DocumentDropzone: React.FC<DocumentDropzoneProps> = ({
  onIngestSuccess,
  onError,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<SelectedFileItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [lastResult, setLastResult] = useState<IngestResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFilesAdded = (files: FileList | File[]) => {
    const validExtensions = ['.pdf', '.docx', '.xlsx', '.txt'];
    const newItems: SelectedFileItem[] = [];

    Array.from(files).forEach((file) => {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (validExtensions.includes(ext)) {
        if (!selectedFiles.some((f) => f.file.name === file.name)) {
          newItems.push({
            id: Math.random().toString(36).substring(2, 9),
            file,
          });
        }
      }
    });

    if (newItems.length > 0) {
      setSelectedFiles((prev) => [...prev, ...newItems]);
      setLastResult(null);
    }
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesAdded(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFilesAdded(e.target.files);
    }
  };

  const removeFile = (id: string) => {
    setSelectedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleIngest = async () => {
    if (selectedFiles.length === 0 || isUploading) return;

    setIsUploading(true);
    setLastResult(null);

    try {
      const filesToUpload = selectedFiles.map((item) => item.file);
      const res = await ingestFiles(filesToUpload);
      setLastResult(res);
      onIngestSuccess(res);
      setSelectedFiles([]);
    } catch (err: any) {
      const msg = err?.message || 'Ingestion failed';
      onError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div id="document-dropzone-card" className="surface-card rounded-2xl p-6 w-full animate-fade-slide-up">
      {/* Title & Description */}
      <div className="mb-4 text-left">
        <h3 className="font-display-serif text-2xl font-bold text-[#1C1B24] tracking-tight">
          Give the workbench something to read
        </h3>
        <p className="text-xs sm:text-sm text-[#666370] mt-1 leading-relaxed">
          Drop in reports, procedures, spreadsheets, or notes. They stay inside this workspace.
        </p>
      </div>

      {/* Large Full-Width Organic Dropzone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all duration-200 ${
          dragActive
            ? 'border-[#2C2B5B] bg-[#EAE5DC]'
            : 'border-[#DCD7CE] hover:border-[#2C2B5B] bg-[#F5F2EB]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.xlsx,.txt"
          onChange={handleFileInputChange}
          className="hidden"
        />

        {/* Retro Single-Color SVG Illustration */}
        <div className="w-10 h-10 mx-auto mb-2 text-[#2C2B5B] flex items-center justify-center">
          <svg className="w-9 h-9 stroke-current fill-none" viewBox="0 0 24 24" strokeWidth="1.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        </div>

        <p className="text-xs font-semibold text-[#1C1B24]">
          Drop confidential files here or <span className="text-[#2C2B5B] underline">browse</span>
        </p>
        <p className="text-[11px] text-[#666370] mt-1 font-mono">
          PDF, DOCX, XLSX, TXT (on-premise only)
        </p>
      </div>

      {/* Selected File Queue */}
      {selectedFiles.length > 0 && (
        <div className="mt-4 space-y-2 max-h-44 overflow-y-auto pr-1">
          <div className="text-[11px] font-semibold text-[#666370] uppercase tracking-wider text-left">
            Queued for indexing ({selectedFiles.length}):
          </div>
          {selectedFiles.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between bg-[#F5F2EB] border border-[#DCD7CE] rounded-xl p-2.5 text-xs"
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="h-3.5 w-3.5 text-[#2C2B5B] flex-shrink-0" />
                <span className="text-[#1C1B24] font-mono text-[11px] font-medium truncate">
                  {item.file.name}
                </span>
                <span className="text-[10px] text-[#666370] flex-shrink-0">
                  ({formatFileSize(item.file.size)})
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(item.id);
                }}
                className="text-[#666370] hover:text-rose-600 p-1 transition-colors"
                title="Remove file"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Primary Ingest Button */}
      <div className="mt-4">
        <button
          onClick={handleIngest}
          disabled={selectedFiles.length === 0 || isUploading}
          className={`w-full py-3 px-4 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
            selectedFiles.length > 0 && !isUploading
              ? 'btn-retro shadow-xs'
              : 'bg-[#DCD7CE] text-[#8C8780] cursor-not-allowed'
          }`}
        >
          {isUploading ? (
            <>
              <div className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Indexing documents into vector store...</span>
            </>
          ) : (
            <>
              <FolderPlus className="h-4 w-4" />
              <span>Ingest files ({selectedFiles.length})</span>
            </>
          )}
        </button>
      </div>

      {/* Warm Success State */}
      {lastResult && (
        <div className="mt-3.5 p-3 rounded-xl bg-[#EAE5DC] border border-[#DCD7CE] text-[#1C1B24] text-xs flex items-start gap-2.5">
          <CheckCircle2 className="h-4 w-4 text-[#2C2B5B] flex-shrink-0 mt-0.5" />
          <div className="text-left">
            <p className="font-semibold text-[#1C1B24]">Your workspace is up to date.</p>
            <p className="text-[11px] text-[#2C2B5B] font-mono mt-0.5">
              Ingested {lastResult.files_ingested} file(s), {lastResult.chunks_created} vector chunks created.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
