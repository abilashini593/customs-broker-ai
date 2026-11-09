"use client";

import React from "react";
import { ExtractedField } from "../lib/api";
import { Check, Edit2, Save, AlertTriangle } from "lucide-react";

interface FieldCardProps {
  field: ExtractedField;
  isEditing: boolean;
  editValue: string;
  setEditValue: (val: string) => void;
  onStartEdit: () => void;
  onSave: () => void;
  onConfirm: () => void;
}

export const FieldCard: React.FC<FieldCardProps> = ({
  field,
  isEditing,
  editValue,
  setEditValue,
  onStartEdit,
  onSave,
  onConfirm,
}) => {
  const isLowConf = field.confidence_score < 85 && !field.is_confirmed;
  const label = field.field_label || (field as any).field_name || field.field_key;

  return (
    <div
      className={`p-3 rounded-xl border transition-all duration-200 ${
        isLowConf
          ? "bg-amber-950/20 border-amber-800/60 shadow-sm"
          : "bg-zinc-900/40 border-zinc-800/80 hover:border-zinc-700/80"
      }`}
    >
      {/* Top Row: Field Label on Left, Confidence Badge on Right */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs text-zinc-400 font-medium truncate pr-2" title={label}>
          {label}
        </span>
        <div className="flex-shrink-0">
          {isLowConf ? (
            <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-amber-500/15 text-amber-400 border border-amber-500/30 animate-pulse">
              <AlertTriangle className="w-2.5 h-2.5" />
              <span>{field.confidence_score.toFixed(1)}% Conf</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Check className="w-2.5 h-2.5" />
              <span>{field.confidence_score.toFixed(1)}%</span>
            </span>
          )}
        </div>
      </div>

      {/* Bottom Row: Field Value on Left, Actions (Edit / Confirm) on Right */}
      {isEditing ? (
        <div className="flex items-center space-x-2 mt-1">
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="w-full bg-zinc-950 border border-blue-500/80 rounded px-2.5 py-1 text-xs text-zinc-100 font-mono focus:outline-none focus:ring-1 focus:ring-blue-500"
            autoFocus
          />
          <button
            onClick={onSave}
            className="p-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded transition shadow-sm"
            title="Save changes"
          >
            <Save className="w-3.5 h-3.5" />
          </button>
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <span
            className={`text-xs font-mono font-medium truncate max-w-[220px] ${
              field.field_key.includes("weight") && field.field_value === "12800.00"
                ? "text-rose-400 font-bold"
                : isLowConf
                ? "text-amber-200"
                : "text-zinc-100"
            }`}
            title={field.field_value}
          >
            {field.field_value || <span className="text-zinc-600 italic">Empty</span>}
          </span>

          <div className="flex items-center space-x-1.5 flex-shrink-0">
            {isLowConf && (
              <button
                onClick={onConfirm}
                className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500 hover:bg-amber-400 text-black shadow-sm transition"
                title="1-Click Accept OCR Value"
              >
                Confirm
              </button>
            )}
            <button
              onClick={onStartEdit}
              className="p-1 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 rounded transition"
              title="Edit value manually"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
