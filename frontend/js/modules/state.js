/**
 * PayAgent OS — State & Shared Utilities Module
 */

export const API_BASE = '/api/v1';

export const appState = {
  currentLang: localStorage.getItem('payagent_lang') || 'tr',
  agentsList: [],
  transactionsList: [],
  analyticsData: null,
  currentBiddingResult: null,
};

// DOM Elements Cache
export const el = {
  tabHitlBadge: document.getElementById('tab-hitl-badge'),
  btnGotoP2p: document.getElementById('btn-goto-p2p'),
  p2pDeskTradedVol: document.getElementById('p2p-desk-traded-vol'),
  btnCopyToolkitCode: document.getElementById('btn-copy-toolkit-code'),
  btnLangTr: document.getElementById('btn-lang-tr'),
  btnLangEn: document.getElementById('btn-lang-en'),
  paypalConnLabel: document.getElementById('paypal-conn-label'),
  statAllocated: document.getElementById('stat-allocated'),
  statSpentToday: document.getElementById('stat-spent-today'),
  statPending: document.getElementById('stat-pending'),
  statVolume: document.getElementById('stat-volume'),
  statAgentsCount: document.getElementById('stat-agents-count'),
  simAgentSelect: document.getElementById('sim-agent-select'),
  simAmount: document.getElementById('sim-amount'),
  simRecipient: document.getElementById('sim-recipient'),
  simCategory: document.getElementById('sim-category'),
  simReasoning: document.getElementById('sim-reasoning'),
  simForm: document.getElementById('simulator-form'),
  hitlContainer: document.getElementById('hitl-queue-container'),
  badgeHitlCount: document.getElementById('badge-hitl-count'),
  fleetContainer: document.getElementById('fleet-container'),
  auditTableBody: document.getElementById('audit-table-body'),
  btnRefreshAudit: document.getElementById('btn-refresh-audit'),
  toastContainer: document.getElementById('toast-container'),
  chipPass: document.getElementById('chip-pass'),
  chipExceed: document.getElementById('chip-exceed'),
  chipUnauthorized: document.getElementById('chip-unauthorized'),
  chipPayout: document.getElementById('chip-payout'),
  btnToggleNegotiation: document.getElementById('btn-toggle-negotiation'),
  toggleIcon: document.getElementById('toggle-icon'),
  negotiationDrawer: document.getElementById('negotiation-drawer'),
  negotiationContentBody: document.getElementById('negotiation-content-body'),
  negotiationForm: document.getElementById('negotiation-form'),
  negRequesterSelect: document.getElementById('neg-requester-select'),
  negTargetSelect: document.getElementById('neg-target-select'),
  negAmount: document.getElementById('neg-amount'),
  negUrgency: document.getElementById('neg-urgency'),
  negJustification: document.getElementById('neg-justification'),
  chipPresetNeg: document.getElementById('chip-preset-neg'),
  negotiationChatFeed: document.getElementById('negotiation-chat-feed'),
  // Phase 1 Analytics & Executive Report Elements
  statSavingsAmount: document.getElementById('stat-savings-amount'),
  statP2pVolume: document.getElementById('stat-p2p-volume'),
  statAutonomyRate: document.getElementById('stat-autonomy-rate'),
  donutChartSvg: document.getElementById('donut-chart-svg'),
  donutTotalLabel: document.getElementById('donut-total-label'),
  donutCenterTotal: document.getElementById('donut-center-total'),
  donutLegend: document.getElementById('donut-legend'),
  vendorBarsContainer: document.getElementById('vendor-bars-container'),
  btnOpenPdfReport: document.getElementById('btn-open-pdf-report'),
  executiveReportModal: document.getElementById('executive-report-modal'),
  btnCloseReport: document.getElementById('btn-close-report'),
  btnPrintReport: document.getElementById('btn-print-report'),
  reportDateTime: document.getElementById('report-date-time'),
  repTotalBalance: document.getElementById('rep-total-balance'),
  repSpentToday: document.getElementById('rep-spent-today'),
  repSavedReserve: document.getElementById('rep-saved-reserve'),
  repP2pVolume: document.getElementById('rep-p2p-volume'),
  repAgentsTableBody: document.getElementById('rep-agents-table-body'),
  repAuditTableBody: document.getElementById('rep-audit-table-body'),
  // Interactive Workbench Elements (Stress Simulator & CFO Copilot)
  sliderInflation: document.getElementById('slider-inflation'),
  sliderTraffic: document.getElementById('slider-traffic'),
  selectOutage: document.getElementById('select-outage'),
  valInflation: document.getElementById('val-inflation'),
  valTraffic: document.getElementById('val-traffic'),
  stressRiskBadge: document.getElementById('stress-risk-badge'),
  projBurnRate: document.getElementById('proj-burn-rate'),
  projExhaustionHours: document.getElementById('proj-exhaustion-hours'),
  projDeficit: document.getElementById('proj-deficit'),
  projRecommendation: document.getElementById('proj-recommendation'),
  cfoQueryForm: document.getElementById('cfo-query-form'),
  cfoInputQuestion: document.getElementById('cfo-input-question'),
  cfoBubbleText: document.getElementById('cfo-bubble-text'),
  cfoTimeStamp: document.getElementById('cfo-time-stamp'),
  cfoActionRow: document.getElementById('cfo-action-row'),
  cfoActionText: document.getElementById('cfo-action-text'),
  btnCfoAction: document.getElementById('btn-cfo-action'),
};

// Toast System
export function showToast(message, type = 'success') {
  if (!el.toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast-msg ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : type === 'warning' ? '⚠️' : '✕'}</span> ${message}`;
  el.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// 1-Click Copy Reference ID
export function copyRef(text) {
  navigator.clipboard.writeText(text);
  showToast(appState.currentLang === 'tr' ? `Kopyalandı: ${text}` : `Copied: ${text}`, 'success');
}

// Attach to global window for onclick attributes
window.copyRef = copyRef;
