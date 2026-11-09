"use client";

import React, { useState, useEffect } from "react";
import { 
  fetchShipments, 
  fetchShipmentDetail, 
  updateField, 
  updateLineItem, 
  overrideCrossCheck, 
  exportFiling,
  runCrossCheck,
  ShipmentListItem,
  ShipmentDetail,
  AuditLog
} from "../lib/api";
import { Navbar } from "../components/Navbar";
import { ShipmentDashboard } from "../components/ShipmentDashboard";
import { DocumentUploadModal, UploadFileItem } from "../components/DocumentUploadModal"; // Added UploadFileItem import
import { ExtractionProcessingModal } from "../components/ExtractionProcessingModal";
import { ReviewWorkspace } from "../components/ReviewWorkspace";
import { ManagerOverrideModal } from "../components/ManagerOverrideModal";
import { ExportApprovalModal } from "../components/ExportApprovalModal";
import { AuditTrailModal } from "../components/AuditTrailModal";

export default function Home() {
  const [currentRole, setCurrentRole] = useState<"Documentation Executive" | "Documentation Manager">("Documentation Executive");

  const [activeShipmentId, setActiveShipmentId] = useState<number | null>(null);
  const [shipments, setShipments] = useState<ShipmentListItem[]>([]);
  const [selectedShipment, setSelectedShipment] = useState<ShipmentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const [selectedStatus, setSelectedStatus] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isProcessingModalOpen, setIsProcessingModalOpen] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isOverrideModalOpen, setIsOverrideModalOpen] = useState(false);
  const [overrideRuleCode, setOverrideRuleCode] = useState<string>("RULE_GROSS_WEIGHT_CONSISTENCY");
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);

  const loadShipments = async () => {
    setIsLoading(true);
    const data = await fetchShipments(selectedStatus, searchQuery);
    setShipments(data);
    setIsLoading(false);
  };

  useEffect(() => {
    loadShipments();
  }, [selectedStatus, searchQuery]);

  const handleSelectShipment = async (id: number) => {
    setActiveShipmentId(id);
    const detail = await fetchShipmentDetail(id);
    setSelectedShipment(detail);
  };

  const [isReRunningChecks, setIsReRunningChecks] = useState(false);

  const handleReRunChecks = async () => {
    if (!activeShipmentId) return;
    setIsReRunningChecks(true);
    try {
      const updatedDetail = await runCrossCheck(activeShipmentId);
      setSelectedShipment(updatedDetail);
    } catch (err) {
      console.error("Failed to re-run checks:", err);
    } finally {
      setIsReRunningChecks(false);
    }
  };

  const handleUpdateField = async (fieldId: number, newValue: string, isConfirmed = true) => {
    if (!activeShipmentId || !selectedShipment) return;
    await updateField(activeShipmentId, fieldId, newValue, isConfirmed, currentRole);
    const updated = await fetchShipmentDetail(activeShipmentId);
    setSelectedShipment(updated);
    loadShipments();
  };

  const handleUpdateLineItem = async (itemId: number, data: any) => {
    if (!activeShipmentId || !selectedShipment) return;
    await updateLineItem(activeShipmentId, itemId, data);
    const updated = await fetchShipmentDetail(activeShipmentId);
    setSelectedShipment(updated);
    loadShipments();
  };

  const handleConfirmOverride = async (ruleCode: string, reason: string) => {
    if (!activeShipmentId || !selectedShipment) return;
    await overrideCrossCheck(activeShipmentId, ruleCode, reason, `Manager (${currentRole})`);
    const updated = await fetchShipmentDetail(activeShipmentId);
    setSelectedShipment(updated);
    loadShipments();
  };

  const handleConfirmExport = async (format: "csv" | "xlsx") => {
    if (!activeShipmentId || !selectedShipment) throw new Error("No shipment active");
    const result = await exportFiling(activeShipmentId, format, currentRole, currentRole === "Documentation Manager" ? "Sarah Chen" : "John Doe");
    const updated = await fetchShipmentDetail(activeShipmentId);
    setSelectedShipment(updated);
    loadShipments();
    return result;
  };

  // Start Ingestion Pipeline (Receives files array from DocumentUploadModal)
  const handleStartExtraction = (uploadedFiles: UploadFileItem[]) => {
    const validFileItem = uploadedFiles.find(f => f.file !== null);
    if (validFileItem && validFileItem.file) {
      setUploadedFile(validFileItem.file);
    }
    setIsUploadModalOpen(false);
    setIsProcessingModalOpen(true);
  };

  const handleExtractionComplete = async () => {
    setIsProcessingModalOpen(false);
    await handleSelectShipment(activeShipmentId || 1);
    loadShipments();
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex flex-col">
      <Navbar
        currentRole={currentRole}
        setCurrentRole={setCurrentRole}
        onOpenAuditTrail={() => setIsAuditModalOpen(true)}
        onNewUpload={() => setIsUploadModalOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {selectedShipment && activeShipmentId ? (
          <ReviewWorkspace
            shipment={selectedShipment}
            onBack={() => {
              setActiveShipmentId(null);
              setSelectedShipment(null);
            }}
            onUpdateField={handleUpdateField}
            onUpdateLineItem={handleUpdateLineItem}
            onReRunChecks={handleReRunChecks}
            isReRunning={isReRunningChecks}
            onOpenOverrideModal={(rule) => {
              setOverrideRuleCode(rule);
              setIsOverrideModalOpen(true);
            }}
            onOpenExportModal={() => setIsExportModalOpen(true)}
            userRole={currentRole}
          />
        ) : (
          <ShipmentDashboard
            shipments={shipments}
            isLoading={isLoading}
            selectedStatus={selectedStatus}
            setSelectedStatus={setSelectedStatus}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            onSelectShipment={handleSelectShipment}
            onOpenUploadModal={() => setIsUploadModalOpen(true)}
          />
        )}
      </main>

      <DocumentUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onStartExtraction={handleStartExtraction}
      />

      <ExtractionProcessingModal
        isOpen={isProcessingModalOpen}
        shipmentId={activeShipmentId || 1}
        file={uploadedFile}
        docType="commercial_invoice"
        onComplete={handleExtractionComplete}
        onClose={() => setIsProcessingModalOpen(false)}
      />

      <ManagerOverrideModal
        isOpen={isOverrideModalOpen}
        onClose={() => setIsOverrideModalOpen(false)}
        ruleCode={overrideRuleCode}
        onConfirmOverride={handleConfirmOverride}
      />

      {selectedShipment && (
        <ExportApprovalModal
          isOpen={isExportModalOpen}
          onClose={() => setIsExportModalOpen(false)}
          shipment={selectedShipment}
          onConfirmExport={handleConfirmExport}
          userRole={currentRole}
        />
      )}

      <AuditTrailModal
        isOpen={isAuditModalOpen}
        onClose={() => setIsAuditModalOpen(false)}
        logs={selectedShipment ? selectedShipment.audit_logs : []}
        shipmentNumber={selectedShipment?.shipment_number}
      />
    </div>
  );
}