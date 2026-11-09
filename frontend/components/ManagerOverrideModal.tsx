"use client";

import React, { useState } from "react";
import { 
  X, 
  ShieldAlert, 
  Unlock, 
  AlertCircle, 
  CheckCircle2,
  FileCheck
} from "lucide-react";

interface ManagerOverrideModalProps {
  isOpen: boolean;
  onClose: () => void;
  ruleCode: string;
  onConfirmOverride: (ruleCode: string, reason: string) => Promise<void>;
}

export const ManagerOverrideModal: React.FC<ManagerOverrideModalProps> = ({
  isOpen,
  onClose,
  ruleCode,
  onConfirmOverride,
}) => {
  const [reason, setReason] = useState(
    "Tare weight of 4 heavy-duty steel pallets (350 kg) included in carrier scale certificate; verified against factory tare manifest."
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reason || reason.trim().length < 10) {
      setError("Please provide a thorough audit justification (minimum 10 characters) for customs compliance.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onConfirmOverride(ruleCode, reason);
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to process override.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-lg bg-[#09090b] border border-zinc-800 rounded-2xl shadow-glass overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-rose-950/20">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-zinc-100">
                Documentation Manager Override
              </h3>
              <p className="text-xs text-zinc-400">
                Authorized override for {ruleCode}
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

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800 text-xs text-zinc-300 leading-relaxed">
            <p className="font-semibold text-rose-400 mb-1 flex items-center space-x-1.5">
              <AlertCircle className="w-4 h-4 text-rose-400" />
              <span>Customs Audit Notice</span>
            </p>
            This action will formally unlock the customs filing export by signing off on the mathematical or manifest discrepancy under your credentials. An immutable audit record will be logged with your timestamp.
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
              Mandatory Justification / Resolution Explanation
            </label>
            <textarea
              rows={4}
              value={reason}
              onChange={(e) => {
                setReason(e.target.value);
                if (error) setError(null);
              }}
              className="w-full bg-zinc-950 border border-zinc-800 focus:border-rose-500 rounded-xl p-3 text-xs text-zinc-200 focus:outline-none focus:ring-1 focus:ring-rose-500/30 font-sans"
              placeholder="Detail why this discrepancy is allowable under customs regulations (e.g. tare weight, commercial amendment)..."
            />
          </div>

          {error && (
            <p className="text-xs text-rose-400 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
              {error}
            </p>
          )}

          <div className="flex items-center justify-between pt-3 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-900/30 transition disabled:opacity-50"
            >
              <Unlock className="w-3.5 h-3.5" />
              <span>{isSubmitting ? "Authorizing..." : "Authorize & Sign Off"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
