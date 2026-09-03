'use client';

import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { UploadCloud, FileText, CheckCircle2, Trash2, Database } from 'lucide-react';
import { ingestFiles } from '@/lib/api';
import { IngestResponse } from '@/lib/types';

interface DocumentUploaderCardProps {
  onIngestSuccess: (data: IngestResponse) => void;
  onError: (errorMsg: string) => void;
}

interface SelectedFileItem {
  id: string;
  file: File;
}

export const DocumentUploaderCard: React.FC<DocumentUploaderCardProps> = ({
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
    <div className="card-editorial bg-white p-6">
      {/* Editorial Title & Subtext */}
      <div className="mb-4">
        <h2 className="font-serif-display text-xl font-bold text-[#111318] tracking-tight">
          Feed it your docs
        </h2>
        <p className="text-xs text-[#525663] mt-1 leading-relaxed">
          PDF, DOCX, XLSX, TXT — everything stays on your isolated local servers.
        </p>
      </div>

      {/* Large dashed drop zone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-[#312E81] bg-[#EEF2FF]'
            : 'border-[#E2DDD5] hover:border-[#312E81] bg-[#FAF9F6]'
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

        <UploadCloud className="h-9 w-9 text-[#312E81] mx-auto mb-2 opacity-85" />
        <p className="text-xs font-semibold text-[#111318]">
          Drag & drop confidential files or <span className="text-[#312E81] underline">browse</span>
        </p>
        <p className="text-[11px] text-[#717582] mt-1 font-mono">
          Supports multi-file index ingestion
        </p>
      </div>

      {/* Selected File List */}
      {selectedFiles.length > 0 && (
        <div className="mt-3.5 space-y-2 max-h-40 overflow-y-auto pr-1">
          <div className="text-[11px] font-semibold text-[#525663] uppercase tracking-wider">
            Queued Files ({selectedFiles.length}):
          </div>
          {selectedFiles.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between bg-[#FAF9F6] border border-[#E5E2DC] rounded-lg p-2.5 text-xs"
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="h-3.5 w-3.5 text-[#312E81] flex-shrink-0" />
                <span className="text-[#111318] font-mono text-[11px] font-medium truncate">
                  {item.file.name}
                </span>
                <span className="text-[10px] text-[#717582] flex-shrink-0">
                  ({formatFileSize(item.file.size)})
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(item.id);
                }}
                className="text-[#717582] hover:text-rose-600 p-1 transition-colors"
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
          className={`w-full py-2.5 px-4 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
            selectedFiles.length > 0 && !isUploading
              ? 'button-primary shadow-md'
              : 'bg-[#E5E2DC] text-[#9CA3AF] cursor-not-allowed'
          }`}
        >
          {isUploading ? (
            <>
              <div className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Ingesting & Chunking...</span>
            </>
          ) : (
            <>
              <Database className="h-3.5 w-3.5" />
              <span>Ingest files ({selectedFiles.length})</span>
            </>
          )}
        </button>
      </div>

      {/* Small status text after ingestion */}
      {lastResult && (
        <div className="mt-3 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs flex items-start gap-2.5 animate-fadeIn">
          <CheckCircle2 className="h-4 w-4 text-emerald-700 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-emerald-950">Ingestion complete</p>
            <p className="text-[11px] text-emerald-800 font-mono mt-0.5">
              Ingested {lastResult.files_ingested} file(s), {lastResult.chunks_created} chunks created.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
