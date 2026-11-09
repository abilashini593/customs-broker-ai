"use client";

import React from "react";
import { X, History, User, Bot, Clock, ShieldCheck, ArrowRight } from "lucide-react";
import { AuditLog } from "../lib/api";

interface AuditTrailModalProps {
  isOpen: boolean;
  onClose: () => void;
  logs: AuditLog[];
  shipmentNumber?: string;
}

export const AuditTrailModal: React.FC<AuditTrailModalProps> = ({
  isOpen,
  onClose,
  logs,
  shipmentNumber,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="relative w-full max-w-2xl bg-[#09090b] border border-zinc-800 rounded-2xl shadow-glass overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-900/50">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <History className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-zinc-100">
                Compliance & Verification Audit Trail
              </h3>
              <p className="text-xs text-zinc-400">
                {shipmentNumber ? `Immutable ledger for ${shipmentNumber}` : "All system events & reviews"}
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

        <div className="p-6 max-h-[500px] overflow-y-auto space-y-4">
          {logs.length === 0 ? (
            <div className="text-center py-12 text-zinc-500 text-xs">
              No audit records recorded yet.
            </div>
          ) : (
            logs.map((log) => {
              const isSystem = log.user_role.includes("System") || log.user_role.includes("Vision");
              const isManager = log.user_role.includes("Manager");

              return (
                <div
                  key={log.id}
                  className="flex items-start space-x-3.5 p-3 rounded-xl bg-zinc-900/40 border border-zinc-800/80"
                >
                  <div className="mt-0.5 flex-shrink-0">
                    {isSystem ? (
                      <div className="w-7 h-7 rounded-lg bg-zinc-800 text-blue-400 flex items-center justify-center border border-zinc-700">
                        <Bot className="w-4 h-4" />
                      </div>
                    ) : isManager ? (
                      <div className="w-7 h-7 rounded-lg bg-indigo-950/80 text-indigo-400 flex items-center justify-center border border-indigo-800">
                        <ShieldCheck className="w-4 h-4" />
                      </div>
                    ) : (
                      <div className="w-7 h-7 rounded-lg bg-zinc-800 text-zinc-300 flex items-center justify-center border border-zinc-700">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                  </div>

                  <div className="flex-1 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-zinc-200">{log.user_name}</span>
                        <span className="text-[10px] font-mono text-zinc-400 px-1.5 py-0.2 rounded bg-zinc-800 border border-zinc-700">
                          {log.user_role}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-zinc-500 flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                      </span>
                    </div>

                    <div className="font-mono text-[11px] text-blue-400 font-medium mb-0.5">
                      {log.action}
                    </div>
                    <p className="text-zinc-400 text-xs leading-relaxed">{log.details}</p>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="px-6 py-3 border-t border-zinc-800 bg-zinc-950/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-800 hover:bg-zinc-700 transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
