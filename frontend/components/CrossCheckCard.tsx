"use client";

import React from "react";
import { 
  CrossCheckResult 
} from "../lib/api";
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  ShieldAlert, 
  ShieldCheck, 
  RefreshCw, 
  ExternalLink,
  Lock,
  Unlock,
  SlidersHorizontal
} from "lucide-react";

interface CrossCheckCardProps {
  checks: CrossCheckResult[];
  onReRunChecks: () => void;
  onOpenOverrideModal: (ruleCode: string) => void;
  userRole: "Documentation Executive" | "Documentation Manager";
  isReRunning?: boolean;
}

export const CrossCheckCard: React.FC<CrossCheckCardProps> = ({
  checks,
  onReRunChecks,
  onOpenOverrideModal,
  userRole,
  isReRunning = false,
}) => {
  const hasBlockers = checks.some((c) => c.status === "FAILED" && c.is_blocking);
  const failedCount = checks.filter((c) => c.status === "FAILED").length;
  const passedCount = checks.filter((c) => c.status === "PASSED").length;
  const overriddenCount = checks.filter((c) => c.status === "OVERRIDDEN").length;

  return (
    <div className="glass-panel rounded-2xl border border-zinc-800/90 overflow-hidden shadow-card">
      {/* Header Banner */}
      <div className={`px-5 py-4 border-b flex items-center justify-between transition-colors ${
        hasBlockers 
          ? "bg-rose-950/20 border-rose-900/40" 
          : "bg-emerald-950/20 border-emerald-900/40"
      }`}>
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-xl flex items-center justify-center ${
            hasBlockers 
              ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" 
              : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
          }`}>
            {hasBlockers ? <ShieldAlert className="w-5 h-5 text-rose-400" /> : <ShieldCheck className="w-5 h-5 text-emerald-400" />}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-zinc-100">
                Deterministic Cross-Check Engine
              </h3>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
                hasBlockers 
                  ? "bg-rose-500/20 text-rose-300 border border-rose-500/30 animate-pulse" 
                  : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              }`}>
                {hasBlockers ? "EXPORT BLOCKED" : "CLEARED FOR FILING"}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              {hasBlockers 
                ? `${failedCount} mathematical/manifest discrepancy detected. Export locked.`
                : "All customs reconciliation rules verified against commercial manifests."}
            </p>
          </div>
        </div>

        <button
          onClick={onReRunChecks}
          disabled={isReRunning}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-300 bg-zinc-800/80 hover:bg-zinc-700/80 border border-zinc-700/80 transition shadow-sm disabled:opacity-50"
          title="Re-run deterministic rules"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isReRunning ? "animate-spin text-blue-400" : ""}`} />
          <span>Re-validate</span>
        </button>
      </div>

      {/* Rules Evaluation List */}
      <div className="p-4 space-y-3">
        {checks.map((rule) => {
          const isFailed = rule.status === "FAILED";
          const isOverridden = rule.status === "OVERRIDDEN";
          const isPassed = rule.status === "PASSED";

          return (
            <div
              key={rule.rule_code}
              className={`p-3.5 rounded-xl border transition-all duration-200 ${
                isFailed
                  ? "bg-rose-950/15 border-rose-800/40 text-rose-200 shadow-sm"
                  : isOverridden
                  ? "bg-amber-950/15 border-amber-800/40 text-amber-200"
                  : "bg-zinc-900/40 border-zinc-800/60 hover:border-zinc-700/60"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start space-x-3">
                  <div className="mt-0.5 flex-shrink-0">
                    {isFailed ? (
                      <XCircle className="w-4 h-4 text-rose-400" />
                    ) : isOverridden ? (
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-zinc-200">
                        {rule.rule_name}
                      </span>
                      <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded border ${
                        isFailed 
                          ? "bg-rose-500/10 text-rose-400 border-rose-500/20" 
                          : isOverridden 
                          ? "bg-amber-500/10 text-amber-400 border-amber-500/20" 
                          : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      }`}>
                        {rule.status}
                      </span>
                    </div>

                    <p className={`text-xs mt-1 leading-relaxed ${isFailed ? "text-rose-300 font-medium" : "text-zinc-400"}`}>
                      {rule.message}
                    </p>

                    {/* Numerical breakdown details if failed */}
                    {isFailed && rule.discrepancy_details && (
                      <div className="mt-2 p-2.5 rounded-lg bg-zinc-950/80 border border-rose-900/40 font-mono text-[11px] space-y-1">
                        {rule.discrepancy_details.difference !== undefined && (
                          <div className="flex justify-between text-zinc-300">
                            <span>Variance Amount:</span>
                            <span className="text-rose-400 font-bold">
                              ${Math.abs(rule.discrepancy_details.difference).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </span>
                          </div>
                        )}
                        {rule.discrepancy_details.absolute_diff_kg !== undefined && (
                          <div className="flex justify-between text-zinc-300">
                            <span>Weight Variance:</span>
                            <span className="text-rose-400 font-bold">
                              +{rule.discrepancy_details.absolute_diff_kg} kg (+{rule.discrepancy_details.percentage_diff}%)
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Override notes if already overridden */}
                    {isOverridden && (
                      <div className="mt-2 p-2 rounded-lg bg-amber-950/30 border border-amber-800/40 text-[11px] text-amber-300">
                        <span className="font-semibold">Manager Override:</span> {rule.override_reason}
                        <div className="text-[10px] text-amber-400/80 font-mono mt-0.5">
                          Authorized by: {rule.overridden_by}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Manager Override Action Button */}
                {isFailed && (
                  <div className="flex-shrink-0">
                    {userRole === "Documentation Manager" ? (
                      <button
                        onClick={() => onOpenOverrideModal(rule.rule_code)}
                        className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white shadow-sm border border-rose-500/40 transition"
                      >
                        <Unlock className="w-3.5 h-3.5" />
                        <span>Override Blocker</span>
                      </button>
                    ) : (
                      <div className="flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[11px] font-medium bg-zinc-900 text-zinc-500 border border-zinc-800" title="Requires Documentation Manager role">
                        <Lock className="w-3 h-3 text-zinc-500" />
                        <span>Manager Sign-Off Req</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
