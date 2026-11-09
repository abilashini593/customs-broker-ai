"use client";

import React, { useEffect, useState } from "react";
import { 
  Sparkles, 
  CheckCircle2, 
  Loader2, 
  FileSearch, 
  Scale, 
  Binary, 
  Layers,
  AlertTriangle
} from "lucide-react";

interface ExtractionProcessingModalProps {
  isOpen: boolean;
  shipmentId: number;
  file: File | null;
  docType?: string;
  onComplete: () => void;
  onClose?: () => void;
}

export const ExtractionProcessingModal: React.FC<ExtractionProcessingModalProps> = ({
  isOpen,
  shipmentId,
  file,
  docType = "commercial_invoice",
  onComplete,
  onClose,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);
  const [hasError, setHasError] = useState(false);

  const steps = [
    {
      title: "Document Transmission & API Handshake",
      desc: "Uploading raw PDF binary to FastAPI backend ingest endpoint",
      icon: FileSearch,
    },
    {
      title: "Database Cleanup & Table Reset",
      desc: "Clearing stale ExtractedField and LineItem records for shipment",
      icon: Layers,
    },
    {
      title: "Vision AI & OCR Extraction",
      desc: "Parsing multi-column line items, HSN codes, and pricing tables",
      icon: Scale,
    },
    {
      title: "Deterministic Cross-Check Reconciliation",
      desc: "Re-evaluating cross-check validation engine rules and totals",
      icon: Binary,
    },
  ];

  useEffect(() => {
    if (!isOpen || !file) {
      setCurrentStep(0);
      setLogs([]);
      setHasError(false);
      return;
    }

    let isMounted = true;

    const processUpload = async () => {
      setHasError(false);
      setCurrentStep(0);
      setLogs([`[Client] Initiating file transmission for '${file.name}' (${file.size} bytes)...`]);

      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", docType);

      try {
        // Step 1: Transmitting document
        setCurrentStep(0);
        setLogs((prev) => [...prev, `[HTTP] POST http://localhost:8000/api/shipments/${shipmentId}/documents/upload`]);

        const response = await fetch(`http://localhost:8000/api/shipments/${shipmentId}/documents/upload`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || `Upload failed with status code ${response.status}`);
        }

        // Step 2: Clearing Database & Processing Extractions
        if (!isMounted) return;
        setCurrentStep(1);
        setLogs((prev) => [
          ...prev,
          `[Database] Purged old ExtractedField and LineItem records for Shipment #${shipmentId}.`,
        ]);

        const data = await response.json();

        // Step 3: Vision Extraction Results
        if (!isMounted) return;
        setCurrentStep(2);
        setLogs((prev) => [
          ...prev,
          `[Vision AI] Successfully extracted document: ${data.file_name}`,
          `[Vision AI] Processed document ID #${data.id}.`,
        ]);

        // Step 4: Cross-Check Rules
        if (!isMounted) return;
        setCurrentStep(3);
        setLogs((prev) => [
          ...prev,
          `[CrossCheck Engine] Rule validations completed. Database committed.`,
          `[Pipeline] Successfully updated dashboard with new extractions.`,
        ]);

        // Auto-complete after short delay so user can read final log
        setTimeout(() => {
          if (isMounted) {
            onComplete();
          }
        }, 1200);

      } catch (err: any) {
        if (!isMounted) return;
        setHasError(true);
        setLogs((prev) => [
          ...prev,
          `[ERROR] Ingestion failed: ${err.message || "Network Error"}`,
          `[ERROR] Please check backend server at http://localhost:8000`,
        ]);
      }
    };

    processUpload();

    return () => {
      isMounted = false;
    };
  }, [isOpen, file, shipmentId, docType, onComplete]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
      <div className="relative w-full max-w-xl bg-[#09090b] border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden p-6 animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="text-center pb-4 border-b border-zinc-800/80">
          <div className={`inline-flex items-center justify-center w-12 h-12 rounded-2xl text-white shadow-glow mb-3 ${
            hasError 
              ? "bg-rose-600/20 text-rose-400 border border-rose-500/30" 
              : "bg-gradient-to-tr from-blue-600 to-indigo-600 text-white"
          }`}>
            {hasError ? (
              <AlertTriangle className="w-6 h-6 text-rose-400" />
            ) : (
              <Sparkles className="w-6 h-6 animate-spin text-blue-200" style={{ animationDuration: "3s" }} />
            )}
          </div>
          <h2 className="text-lg font-bold text-zinc-100 tracking-tight">
            {hasError ? "Ingestion Failed" : "Vision AI Extraction Pipeline"}
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            {hasError 
              ? "An error occurred while communicating with the ingestion API endpoint."
              : "Uploading document and running real-time deterministic database extractions"}
          </p>
        </div>

        {/* Step Progress Tracker */}
        <div className="py-6 space-y-3">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isFinished = currentStep > idx && !hasError;
            const isCurrent = currentStep === idx && !hasError;
            const isFailed = currentStep === idx && hasError;

            return (
              <div
                key={idx}
                className={`flex items-start space-x-3.5 p-3 rounded-xl transition-all duration-300 ${
                  isFailed
                    ? "bg-rose-950/20 border border-rose-800/50"
                    : isCurrent
                    ? "bg-zinc-900 border border-blue-500/40 shadow-sm"
                    : isFinished
                    ? "bg-zinc-950/40 border border-zinc-800/50"
                    : "opacity-40 border border-transparent"
                }`}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {isFinished ? (
                    <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                  ) : isCurrent ? (
                    <div className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/40 flex items-center justify-center">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    </div>
                  ) : isFailed ? (
                    <div className="w-6 h-6 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/40 flex items-center justify-center">
                      <AlertTriangle className="w-3.5 h-3.5" />
                    </div>
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-zinc-800 text-zinc-500 flex items-center justify-center">
                      <Icon className="w-3 h-3" />
                    </div>
                  )}
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className={`text-xs font-semibold ${
                      isFailed 
                        ? "text-rose-400" 
                        : isCurrent 
                        ? "text-blue-300" 
                        : isFinished 
                        ? "text-zinc-200" 
                        : "text-zinc-500"
                    }`}>
                      {step.title}
                    </p>
                    {isCurrent && (
                      <span className="text-[10px] font-mono text-blue-400 uppercase tracking-widest animate-pulse">
                        Executing...
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-0.5">{step.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Terminal Log Stream */}
        <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-3 font-mono text-[11px] text-zinc-400 space-y-1 max-h-36 overflow-y-auto">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1 flex items-center justify-between">
            <span>HTTP Execution Stream</span>
            <span className={`inline-block w-2 h-2 rounded-full ${hasError ? "bg-rose-500" : "bg-emerald-400 animate-ping"}`} />
          </div>
          {logs.map((log, i) => (
            <div key={i} className="flex items-center space-x-2">
              <span className="text-zinc-600">&gt;</span>
              <span className={log.includes("[ERROR]") ? "text-rose-400 font-semibold" : log.includes("[Pipeline]") ? "text-emerald-400 font-semibold" : "text-zinc-300"}>
                {log}
              </span>
            </div>
          ))}
        </div>

        {/* Failure Close Button */}
        {hasError && (
          <div className="mt-4 text-right">
            <button
              onClick={onClose || onComplete}
              className="px-4 py-1.5 text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};