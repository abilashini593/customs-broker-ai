"use client";

import React, { useState } from "react";
import { 
  X, 
  Download, 
  FileSpreadsheet, 
  CheckCircle2, 
  Copy, 
  Check, 
  ShieldCheck, 
  Sparkles,
  ArrowRight
} from "lucide-react";
import { ShipmentDetail } from "../lib/api";

interface ExportApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  shipment: ShipmentDetail;
  onConfirmExport: (format: "csv" | "xlsx") => Promise<{ file_name: string; preview_content: string }>;
  userRole: "Documentation Executive" | "Documentation Manager";
}

export const ExportApprovalModal: React.FC<ExportApprovalModalProps> = ({
  isOpen,
  onClose,
  shipment,
  onConfirmExport,
  userRole,
}) => {
  const [format, setFormat] = useState<"csv" | "xlsx">("csv");
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<{ file_name: string; preview_content: string } | null>(null);
  const [copied, setCopied] = useState(false);
  const [showToast, setShowToast] = useState(false);

  if (!isOpen) return null;

  const handleExport = async () => {
    try {
      setIsExporting(true);
      const res = await onConfirmExport(format);
      setExportResult(res);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 4000);
    } catch (err) {
      console.error(err);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadFile = () => {
    if (!exportResult) return;
    const downloadUrl = `http://localhost:8000/api/shipments/${shipment.id}/export/download/${exportResult.file_name}`;
    window.open(downloadUrl, "_blank");
  };

  const handleCopyClipboard = () => {
    if (!exportResult) return;
    navigator.clipboard.writeText(exportResult.preview_content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
      <div className="relative w-full max-w-3xl bg-[#09090b] border border-zinc-800 rounded-2xl shadow-glass overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Toast Notification */}
        {showToast && (
          <div className="absolute top-4 right-4 z-50 flex items-center space-x-2 bg-emerald-500 text-black px-4 py-2.5 rounded-xl text-xs font-bold shadow-2xl animate-in slide-in-from-top-2">
            <CheckCircle2 className="w-4 h-4 text-black" />
            <span>Customs declaration successfully compiled & filed!</span>
          </div>
        )}

        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800/90 bg-zinc-900/50">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-zinc-100">
                Customs Filing Software Export (EDI)
              </h3>
              <p className="text-xs text-zinc-400">
                Single Window Customs Declaration • ICEGATE & US CBP ACE Compatible
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-5">
          {/* Signatory Banner */}
          <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 flex items-center justify-between text-xs">
            <div className="flex items-center space-x-3">
              <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0" />
              <div>
                <p className="font-semibold text-zinc-200">
                  Authorized Signatory: <span className="text-blue-400">{userRole}</span>
                </p>
                <p className="text-[11px] text-zinc-400">
                  Docket: {shipment.shipment_number} | Total Declared: ${shipment.total_declared_value.toLocaleString()} USD
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2 bg-zinc-950 p-1 rounded-lg border border-zinc-800">
              <button
                onClick={() => {
                  setFormat("csv");
                  setExportResult(null);
                }}
                className={`px-3 py-1 rounded text-xs font-mono font-medium transition ${
                  format === "csv" ? "bg-zinc-800 text-zinc-100 border border-zinc-700" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                CSV EDI
              </button>
              <button
                onClick={() => {
                  setFormat("xlsx");
                  setExportResult(null);
                }}
                className={`px-3 py-1 rounded text-xs font-mono font-medium transition ${
                  format === "xlsx" ? "bg-zinc-800 text-zinc-100 border border-zinc-700" : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                Excel Sheet
              </button>
            </div>
          </div>

          {/* Export Preview Area */}
          <div>
            <div className="flex items-center justify-between text-xs font-medium text-zinc-400 mb-2">
              <span>Standard Declaration Layout Preview</span>
              {exportResult && (
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleCopyClipboard}
                    className="flex items-center space-x-1 text-[11px] text-zinc-400 hover:text-zinc-200 bg-zinc-900 px-2 py-1 rounded border border-zinc-800"
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copied ? "Copied" : "Copy Manifest"}</span>
                  </button>
                  <button
                    onClick={handleDownloadFile}
                    className="flex items-center space-x-1 text-[11px] text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/30"
                  >
                    <Download className="w-3 h-3" />
                    <span>Download File</span>
                  </button>
                </div>
              )}
            </div>

            <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 font-mono text-[11px] text-zinc-300 max-h-72 overflow-y-auto whitespace-pre leading-relaxed select-all">
              {exportResult ? (
                exportResult.preview_content
              ) : (
                <div className="text-zinc-500 text-center py-10 font-sans">
                  Click &quot;Compile &amp; Generate Filing Manifest&quot; below to generate the exact customs declaration layout for {format.toUpperCase()}.
                </div>
              )}
            </div>
          </div>

          {/* Footer Action */}
          <div className="flex items-center justify-between pt-3 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
            >
              Close
            </button>

            {!exportResult ? (
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white shadow-lg shadow-emerald-900/30 transition-all disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isExporting ? "Compiling Manifest..." : "Compile & Generate Filing Manifest"}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                onClick={handleDownloadFile}
                className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-black shadow-lg shadow-emerald-900/40 transition-all font-bold"
              >
                <Download className="w-4 h-4 text-black" />
                <span>Download {exportResult.file_name}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};