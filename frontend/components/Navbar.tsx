"use client";

import React from "react";
import { 
  ShieldCheck, 
  UserCheck, 
  FileText, 
  History, 
  Sparkles, 
  SlidersHorizontal 
} from "lucide-react";

interface NavbarProps {
  currentRole: "Documentation Executive" | "Documentation Manager";
  setCurrentRole: (role: "Documentation Executive" | "Documentation Manager") => void;
  onOpenAuditTrail?: () => void;
  onNewUpload?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRole,
  setCurrentRole,
  onOpenAuditTrail,
  onNewUpload
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-zinc-800/80 bg-[#09090b]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Identity */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-emerald-400 p-[1px] shadow-glow flex items-center justify-center">
            <div className="w-full h-full bg-zinc-950 rounded-[11px] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-zinc-100 tracking-tight text-base">
                ClearBorder<span className="text-emerald-400 font-mono font-medium text-xs ml-1 px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">AI</span>
              </span>
              <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800">
                Customs v4.2
              </span>
            </div>
            <p className="text-[11px] text-zinc-400">Automated Customs Broker Document Extraction & Cross-Check</p>
          </div>
        </div>

        {/* Center / Role Switcher (Screen 6 Role Switch Directive) */}
        <div className="flex items-center bg-zinc-900/90 p-1 rounded-xl border border-zinc-800 shadow-inner">
          <button
            type="button"
            onClick={() => setCurrentRole("Documentation Executive")}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
              currentRole === "Documentation Executive"
                ? "bg-blue-600 text-white shadow-sm border border-blue-500 font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <UserCheck className="w-3.5 h-3.5 text-blue-200" />
            <span>Doc Executive</span>
            <span className="text-[10px] text-blue-100 bg-blue-700/60 px-1.5 py-0.2 rounded font-mono">Review/Edit</span>
          </button>

          <button
            type="button"
            onClick={() => setCurrentRole("Documentation Manager")}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
              currentRole === "Documentation Manager"
                ? "bg-blue-600 text-white shadow-sm border border-blue-500 font-semibold"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-blue-200" />
            <span>Doc Manager</span>
            <span className="text-[10px] text-blue-100 bg-blue-700/60 px-1.5 py-0.2 rounded font-mono">Sign-Off/Override</span>
          </button>
        </div>

        {/* Right Actions & Status */}
        <div className="flex items-center space-x-3">
          {onOpenAuditTrail && (
            <button
              onClick={onOpenAuditTrail}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60 border border-zinc-800/80 transition-all duration-200"
              title="Audit Logs"
            >
              <History className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Audit Logs</span>
            </button>
          )}

          {onNewUpload && (
            <button
              onClick={onNewUpload}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/30 transition-all duration-200 shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Ingest Documents</span>
            </button>
          )}

          <div className="flex items-center space-x-2 pl-2 border-l border-zinc-800">
            <div className="w-7 h-7 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-xs font-mono font-medium text-zinc-300">
              {currentRole === "Documentation Manager" ? "SC" : "JD"}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};