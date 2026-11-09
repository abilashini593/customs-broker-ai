"use client";

import React, { useState } from "react";
import { 
  X, 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  Trash2, 
  Sparkles, 
  FileType,
  ArrowRight,
  Layers
} from "lucide-react";

export interface UploadFileItem {
  id: string;
  name: string;
  size: number;
  type: "commercial_invoice" | "packing_list" | "bill_of_lading";
  file: File | null;
}

interface DocumentUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartExtraction: (files: UploadFileItem[]) => void;
}

export const DocumentUploadModal: React.FC<DocumentUploadModalProps> = ({
  isOpen,
  onClose,
  onStartExtraction,
}) => {
  const [supplierName, setSupplierName] = useState("Tokyo Semiconductor Systems Corp");
  const [supplierCountry, setSupplierCountry] = useState("Japan");
  const [consigneeName, setConsigneeName] = useState("Pacific Crest Electronics LLC");
  
  // Start with an empty list or your custom files so users are forced to upload real files
  const [files, setFiles] = useState<UploadFileItem[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  if (!isOpen) return null;

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newItems: UploadFileItem[] = Array.from(e.dataTransfer.files).map((f, i) => {
        let detectedType: "commercial_invoice" | "packing_list" | "bill_of_lading" = "commercial_invoice";
        const lower = f.name.toLowerCase();
        if (lower.includes("pack") || lower.includes("pl")) detectedType = "packing_list";
        else if (lower.includes("bl") || lower.includes("lading") || lower.includes("bill")) detectedType = "bill_of_lading";

        return {
          id: `f-${Date.now()}-${i}`,
          name: f.name,
          size: f.size,
          type: detectedType,
          file: f, // Real binary file attached!
        };
      });
      setFiles((prev) => [...prev, ...newItems]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newItems: UploadFileItem[] = Array.from(e.target.files).map((f, i) => {
        let detectedType: "commercial_invoice" | "packing_list" | "bill_of_lading" = "commercial_invoice";
        const lower = f.name.toLowerCase();
        if (lower.includes("pack") || lower.includes("pl")) detectedType = "packing_list";
        else if (lower.includes("bl") || lower.includes("lading") || lower.includes("bill")) detectedType = "bill_of_lading";

        return {
          id: `f-${Date.now()}-${i}`,
          name: f.name,
          size: f.size,
          type: detectedType,
          file: f, // Real binary file attached!
        };
      });
      setFiles((prev) => [...prev, ...newItems]);
    }
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((item) => item.id !== id));
  };

  const changeType = (id: string, newType: "commercial_invoice" | "packing_list" | "bill_of_lading") => {
    setFiles((prev) =>
      prev.map((f) => (f.id === id ? { ...f, type: newType } : f))
    );
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) return;
    onStartExtraction(files);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl bg-[#09090b] border border-zinc-800 rounded-2xl shadow-glass overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/90 bg-zinc-900/50">
          <div className="flex items-center space-x-2">
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-zinc-100">
                Ingest Shipment Documents
              </h2>
              <p className="text-xs text-zinc-400">
                Upload Commercial Invoice, Packing List, and Bill of Lading for automated AI parsing
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Metadata quick inputs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Declared Supplier
              </label>
              <input
                type="text"
                value={supplierName}
                onChange={(e) => setSupplierName(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-blue-500"
                placeholder="e.g. Tokyo Semiconductor Systems"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-zinc-400 mb-1">
                Consignee / Importer
              </label>
              <input
                type="text"
                value={consigneeName}
                onChange={(e) => setConsigneeName(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-blue-500"
                placeholder="e.g. Pacific Crest Electronics LLC"
              />
            </div>
          </div>

          {/* Drag & Drop Zone */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 ${
              isDragging
                ? "border-blue-500 bg-blue-500/5"
                : "border-zinc-800 hover:border-zinc-700 bg-zinc-950/40 hover:bg-zinc-950/60"
            }`}
          >
            <input
              type="file"
              id="file-upload-input"
              multiple
              accept=".pdf,.png,.jpg,.jpeg,.tiff"
              onChange={handleFileInput}
              className="hidden"
            />
            <label htmlFor="file-upload-input" className="cursor-pointer block">
              <UploadCloud className="w-8 h-8 text-blue-400 mx-auto mb-2 opacity-80" />
              <p className="text-xs font-medium text-zinc-200">
                Drag & drop customs documents here, or <span className="text-blue-400 underline">browse files</span>
              </p>
              <p className="text-[11px] text-zinc-500 mt-1">
                Upload your test PDF file here (e.g. TEST_NEW_INVOICE_INV_9999.pdf)
              </p>
            </label>
          </div>

          {/* Ingested Document List */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-medium text-zinc-400">
              <span className="flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-zinc-500" />
                <span>Selected Documents ({files.length})</span>
              </span>
              <span className="text-[11px] text-zinc-500">Auto-classified by Vision Parser</span>
            </div>

            <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
              {files.length === 0 ? (
                <div className="text-center py-6 text-zinc-500 text-xs border border-dashed border-zinc-800/60 rounded-xl">
                  No files selected yet. Upload your PDF to begin.
                </div>
              ) : (
                files.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700 transition"
                  >
                    <div className="flex items-center space-x-3 overflow-hidden">
                      <div className="p-2 rounded-lg bg-zinc-800 text-zinc-300 flex-shrink-0">
                        <FileText className="w-4 h-4 text-blue-400" />
                      </div>
                      <div className="truncate">
                        <p className="text-xs font-medium text-zinc-200 truncate">{file.name}</p>
                        <p className="text-[10px] text-zinc-500 font-mono">{formatSize(file.size)}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 flex-shrink-0">
                      <select
                        value={file.type}
                        onChange={(e) => changeType(file.id, e.target.value as any)}
                        className="bg-zinc-950 border border-zinc-800 rounded-lg text-[11px] font-medium text-zinc-300 py-1 px-2 focus:outline-none focus:border-blue-500"
                      >
                        <option value="commercial_invoice">Commercial Invoice</option>
                        <option value="packing_list">Packing List</option>
                        <option value="bill_of_lading">Bill of Lading</option>
                      </select>

                      <button
                        type="button"
                        onClick={() => removeFile(file.id)}
                        className="p-1 rounded-lg text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 transition"
                        title="Remove document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-between pt-3 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60 transition"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={files.length === 0}
              className="inline-flex items-center space-x-2 px-5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-500 hover:from-blue-500 hover:to-emerald-400 text-white shadow-lg shadow-indigo-900/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch AI Extraction & Cross-Check</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};