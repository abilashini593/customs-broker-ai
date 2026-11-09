"use client";

import React, { useState } from "react";
import { 
  ShipmentListItem 
} from "../lib/api";
import { 
  Search, 
  Filter, 
  ArrowRight, 
  FileCheck2, 
  AlertTriangle, 
  XCircle, 
  CheckCircle2, 
  Box, 
  Ship, 
  Calendar,
  Layers,
  Sparkles,
  ArrowUpRight
} from "lucide-react";

interface ShipmentDashboardProps {
  shipments: ShipmentListItem[];
  isLoading: boolean;
  selectedStatus: string;
  setSelectedStatus: (status: string) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  onSelectShipment: (id: number) => void;
  onOpenUploadModal: () => void;
}

export const ShipmentDashboard: React.FC<ShipmentDashboardProps> = ({
  shipments,
  isLoading,
  selectedStatus,
  setSelectedStatus,
  searchQuery,
  setSearchQuery,
  onSelectShipment,
  onOpenUploadModal,
}) => {
  // KPI computations
  const totalShipments = shipments.length;
  const failedCrossChecks = shipments.filter((s) => s.status === "Cross-Check Failed").length;
  const pendingReview = shipments.filter((s) => s.status === "Pending Review").length;
  const clearedCount = shipments.filter((s) => s.status === "Cleared" || s.status === "Exported").length;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "Cleared":
      case "Exported":
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{status === "Exported" ? "Filing Exported" : "Cleared"}</span>
          </span>
        );
      case "Pending Review":
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>Pending Review</span>
          </span>
        );
      case "Cross-Check Failed":
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20 animate-pulse">
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>Cross-Check Failed</span>
          </span>
        );
    }
  };

  const statusFilters = ["All", "Cross-Check Failed", "Pending Review", "Cleared"];

  return (
    <div className="space-y-6">
      {/* Top Banner & Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-800/80">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-zinc-100 flex items-center space-x-2">
            <span>Shipment Clearance Manifests</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 font-mono">
              Live Customs Docket
            </span>
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Automated multi-document OCR ingestion, line-item reconciliation, and deterministic weight cross-checks.
          </p>
        </div>

        <button
          onClick={onOpenUploadModal}
          className="inline-flex items-center justify-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-900/20 border border-blue-500/30 transition-all duration-200"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-200" />
          <span>Upload New Docket</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Shipments */}
        <div className="glass-panel p-4 rounded-xl border border-zinc-800/80 hover:border-zinc-700/80 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">Total Ingested Shipments</span>
            <span className="p-1.5 rounded-lg bg-zinc-800/60 text-zinc-400">
              <Box className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-bold tracking-tight text-zinc-100 font-mono">{totalShipments}</span>
            <span className="text-[11px] text-zinc-500 font-normal">Active Declarations</span>
          </div>
        </div>

        {/* Failed Cross-Checks */}
        <div className="glass-panel p-4 rounded-xl border border-rose-900/30 bg-rose-950/10 hover:border-rose-700/50 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-rose-300">Cross-Check Blockers</span>
            <span className="p-1.5 rounded-lg bg-rose-500/10 text-rose-400">
              <XCircle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-bold tracking-tight text-rose-400 font-mono">{failedCrossChecks}</span>
            <span className="text-[11px] text-rose-400/70 font-medium">Require Resolution</span>
          </div>
        </div>

        {/* Pending Review */}
        <div className="glass-panel p-4 rounded-xl border border-amber-900/30 bg-amber-950/10 hover:border-amber-700/50 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-amber-300">Low-Confidence Flags</span>
            <span className="p-1.5 rounded-lg bg-amber-500/10 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-bold tracking-tight text-amber-400 font-mono">{pendingReview}</span>
            <span className="text-[11px] text-amber-400/70 font-medium">Fields &lt; 85% Conf</span>
          </div>
        </div>

        {/* Cleared for Filing */}
        <div className="glass-panel p-4 rounded-xl border border-emerald-900/30 bg-emerald-950/10 hover:border-emerald-700/50 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-emerald-300">Cleared for Customs</span>
            <span className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-2 flex items-baseline space-x-2">
            <span className="text-2xl font-bold tracking-tight text-emerald-400 font-mono">{clearedCount}</span>
            <span className="text-[11px] text-emerald-400/70 font-medium">Export Ready</span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-zinc-900/60 p-2 rounded-xl border border-zinc-800">
        {/* Status Pills */}
        <div className="flex items-center space-x-1 overflow-x-auto pb-1 sm:pb-0">
          {statusFilters.map((st) => (
            <button
              key={st}
              onClick={() => setSelectedStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 whitespace-nowrap ${
                selectedStatus === st
                  ? "bg-zinc-800 text-zinc-100 font-semibold shadow-sm border border-zinc-700/80"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/40"
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative min-w-[260px]">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by ID, supplier, or consignee..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-zinc-950/80 text-zinc-200 text-xs pl-9 pr-3 py-1.5 rounded-lg border border-zinc-800 focus:outline-none focus:border-blue-500/80 focus:ring-1 focus:ring-blue-500/20 placeholder-zinc-500 transition-all"
          />
        </div>
      </div>

      {/* High-density Data Table */}
      <div className="glass-panel rounded-xl border border-zinc-800/90 overflow-hidden shadow-card">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/90 text-[11px] font-mono uppercase tracking-wider text-zinc-400">
                <th className="py-3 px-4">Shipment Docket</th>
                <th className="py-3 px-4">Supplier & Origin</th>
                <th className="py-3 px-4">Consignee & Route</th>
                <th className="py-3 px-4 text-right">Declared Value</th>
                <th className="py-3 px-4 text-center">Docs</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/60 text-xs">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-zinc-500">
                    <div className="inline-flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                      <span>Loading shipment records...</span>
                    </div>
                  </td>
                </tr>
              ) : shipments.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-zinc-500">
                    <p className="font-medium text-zinc-400">No shipments found matching criteria</p>
                    <p className="text-[11px] text-zinc-600 mt-1">Try resetting the status filter or search query</p>
                  </td>
                </tr>
              ) : (
                shipments.map((shipment) => (
                  <tr
                    key={shipment.id}
                    onClick={() => onSelectShipment(shipment.id)}
                    className="hover:bg-zinc-800/40 cursor-pointer transition-colors duration-150 group"
                  >
                    {/* Shipment ID */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-medium text-blue-400 group-hover:text-blue-300">
                          {shipment.shipment_number}
                        </span>
                        {shipment.low_confidence_count > 0 && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20" title="Low confidence OCR field flags">
                            {shipment.low_confidence_count} flag{shipment.low_confidence_count > 1 ? "s" : ""}
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-zinc-500 font-mono mt-0.5">
                        {new Date(shipment.created_at).toLocaleDateString()}
                      </div>
                    </td>

                    {/* Supplier */}
                    <td className="py-3.5 px-4 max-w-[240px]">
                      <div className="text-zinc-200 font-medium truncate" title={shipment.supplier_name}>
                        {shipment.supplier_name}
                      </div>
                      <div className="text-[11px] text-zinc-500 flex items-center space-x-1 mt-0.5">
                        <span>{shipment.supplier_country}</span>
                      </div>
                    </td>

                    {/* Consignee & Route */}
                    <td className="py-3.5 px-4 max-w-[260px]">
                      <div className="text-zinc-300 truncate" title={shipment.consignee_name}>
                        {shipment.consignee_name}
                      </div>
                      <div className="text-[10px] text-zinc-500 font-mono flex items-center space-x-1 mt-0.5">
                        <span>{shipment.port_of_loading.split(",")[0]}</span>
                        <ArrowRight className="w-2.5 h-2.5 text-zinc-600 inline" />
                        <span>{shipment.port_of_discharge.split(",")[0]}</span>
                      </div>
                    </td>

                    {/* Declared Value */}
                    <td className="py-3.5 px-4 text-right font-mono text-zinc-200">
                      <div>
                        {shipment.currency} {shipment.total_declared_value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </div>
                    </td>

                    {/* Document Count */}
                    <td className="py-3.5 px-4 text-center">
                      <span className="inline-flex items-center space-x-1 text-zinc-400 text-xs font-mono bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">
                        <Layers className="w-3 h-3 text-zinc-500" />
                        <span>{shipment.document_count}</span>
                      </span>
                    </td>

                    {/* Status Pill */}
                    <td className="py-3.5 px-4 text-center">
                      {getStatusBadge(shipment.status)}
                    </td>

                    {/* Action */}
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectShipment(shipment.id);
                        }}
                        className="inline-flex items-center space-x-1 text-xs text-zinc-400 hover:text-blue-400 font-medium group-hover:translate-x-0.5 transition-all"
                      >
                        <span>Review</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
