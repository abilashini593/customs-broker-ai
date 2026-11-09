"use client";

import React, { useState } from "react";
import { 
  ShipmentDetail, 
  ExtractedField, 
  LineItem, 
  CrossCheckResult 
} from "../lib/api";
import { CrossCheckCard } from "./CrossCheckCard";
import { FieldCard } from "./FieldCard";
import { 
  ArrowLeft, 
  FileText, 
  Check, 
  Edit2, 
  AlertTriangle, 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  Download, 
  ShieldCheck, 
  Lock, 
  Unlock, 
  ChevronDown, 
  ChevronRight, 
  CheckCircle2, 
  Save, 
  Eye, 
  RotateCw,
  Hash,
  Scale,
  Box,
  Building,
  Calendar,
  Sparkles
} from "lucide-react";

interface ReviewWorkspaceProps {
  shipment: ShipmentDetail;
  onBack: () => void;
  onUpdateField: (fieldId: number, newValue: string, isConfirmed?: boolean) => Promise<void>;
  onUpdateLineItem: (itemId: number, data: Partial<LineItem>) => Promise<void>;
  onReRunChecks: () => void;
  isReRunning?: boolean;
  onOpenOverrideModal: (ruleCode: string) => void;
  onOpenExportModal: () => void;
  userRole: "Documentation Executive" | "Documentation Manager";
}

export function ReviewWorkspace({
  shipment,
  onBack,
  onUpdateField,
  onUpdateLineItem,
  onReRunChecks,
  isReRunning = false,
  onOpenOverrideModal,
  onOpenExportModal,
  userRole,
}: ReviewWorkspaceProps) {
  const [activeDocTab, setActiveDocTab] = useState<"commercial_invoice" | "packing_list" | "bill_of_lading">("commercial_invoice");
  const [zoomLevel, setZoomLevel] = useState<number>(100);
  const [editingFieldId, setEditingFieldId] = useState<number | null>(null);
  const [fieldEditValue, setFieldEditValue] = useState<string>("");

  // Accordion toggle states
  const [accordions, setAccordions] = useState({
    parties: true,
    metadata: true,
    lineItems: true,
    packages: true,
    weights: true,
  });

  const toggleAccordion = (key: keyof typeof accordions) => {
    setAccordions((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const hasBlockingFailures = (shipment.cross_checks || []).some(
    (c) => c.status === "FAILED" && c.is_blocking
  );

  const startEditField = (field: ExtractedField) => {
    setEditingFieldId(field.id);
    setFieldEditValue(field.field_value);
  };

  const saveEditField = async (fieldId: number) => {
    await onUpdateField(fieldId, fieldEditValue, true);
    setEditingFieldId(null);
  };

  const confirmField = async (fieldId: number, val: string) => {
    await onUpdateField(fieldId, val, true);
  };

  // Safe Group fields
  const fields = shipment.extracted_fields || [];
  const partiesFields = fields.filter((f) => f.field_group === "parties");
  const metadataFields = fields.filter((f) => f.field_group === "metadata");
  const weightsFields = fields.filter((f) => f.field_group === "weights");
  const packagesFields = fields.filter((f) => f.field_group === "packages");
  const lineItemsList = shipment.line_items || [];

  return (
    <div className="space-y-4">
      {/* Top Breadcrumb & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-zinc-800">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/80 transition"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-zinc-100 font-mono">
                {shipment.shipment_number}
              </h2>
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded-full border ${
                shipment.status === "Cleared" || shipment.status === "Exported"
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                  : shipment.status === "Pending Review"
                  ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                  : "bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse"
              }`}>
                {shipment.status}
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              {shipment.supplier_name} ({shipment.supplier_country}) → {shipment.consignee_name}
            </p>
          </div>
        </div>

        {/* Export / Action Buttons */}
        <div className="flex items-center space-x-3">
          {hasBlockingFailures ? (
            <div className="flex items-center space-x-2">
              <span className="text-[11px] text-rose-400 font-medium hidden md:inline">
                Cross-Check Blocker active
              </span>
              <button
                disabled
                className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold bg-zinc-800 text-zinc-500 border border-zinc-700/50 cursor-not-allowed opacity-75"
                title="Resolve or override cross-check blockers to export"
              >
                <Lock className="w-3.5 h-3.5 text-rose-400" />
                <span>Export Blocked</span>
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenExportModal}
              className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/30 border border-emerald-400/40 transition-all duration-200"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Customs Filing (EDI)</span>
            </button>
          )}
        </div>
      </div>

      {/* Screen 5: Deterministic Cross-Check Validation Box */}
      <CrossCheckCard
        checks={shipment.cross_checks || []}
        onReRunChecks={onReRunChecks}
        isReRunning={isReRunning}
        onOpenOverrideModal={onOpenOverrideModal}
        userRole={userRole}
      />

      {/* Screen 4: Split Side-by-Side Review Pane */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ========================================================= */}
        {/* LEFT PANE: Interactive Document Previewer (5 cols on lg) */}
        {/* ========================================================= */}
        <div className="lg:col-span-5 glass-panel rounded-2xl border border-zinc-800/90 overflow-hidden shadow-card sticky top-20">
          {/* Document Switcher Tabs */}
          <div className="flex items-center justify-between px-3 py-2 border-b border-zinc-800 bg-zinc-900/80">
            <div className="flex items-center space-x-1">
              <button
                onClick={() => setActiveDocTab("commercial_invoice")}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition ${
                  activeDocTab === "commercial_invoice"
                    ? "bg-zinc-800 text-blue-400 font-semibold border border-zinc-700/60"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Commercial Invoice
              </button>
              <button
                onClick={() => setActiveDocTab("packing_list")}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition ${
                  activeDocTab === "packing_list"
                    ? "bg-zinc-800 text-blue-400 font-semibold border border-zinc-700/60"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Packing List
              </button>
              <button
                onClick={() => setActiveDocTab("bill_of_lading")}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition ${
                  activeDocTab === "bill_of_lading"
                    ? "bg-zinc-800 text-blue-400 font-semibold border border-zinc-700/60"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                Bill of Lading
              </button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center space-x-1 text-zinc-400">
              <button
                onClick={() => setZoomLevel((z) => Math.max(70, z - 10))}
                className="p-1 hover:text-zinc-200 hover:bg-zinc-800 rounded"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span className="text-[10px] font-mono px-1">{zoomLevel}%</span>
              <button
                onClick={() => setZoomLevel((z) => Math.min(150, z + 10))}
                className="p-1 hover:text-zinc-200 hover:bg-zinc-800 rounded"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel(100)}
                className="p-1 hover:text-zinc-200 hover:bg-zinc-800 rounded"
                title="Reset Zoom"
              >
                <RotateCw className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Document Canvas / Scanned View Simulation */}
          <div className="p-4 bg-zinc-950/70 overflow-auto max-h-[750px] flex justify-center">
            <div
              style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center" }}
              className="w-full max-w-[480px] bg-[#0d0e12] border border-zinc-700/70 rounded-xl p-5 shadow-2xl relative text-[11px] font-mono text-zinc-300 transition-transform duration-150 select-none"
            >
              {/* Document Header Watermark */}
              <div className="flex justify-between items-start border-b border-zinc-700/80 pb-3 mb-3">
                <div>
                  <div className="font-bold text-sm tracking-wider uppercase text-zinc-100">
                    {activeDocTab === "commercial_invoice" && "COMMERCIAL INVOICE"}
                    {activeDocTab === "packing_list" && "EXPORT PACKING LIST"}
                    {activeDocTab === "bill_of_lading" && "OCEAN BILL OF LADING"}
                  </div>
                  <div className="text-[10px] text-zinc-500 font-sans">
                    ORIGINAL FOR CUSTOMS CLEARANCE / EDI COMPLIANT
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[10px] text-zinc-400">DOCKET REF</div>
                  <div className="font-bold text-xs text-blue-400">{shipment.shipment_number}</div>
                </div>
              </div>

              {/* Document Meta Row */}
              <div className="grid grid-cols-2 gap-3 pb-3 border-b border-zinc-800/80 text-[10px]">
                <div className="space-y-1">
                  <span className="text-zinc-500 block uppercase">Shipper / Exporter:</span>
                  <span className="font-medium text-zinc-200 block leading-tight">
                    {shipment.supplier_name}
                  </span>
                  <span className="text-zinc-400 block">{shipment.supplier_country}</span>
                </div>
                <div className="space-y-1">
                  <span className="text-zinc-500 block uppercase">Consignee:</span>
                  <span className="font-medium text-zinc-200 block leading-tight">
                    {shipment.consignee_name}
                  </span>
                  <span className="text-zinc-400 block">{shipment.consignee_country}</span>
                </div>
              </div>

              {/* Logistics & Route */}
              <div className="grid grid-cols-2 gap-3 py-2.5 border-b border-zinc-800/80 text-[10px]">
                <div>
                  <span className="text-zinc-500 block">PORT OF LOADING:</span>
                  <span className="text-zinc-200 font-medium">{shipment.port_of_loading}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block">PORT OF DISCHARGE:</span>
                  <span className="text-zinc-200 font-medium">{shipment.port_of_discharge}</span>
                </div>
              </div>

              {/* Document Body depending on Doc Type */}
              {activeDocTab === "commercial_invoice" && (
                <div className="py-3 space-y-3">
                  <div className="text-[10px] font-bold text-zinc-400 uppercase">Item Valuation Manifest</div>
                  <div className="border border-zinc-800 rounded-lg overflow-hidden">
                    <table className="w-full text-left text-[10px]">
                      <thead className="bg-zinc-900 border-b border-zinc-800 text-zinc-400">
                        <tr>
                          <th className="p-1.5">Item</th>
                          <th className="p-1.5">HSN Code</th>
                          <th className="p-1.5 text-right">Qty</th>
                          <th className="p-1.5 text-right">Total</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-zinc-800/60">
                        {lineItemsList.map((item) => (
                          <tr
                            key={item.id}
                            className={item.confidence_score < 85 ? "bg-amber-500/10 text-amber-300" : ""}
                          >
                            <td className="p-1.5 truncate max-w-[120px]">{item.description}</td>
                            <td className="p-1.5 font-bold">{item.hsn_code}</td>
                            <td className="p-1.5 text-right font-mono">{item.quantity}</td>
                            <td className="p-1.5 text-right font-mono font-bold">${item.total_amount?.toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Highlighting Bounding Box on Invoice Total */}
                  <div className="p-2.5 rounded-lg bg-zinc-900/90 border border-blue-500/40 relative">
                    <div className="flex justify-between items-center">
                      <span className="text-zinc-400 text-[10px]">INVOICE GRAND TOTAL:</span>
                      <span className="text-xs font-bold text-emerald-400 font-mono">
                        ${shipment.total_declared_value?.toLocaleString(undefined, { minimumFractionDigits: 2 })} USD
                      </span>
                    </div>
                    <div className="absolute -top-2 right-2 text-[8px] bg-blue-500 text-white px-1 rounded uppercase tracking-wider font-sans">
                      OCR Conf 99.0%
                    </div>
                  </div>

                  {/* Invoice Gross Weight Box */}
                  <div className="p-2 rounded-lg bg-zinc-900/60 border border-zinc-800 flex justify-between">
                    <span className="text-zinc-400 text-[10px]">DECLARED GROSS WT:</span>
                    <span className="font-bold text-zinc-200">12,450.00 KGS</span>
                  </div>
                </div>
              )}

              {activeDocTab === "packing_list" && (
                <div className="py-3 space-y-3">
                  <div className="text-[10px] font-bold text-zinc-400 uppercase">Package & Tare Manifest</div>
                  <div className="p-2.5 rounded-lg bg-zinc-900/90 border border-zinc-800 space-y-1.5 text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-zinc-400">TOTAL PACKAGES:</span>
                      <span className="font-bold text-zinc-200">42 Pallets / 840 Cartons</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-400">CONTAINER NO:</span>
                      <span className="font-bold text-blue-400">MSKU9281745</span>
                    </div>
                    <div className="flex justify-between items-center p-1 rounded bg-amber-500/10 border border-amber-500/30">
                      <span className="text-amber-400">CARRIER SEAL NO:</span>
                      <span className="font-bold text-amber-300">SL-839201 (79.4% Conf)</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-400">GROSS WEIGHT:</span>
                      <span className="font-bold text-zinc-200">12,450.00 KGS</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-400">NET WEIGHT:</span>
                      <span className="font-bold text-zinc-200">11,200.00 KGS</span>
                    </div>
                  </div>
                </div>
              )}

              {activeDocTab === "bill_of_lading" && (
                <div className="py-3 space-y-3">
                  <div className="text-[10px] font-bold text-zinc-400 uppercase">Carrier Freight & Port Manifest</div>
                  <div className="p-2.5 rounded-lg bg-zinc-900/90 border border-zinc-800 space-y-2 text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-zinc-400">B/L NUMBER:</span>
                      <span className="font-bold text-blue-400">MAEU92837190</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-400">VESSEL / VOYAGE:</span>
                      <span className="font-bold text-zinc-200">EVER GIVEN / 0428-091W</span>
                    </div>
                    
                    {/* CRITICAL WEIGHT MISMATCH HIGHLIGHT CALLOUT ON DOCUMENT */}
                    <div className="p-2.5 rounded-lg bg-rose-500/10 border-2 border-rose-500/60 relative animate-pulse-rose">
                      <div className="flex justify-between items-center">
                        <span className="text-rose-400 font-bold">CARRIER GROSS WEIGHT:</span>
                        <span className="text-xs font-bold text-rose-300 font-mono">12,800.00 KGS</span>
                      </div>
                      <div className="absolute -top-2.5 right-2 text-[9px] bg-rose-600 text-white font-bold px-1.5 py-0.2 rounded font-sans uppercase">
                        +350 kg Discrepancy
                      </div>
                      <div className="text-[9px] text-rose-300/80 mt-1">
                        Carrier scale certificate differs from Invoice (12,450 kg).
                      </div>
                    </div>

                    <div className="flex justify-between">
                      <span className="text-zinc-400">CONTAINER / SEAL:</span>
                      <span className="font-bold text-zinc-200">MSKU9281745 / SL-839201</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Carrier Digital Seal Simulation */}
              <div className="mt-4 pt-3 border-t border-zinc-800 flex items-center justify-between text-[9px] text-zinc-500">
                <div className="flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                  <span>OCR Signature Verified</span>
                </div>
                <div className="font-mono">PAGE 1 OF 2</div>
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================= */}
        {/* RIGHT PANE: Structured Extracted Fields Accordions (7 cols) */}
        {/* ========================================================= */}
        <div className="lg:col-span-7 space-y-4">
          
          {/* 1. Line Items Schedule */}
          <div className="glass-panel rounded-2xl border border-zinc-800/90 overflow-hidden shadow-card">
            <button
              onClick={() => toggleAccordion("lineItems")}
              className="w-full px-5 py-3.5 bg-zinc-900/60 flex items-center justify-between text-left hover:bg-zinc-900/90 transition"
            >
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-blue-400" />
                <span className="text-xs font-bold text-zinc-200">
                  Line Items & Tariff Classification ({lineItemsList.length})
                </span>
                {lineItemsList.some((i) => i.confidence_score < 85 && !i.is_confirmed) && (
                  <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
                    Low Confidence Flag
                  </span>
                )}
              </div>
              {accordions.lineItems ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
            </button>

            {accordions.lineItems && (
              <div className="p-3">
                <table className="w-full text-left text-xs border-collapse table-auto">
                  <thead>
                    <tr className="border-b border-zinc-800 text-[10px] font-mono uppercase text-zinc-400">
                      <th className="py-2 px-1 w-6">#</th>
                      <th className="py-2 px-1.5">Description</th>
                      <th className="py-2 px-1.5">HSN / HTS</th>
                      <th className="py-2 px-1.5 text-right">Qty</th>
                      <th className="py-2 px-1.5 text-right">Price</th>
                      <th className="py-2 px-1.5 text-right">Total</th>
                      <th className="py-2 px-1.5 text-center">Conf</th>
                      <th className="py-2 px-1.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/60">
                    {lineItemsList.map((item) => {
                      const isLowConf = item.confidence_score < 85 && !item.is_confirmed;

                      return (
                        <tr
                          key={item.id}
                          className={`transition-colors ${
                            isLowConf
                              ? "bg-amber-950/20 border-l-2 border-amber-500"
                              : "hover:bg-zinc-900/40"
                          }`}
                        >
                          <td className="py-2.5 px-1 font-mono text-zinc-400">{item.item_number}</td>
                          <td className="py-2.5 px-1.5 max-w-[130px] truncate text-zinc-200 font-medium" title={item.description}>
                            {item.description}
                          </td>
                          <td className="py-2.5 px-1.5 font-mono font-bold text-zinc-200">
                            {item.hsn_code}
                          </td>
                          <td className="py-2.5 px-1.5 text-right font-mono text-zinc-300">
                            {item.quantity?.toLocaleString()}
                          </td>
                          <td className="py-2.5 px-1.5 text-right font-mono text-zinc-300">
                            ${item.unit_price?.toFixed(2)}
                          </td>
                          <td className="py-2.5 px-1.5 text-right font-mono font-bold text-zinc-100">
                            ${item.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </td>
                          <td className="py-2.5 px-1.5 text-center">
                            {isLowConf ? (
                              <span className="inline-flex items-center space-x-0.5 px-1 py-0.5 rounded text-[9px] font-mono bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
                                <AlertTriangle className="w-2.5 h-2.5" />
                                <span>{item.confidence_score?.toFixed(0)}%</span>
                              </span>
                            ) : (
                              <span className="inline-flex items-center space-x-0.5 px-1 py-0.5 rounded text-[9px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                <Check className="w-2.5 h-2.5" />
                                <span>{item.confidence_score?.toFixed(0)}%</span>
                              </span>
                            )}
                          </td>
                          <td className="py-2.5 px-1.5 text-right">
                            {isLowConf ? (
                              <button
                                onClick={() => onUpdateLineItem(item.id, { is_confirmed: true })}
                                className="px-2 py-1 rounded text-[10px] font-semibold bg-amber-500 hover:bg-amber-400 text-black shadow-sm transition"
                                title="1-Click Confirm OCR Extraction"
                              >
                                Confirm
                              </button>
                            ) : (
                              <span className="text-[10px] text-zinc-500 font-mono">Verified</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* 2. Parties & Consignment Entities */}
          <div className="glass-panel rounded-2xl border border-zinc-800/90 overflow-hidden shadow-card">
            <button
              onClick={() => toggleAccordion("parties")}
              className="w-full px-5 py-3.5 bg-zinc-900/60 flex items-center justify-between text-left hover:bg-zinc-900/90 transition"
            >
              <div className="flex items-center space-x-2">
                <Building className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-bold text-zinc-200">
                  Parties & Consignment Entities ({partiesFields.length})
                </span>
              </div>
              {accordions.parties ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
            </button>

            {accordions.parties && (
              <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {partiesFields.map((field) => (
                  <FieldCard
                    key={field.id}
                    field={field}
                    isEditing={editingFieldId === field.id}
                    editValue={fieldEditValue}
                    setEditValue={setFieldEditValue}
                    onStartEdit={() => startEditField(field)}
                    onSave={() => saveEditField(field.id)}
                    onConfirm={() => confirmField(field.id, field.field_value)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* 3. Weights & Cargo Measurements */}
          <div className="glass-panel rounded-2xl border border-zinc-800/90 overflow-hidden shadow-card">
            <button
              onClick={() => toggleAccordion("weights")}
              className="w-full px-5 py-3.5 bg-zinc-900/60 flex items-center justify-between text-left hover:bg-zinc-900/90 transition"
            >
              <div className="flex items-center space-x-2">
                <Scale className="w-4 h-4 text-rose-400" />
                <span className="text-xs font-bold text-zinc-200">
                  Weights & Cargo Measurements ({weightsFields.length})
                </span>
                <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  Cross-Check Focus
                </span>
              </div>
              {accordions.weights ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
            </button>

            {accordions.weights && (
              <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {weightsFields.map((field) => (
                  <FieldCard
                    key={field.id}
                    field={field}
                    isEditing={editingFieldId === field.id}
                    editValue={fieldEditValue}
                    setEditValue={setFieldEditValue}
                    onStartEdit={() => startEditField(field)}
                    onSave={() => saveEditField(field.id)}
                    onConfirm={() => confirmField(field.id, field.field_value)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* 4. Packages, Containers & Carrier Seals */}
          <div className="glass-panel rounded-2xl border border-zinc-800/90 overflow-hidden shadow-card">
            <button
              onClick={() => toggleAccordion("packages")}
              className="w-full px-5 py-3.5 bg-zinc-900/60 flex items-center justify-between text-left hover:bg-zinc-900/90 transition"
            >
              <div className="flex items-center space-x-2">
                <Box className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-bold text-zinc-200">
                  Packages, Containers & Carrier Seals ({packagesFields.length})
                </span>
              </div>
              {accordions.packages ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
            </button>

            {accordions.packages && (
              <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {packagesFields.map((field) => (
                  <FieldCard
                    key={field.id}
                    field={field}
                    isEditing={editingFieldId === field.id}
                    editValue={fieldEditValue}
                    setEditValue={setFieldEditValue}
                    onStartEdit={() => startEditField(field)}
                    onSave={() => saveEditField(field.id)}
                    onConfirm={() => confirmField(field.id, field.field_value)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* 5. Metadata, Invoices & Transport Numbers */}
          <div className="glass-panel rounded-2xl border border-zinc-800/90 overflow-hidden shadow-card">
            <button
              onClick={() => toggleAccordion("metadata")}
              className="w-full px-5 py-3.5 bg-zinc-900/60 flex items-center justify-between text-left hover:bg-zinc-900/90 transition"
            >
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-zinc-400" />
                <span className="text-xs font-bold text-zinc-200">
                  Metadata, Invoices & Transport Numbers ({metadataFields.length})
                </span>
              </div>
              {accordions.metadata ? <ChevronDown className="w-4 h-4 text-zinc-500" /> : <ChevronRight className="w-4 h-4 text-zinc-500" />}
            </button>

            {accordions.metadata && (
              <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                {metadataFields.map((field) => (
                  <FieldCard
                    key={field.id}
                    field={field}
                    isEditing={editingFieldId === field.id}
                    editValue={fieldEditValue}
                    setEditValue={setFieldEditValue}
                    onStartEdit={() => startEditField(field)}
                    onSave={() => saveEditField(field.id)}
                    onConfirm={() => confirmField(field.id, field.field_value)}
                  />
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}