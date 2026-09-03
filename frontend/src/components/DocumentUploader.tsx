'use client';

import React, { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, FileCode, Trash2, Database } from 'lucide-react';
import { ingestFiles } from '@/lib/api';
import { IngestResponse } from '@/lib/types';

interface DocumentUploaderProps {
  onIngestSuccess: (data: IngestResponse) => void;
  onError: (errorMsg: string) => void;
}

interface SelectedFileItem {
  id: string;
  file: File;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
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
        // Prevent duplicate filenames in selection
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
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 glass-panel">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-blue-400" />
          <h2 className="text-sm font-semibold text-slate-200">
            Document Ingestion Pipeline
          </h2>
        </div>
        <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
          PDF, DOCX, XLSX, TXT
        </span>
      </div>

      {/* Drag and Drop Zone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-blue-500 bg-blue-950/30'
            : 'border-slate-800 hover:border-slate-700 bg-slate-950/60'
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

        <UploadCloud className="h-8 w-8 text-blue-400 mx-auto mb-2 opacity-80" />
        <p className="text-xs font-medium text-slate-300">
          Drag & drop confidential files or <span className="text-blue-400 underline">browse</span>
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Files stay stored on your local PSU server node
        </p>
      </div>

      {/* Selected File List */}
      {selectedFiles.length > 0 && (
        <div className="mt-3 space-y-1.5 max-h-40 overflow-y-auto pr-1">
          <div className="text-[11px] font-medium text-slate-400 px-1">
            Files queued for indexing ({selectedFiles.length}):
          </div>
          {selectedFiles.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between bg-slate-950/80 border border-slate-800 rounded-lg p-2 text-xs"
            >
              <div className="flex items-center gap-2 min-w-0">
                <FileText className="h-3.5 w-3.5 text-blue-400 flex-shrink-0" />
                <span className="text-slate-200 truncate font-mono text-[11px]">
                  {item.file.name}
                </span>
                <span className="text-[10px] text-slate-400 flex-shrink-0">
                  ({formatFileSize(item.file.size)})
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(item.id);
                }}
                className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                title="Remove file"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Ingest Action Button */}
      <div className="mt-3">
        <button
          onClick={handleIngest}
          disabled={selectedFiles.length === 0 || isUploading}
          className={`w-full py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
            selectedFiles.length > 0 && !isUploading
              ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20 active:scale-98'
              : 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/50'
          }`}
        >
          {isUploading ? (
            <>
              <div className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing & Chunking Documents...</span>
            </>
          ) : (
            <>
              <Database className="h-3.5 w-3.5" />
              <span>Ingest & Vectorize ({selectedFiles.length} files)</span>
            </>
          )}
        </button>
      </div>

      {/* Ingestion Result Message */}
      {lastResult && (
        <div className="mt-3 p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 text-xs flex items-center gap-2 animate-fadeIn">
          <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
          <div>
            <p className="font-semibold text-emerald-200">
              Ingestion Completed Successfully
            </p>
            <p className="text-[11px] text-emerald-400/90 font-mono">
              Indexed {lastResult.files_ingested} file(s) → {lastResult.chunks_created} vector chunks stored in FAISS / Chroma.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
