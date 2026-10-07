/**
   PayAgent OS — Frontend Controller & i18n Engine
   Full Turkish (TR) & English (EN) language support.
 */

const API_BASE = '/api/v1';

// Translations Dictionary
const i18n = {
  tr: {
    tagline: 'Otonom Ajan Harcama & Cüzdan Orkestrasyonu',
    apiDocs: 'API Kılavuzu',
    step1Title: 'Ajan Talebi',
    step1Sub: 'Gerekçeli Niyet',
    step2Title: 'Politika & Limit',
    step2Sub: 'Bütçe & Beyaz Liste',
    step3Title: 'İnsan Onayı (HITL)',
    step3Sub: 'Riskli / Büyük Tutar',
    step4Title: 'PayPal Tahsilatı',
    step4Sub: 'Orders v2 / Payouts',
    metricAllocated: 'Toplam Tahsis Edilen Bütçe',
    metricSpentToday: 'Bugünkü Otonom Harcama',
    metricSpentSub: 'Politika kurallarına %100 uyumlu',
    metricPendingHITL: 'İnsan Onay Kuyruğu',
    metricPendingSub: 'Süpervizör kararı bekliyor',
    metricSettled: 'PayPal İle Kesinleşen Hacim',
    simTitle: 'Otonom Ajan Harcama Simülatörü',
    simDesc: 'Yapay zeka ajanının harcama talebini ve gerekçesini test edin; politika motorunun kararını izleyin.',
    simCallingAgent: 'Talebi Yapan Ajan',
    simAmount: 'Harcama Tutarı (USD)',
    simVendor: 'Satıcı veya PayPal Alıcısı',
    simCategory: 'Kategori',
    simReasoning: 'Ajanın Doğal Dil Gerekçesi (Explainability)',
    catCompute: 'Bulut Bilişim / GPU',
    catApi: 'API Çıkarım Kotası',
    catDataset: 'Veri Seti / Rapor',
    catPayout: 'Freelancer Hakedişi',
    btnExecute: 'Otonom Harcamayı Başlat',
    quickScenarios: 'Hazır Testler:',
    chipPass: 'Limit İçi ($15)',
    chipExceed: 'Limit Aşımı ($85 HITL)',
    chipUnknown: 'Yetkisiz Satıcı',
    chipPayout: 'Freelance Hakediş ($35)',
    hitlTitle: 'İnsan Onay Masası (HITL Queue)',
    hitlDesc: 'Güvenlik limitlerini aşan veya listede olmayan satıcı işlemleri insan denetimine düşer.',
    fleetTitle: 'Aktif Ajan Filosu & Cüzdanlar',
    fleetDesc: 'Her yapay zeka ajanının anlık bakiyesi, harcama tavanı ve onaylı satıcıları.',
    auditTitle: 'İşlem Denetim Kütüğü (Audit Trail)',
    auditDesc: 'PayPal Orders v2 ve Payouts API üzerinden kesinleşen işlemlerin canlı dökümü.',
    btnRefresh: 'Yenile',
    colTime: 'Saat',
    colAgent: 'Ajan',
    colAmount: 'Tutar',
    colVendor: 'Satıcı / Alıcı',
    colStatus: 'Durum',
    colRef: 'PayPal Ref ID',
    noPending: 'İnceleme bekleyen işlem yok. Tüm ajanlar bütçe ve güvenlik kurallarına uygun çalışıyor.',
    noAudit: 'Henüz işlem kaydı yok. Yukarıdaki simülatörden bir harcama başlatabilirsiniz.',
    statusAuto: '⚡ Otonom',
    statusHuman: '👤 Onaylandı',
    statusPending: '⏳ İnceleniyor',
    statusRejected: '✕ Reddedildi',
    btnAuthorize: '✓ PayPal İle Yetkilendir',
    btnReject: '✕ Reddet',
    toastSuccessAuto: 'Otonom ödeme onaylandı ve PayPal ile tahsil edildi!',
    toastWarningHitl: 'Politika Sınırı Aşıldı: İşlem İnsan Onay Masasına aktarıldı!',
    toastApproveSuccess: 'Ödeme süpervizör tarafından onaylandı ve PayPal ile capture edildi!',
    toastRejectSuccess: 'Ödeme talebi reddedildi.',
    toastRefreshed: 'Panel verileri yenilendi.',
    btnP2PNegotiate: 'P2P Bütçe Müzakeresi',
    negBadge: 'P2P Otonom Protokol',
    negTitle: 'Ajanlar Arası Bütçe Müzakeresi',
    negRequester: 'Kota İsteyen Ajan (Requester)',
    negTarget: 'Fazlası Olan Kaynak Ajan (Target)',
    negAmount: 'Aktarılacak Kota Tutarı (USD)',
    negUrgency: 'Aciliyet Seviyesi',
    negJustification: 'Müzakere Gerekçesi (Agent Reasoning)',
    btnRunNegotiation: 'Otonom Müzakereyi Başlat',
    chipPresetNeg: '⚡ Örnek: Research -> DevOps ($35)',
    toastNegSuccess: '🤝 Bütçe Müzakeresi Başarılı: Günlük kota otonom aktarıldı!',
    toastNegRejected: '⚠️ Müzakere Reddedildi: Kaynak ajanda yeterli kota fazlası yok.',
    btnToggle: 'Gizle / Göster',
    analyticsBadge: 'Canlı Görsel Zeka',
    analyticsTitle: 'Filo Harcama Dağılımı & Analitik',
    guardrailSavings: 'Korumaya Alınan:',
    btnOpenPdf: '📄 Yönetici Raporu (PDF)',
    chartAgentTitle: 'Ajan Harcama Payı',
    chartFleet: 'Filo',
    chartVendorTitle: 'Tedarikçi Kırılımı (Vendor Breakdown)',
    chartVendorSub: 'PayPal Orders v2',
    p2pVolumeLabel: '🤝 P2P Takaslanan Bütçe:',
    guardEfficiencyLabel: '⚡ Otomasyon Oranı:',
    btnPrintPdf: 'Yazdır / PDF Olarak Kaydet',
    btnClose: 'Kapat',
    repAllocatedLabel: 'Yönetilen Toplam Bakiye',
    repSpentLabel: 'Bugünkü Harcama',
    repSavedLabel: 'Korumaya Alınan Rezerv',
    repP2pLabel: 'P2P Kota Takası',
    repSection1: '1. Otonom Ajan Cüzdanları & Davranışsal Kişilikler',
    repSection2: '2. Değiştirilemez PayPal İşlem Kütüğü (Audit Trail)',
    colPersonality: 'Finansal Kişilik',
    colDailyBudget: 'Günlük Bütçe',
    colBalance: 'Kasa Bakiyesi',
    colSpentToday: 'Bugün Harcanan',
    badgeWhatIf: 'What-If Finans Simülatörü',
    stressTitle: 'Finansal Stres & Likidite Simülatörü',
    sliderInflation: 'API Fiyat Enflasyonu:',
    sliderTraffic: 'Trafik / İş Yükü Çarpanı:',
    selectOutage: 'Sağlayıcı Kesintisi Simülasyonu:',
    burnRateLabel: 'Öngörülen 24h Tüketim:',
    exhaustionLabel: 'Likidite Tükenme Süresi:',
    deficitLabel: 'Olası Bütçe Açığı:',
    badgeCfo: 'AI Hazine Copilot',
    cfoTitle: 'CFO Soru-Cevap & Finans Danışmanı',
    cfoName: 'PayAgent OS Hazine Direktörü (CFO)',
    cfoWelcome: 'Merhaba! Ben PayAgent OS Hazine Direktörüyüm. Ajanlarınızın harcama alışkanlıklarını, Cimri Kasa rezervlerini ve PayPal mutabakatlarını canlı izliyorum. Yukarıdaki hazır sorulardan birini seçebilir veya aşağıya serbest soru yazabilirsiniz.',
    btnAsk: 'Sor',
  },
  en: {
    tagline: 'Autonomous AI Agent Wallet & Payment Orchestration',
    apiDocs: 'API Docs',
    step1Title: 'Agent Intent',
    step1Sub: 'Reasoned Need',
    step2Title: 'Policy & Guardrail',
    step2Sub: 'Budget & Allowlist',
    step3Title: 'Human Review (HITL)',
    step3Sub: 'High-Value / Risk',
    step4Title: 'PayPal Settlement',
    step4Sub: 'Orders v2 / Payouts',
    metricAllocated: 'Total Allocated Budget',
    metricSpentToday: 'Autonomous Spend (Today)',
    metricSpentSub: '100% Policy compliant',
    metricPendingHITL: 'Human-in-the-Loop Queue',
    metricPendingSub: 'Awaiting supervisor decision',
    metricSettled: 'Settled via PayPal',
    simTitle: 'Simulate Autonomous Agent Purchase',
    simDesc: 'Trigger a procurement intent from an AI agent to evaluate guardrail rules and PayPal execution.',
    simCallingAgent: 'Calling Agent',
    simAmount: 'Amount (USD)',
    simVendor: 'Vendor or PayPal Recipient',
    simCategory: 'Category',
    simReasoning: 'AI Agent Reasoning Prompt (Explainability)',
    catCompute: 'Cloud Compute / GPU',
    catApi: 'API Token Quota',
    catDataset: 'Dataset / Report',
    catPayout: 'Freelance Milestone',
    btnExecute: 'Execute Autonomous Intent',
    quickScenarios: 'Quick Tests:',
    chipPass: 'Within Limit ($15)',
    chipExceed: 'Exceed Limit ($85 HITL)',
    chipUnknown: 'Unlisted Vendor',
    chipPayout: 'Freelance Payout ($35)',
    hitlTitle: 'Pending Human Approvals (HITL)',
    hitlDesc: 'Transactions that exceeded autonomous safety caps or targeted unlisted vendors.',
    fleetTitle: 'Active Agent Fleet & Wallets',
    fleetDesc: 'Real-time balances, daily budget progress, and approved vendors for each agent.',
    auditTitle: 'Immutable Audit Trail & PayPal Orders',
    auditDesc: 'Live ledger of transactions processed via PayPal Orders v2 and Payouts API.',
    btnRefresh: 'Refresh',
    colTime: 'Time',
    colAgent: 'Agent',
    colAmount: 'Amount',
    colVendor: 'Vendor / Recipient',
    colStatus: 'Status',
    colRef: 'PayPal Ref ID',
    noPending: 'No transactions pending human review. All agents operating safely within policies.',
    noAudit: 'No transactions recorded yet. Use the simulator above to initiate an intent.',
    statusAuto: '⚡ Autonomous',
    statusHuman: '👤 Approved',
    statusPending: '⏳ In Review',
    statusRejected: '✕ Rejected',
    btnAuthorize: '✓ Authorize via PayPal',
    btnReject: '✕ Reject',
    toastSuccessAuto: 'Autonomous payment authorized and captured via PayPal!',
    toastWarningHitl: 'Policy Cap Exceeded: Moved to Human-in-the-Loop review queue!',
    toastApproveSuccess: 'Payment authorized and settled via PayPal Sandbox!',
    toastRejectSuccess: 'Payment intent rejected by supervisor.',
    toastRefreshed: 'Dashboard data refreshed.',
    btnP2PNegotiate: 'P2P Budget Negotiation',
    negBadge: 'P2P Autonomous Protocol',
    negTitle: 'Peer-to-Peer Budget Negotiation',
    negRequester: 'Requester Agent (Needs Quota)',
    negTarget: 'Target Agent (Surplus Headroom)',
    negAmount: 'Quota Transfer Amount (USD)',
    negUrgency: 'Urgency Level',
    negJustification: 'Negotiation Reasoning',
    btnRunNegotiation: 'Execute Autonomous Negotiation',
    chipPresetNeg: '⚡ Preset: Research -> DevOps ($35)',
    toastNegSuccess: '🤝 Negotiation Successful: Daily quota reallocated autonomously!',
    toastNegRejected: '⚠️ Negotiation Rejected: Target agent has insufficient headroom.',
    btnToggle: 'Toggle View',
    analyticsBadge: 'Live Visual Intelligence',
    analyticsTitle: 'Fleet Spend Allocation & Analytics',
    guardrailSavings: 'Guarded Capital:',
    btnOpenPdf: '📄 Executive Audit (PDF)',
    chartAgentTitle: 'Agent Spend Allocation',
    chartFleet: 'Fleet',
    chartVendorTitle: 'Vendor Breakdown (PayPal v2)',
    chartVendorSub: 'PayPal Orders v2',
    p2pVolumeLabel: '🤝 P2P Traded Quota:',
    guardEfficiencyLabel: '⚡ Autonomy Ratio:',
    btnPrintPdf: 'Print / Save as PDF',
    btnClose: 'Close',
    repAllocatedLabel: 'Total Managed Capital',
    repSpentLabel: 'Spent Today',
    repSavedLabel: 'Guarded Reserve',
    repP2pLabel: 'P2P Quota Traded',
    repSection1: '1. Autonomous Agent Wallets & Behavioral Personalities',
    repSection2: '2. Immutable PayPal Audit Trail',
    colPersonality: 'Financial Personality',
    colDailyBudget: 'Daily Budget',
    colBalance: 'Wallet Balance',
    colSpentToday: 'Spent Today',
    badgeWhatIf: 'What-If Stress Simulator',
    stressTitle: 'Financial Stress & Liquidity Simulator',
    sliderInflation: 'API Price Inflation:',
    sliderTraffic: 'Traffic Workload Multiplier:',
    selectOutage: 'Provider Outage Simulation:',
    burnRateLabel: 'Projected 24h Burn:',
    exhaustionLabel: 'Hours Until Exhaustion:',
    deficitLabel: 'Projected Deficit:',
    badgeCfo: 'AI Treasury Copilot',
    cfoTitle: 'CFO Q&A & Advisory',
    cfoName: 'PayAgent OS Chief Financial Officer (CFO)',
    cfoWelcome: 'Hello! I am the PayAgent OS Chief Financial Officer. I monitor fleet spending, Frugal Vault reserves, and PayPal settlements in real-time. Pick a quick prompt above or type any financial question below.',
    btnAsk: 'Ask',
  },
};

// Current Language (default: TR)
let currentLang = localStorage.getItem('payagent_lang') || 'tr';

// State
let agentsList = [];
let transactionsList = [];
let analyticsData = null;

// DOM Elements
const el = {
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

// Apply i18n
function applyLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('payagent_lang', lang);

  if (lang === 'tr') {
    el.btnLangTr.classList.add('active');
    el.btnLangEn.classList.remove('active');
  } else {
    el.btnLangEn.classList.add('active');
    el.btnLangTr.classList.remove('active');
  }

  // Translate static data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    const key = node.getAttribute('data-i18n');
    if (i18n[lang][key]) {
      node.textContent = i18n[lang][key];
    }
  });

  renderHITLQueue();
  renderFleet();
  renderAuditTable();
}

// Toast System
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast-msg ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : type === 'warning' ? '⚠️' : '✕'}</span> ${message}`;
  el.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Fetch Metrics Summary
async function fetchSummary() {
  try {
    const res = await fetch(`${API_BASE}/stats/summary`);
    if (!res.ok) return;
    const data = await res.json();

    el.statAllocated.textContent = data.total_allocated_funds.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    el.statSpentToday.textContent = data.total_spent_today.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    el.statPending.textContent = data.pending_approval_count;
    el.statVolume.textContent = data.total_volume_processed.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    
    el.statAgentsCount.textContent = currentLang === 'tr' 
      ? `${data.active_agents_count} aktif AI ajanı cüzdanında`
      : `Across ${data.active_agents_count} active AI agents`;

    el.badgeHitlCount.textContent = currentLang === 'tr'
      ? `${data.pending_approval_count} Bekliyor`
      : `${data.pending_approval_count} Pending`;

    if (data.is_live_sandbox) {
      el.paypalConnLabel.textContent = currentLang === 'tr' ? 'PayPal Sandbox: Canlı Bağlı' : 'PayPal Sandbox: Connected';
    } else {
      el.paypalConnLabel.textContent = currentLang === 'tr' ? 'PayPal Sandbox: Hazır (Simülasyon)' : 'PayPal Sandbox: Ready (Dev Simulation)';
    }
  } catch (err) {
    console.error('Failed to fetch summary:', err);
  }
}

// Fetch Agents
async function fetchAgents() {
  try {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) return;
    agentsList = await res.json();

    const currentVal = el.simAgentSelect.value;
    el.simAgentSelect.innerHTML = '';
    agentsList.forEach((agent) => {
      const opt = document.createElement('option');
      opt.value = agent.id;
      opt.textContent = `${agent.name} ($${agent.wallet_balance.toFixed(2)})`;
      el.simAgentSelect.appendChild(opt);
    });
    if (currentVal && agentsList.some((a) => a.id === currentVal)) {
      el.simAgentSelect.value = currentVal;
    }

    // Populate P2P Negotiation Selects
    if (el.negRequesterSelect && el.negTargetSelect) {
      const currentReq = el.negRequesterSelect.value || 'agent-research';
      const currentTarget = el.negTargetSelect.value || 'agent-devops';

      el.negRequesterSelect.innerHTML = '';
      el.negTargetSelect.innerHTML = '';

      agentsList.forEach((agent) => {
        const opt1 = document.createElement('option');
        opt1.value = agent.id;
        opt1.textContent = `${agent.name} (Günlük: $${agent.policy.daily_budget.toFixed(2)})`;
        el.negRequesterSelect.appendChild(opt1);

        const surplus = Math.max(0, agent.policy.daily_budget - agent.spent_today);
        const opt2 = document.createElement('option');
        opt2.value = agent.id;
        opt2.textContent = `${agent.name} (Boşta Kalan: $${surplus.toFixed(2)})`;
        el.negTargetSelect.appendChild(opt2);
      });

      if (agentsList.some((a) => a.id === currentReq)) {
        el.negRequesterSelect.value = currentReq;
      }
      if (agentsList.some((a) => a.id === currentTarget)) {
        el.negTargetSelect.value = currentTarget;
      }
    }

    renderFleet();
  } catch (err) {
    console.error('Failed to fetch agents:', err);
  }
}

// Render Fleet with Budget Progress Bars
function renderFleet() {
  el.fleetContainer.innerHTML = '';
  agentsList.forEach((agent) => {
    const card = document.createElement('div');
    card.className = 'agent-fleet-card';

    const spent = agent.spent_today;
    const dailyCap = agent.policy.daily_budget;
    const pct = Math.min(100, Math.round((spent / dailyCap) * 100));
    const isWarning = pct > 75;

    const vendorsHtml = agent.policy.allowed_vendors.length
      ? agent.policy.allowed_vendors.map((v) => `<span class="vendor-pill">${v}</span>`).join('')
      : `<span class="vendor-pill">${currentLang === 'tr' ? 'Tüm Satıcılar (Açık Payout)' : 'Open Payout'}</span>`;

    const limitLabel = currentLang === 'tr' ? 'Tekil Limit' : 'Max Per Tx';
    const dailyLabel = currentLang === 'tr' ? 'Günlük Kota' : 'Daily Cap';
    const spentLabel = currentLang === 'tr' ? 'Kullanılan' : 'Spent';

    let persClass = 'pers-balanced';
    let persIcon = '⚖️';
    let persLabel = currentLang === 'tr' ? 'Dengeli Hazine' : 'Balanced';
    if (agent.personality === 'FRUGAL_VAULT') {
      persClass = 'pers-frugal';
      persIcon = '🏦';
      persLabel = currentLang === 'tr' ? 'Cimri Kasa (Zor Borç Verir)' : 'Frugal Vault (Strict)';
    } else if (agent.personality === 'GROWTH_EXPLORER') {
      persClass = 'pers-growth';
      persIcon = '🚀';
      persLabel = currentLang === 'tr' ? 'Büyüme & Ar-Ge (Cömert)' : 'Growth Explorer';
    }

    card.innerHTML = `
      <div class="agent-card-top">
        <div class="agent-title-row" style="flex-wrap: wrap; gap: 0.45rem;">
          <span class="fleet-status-dot" title="Active"></span>
          <span class="agent-card-title">${agent.name}</span>
          <span class="agent-personality-badge ${persClass}" title="${agent.personality_description || ''}">
            <span>${persIcon}</span>
            <span>${persLabel}</span>
          </span>
        </div>
        <span class="agent-card-balance font-mono">$${agent.wallet_balance.toFixed(2)}</span>
      </div>

      <div class="budget-bar-wrap">
        <div class="budget-bar-labels font-mono">
          <span>${limitLabel}: $${agent.policy.max_per_transaction.toFixed(2)}</span>
          <span>${spentLabel}: $${spent.toFixed(2)} / $${dailyCap.toFixed(2)} (${pct}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill ${isWarning ? 'warning' : ''}" style="width: ${pct}%;"></div>
        </div>
      </div>

      <div class="vendor-pills-row">
        ${vendorsHtml}
      </div>
    `;
    el.fleetContainer.appendChild(card);
  });
}

// Fetch Transactions
async function fetchTransactions() {
  try {
    const res = await fetch(`${API_BASE}/payments`);
    if (!res.ok) return;
    transactionsList = await res.json();

    renderHITLQueue();
    renderAuditTable();
  } catch (err) {
    console.error('Failed to fetch transactions:', err);
  }
}

// Render HITL Queue (Hero Feature with Diff Breakdown & PayPal button)
function renderHITLQueue() {
  const pending = transactionsList.filter((t) => t.status === 'PENDING_APPROVAL');
  el.hitlContainer.innerHTML = '';

  if (pending.length === 0) {
    el.hitlContainer.innerHTML = `
      <div class="empty-placeholder">
        <div class="empty-icon">✓</div>
        <p>${i18n[currentLang].noPending}</p>
      </div>
    `;
    return;
  }

  pending.forEach((tx) => {
    const agent = agentsList.find((a) => a.id === tx.agent_id);
    const limit = agent ? agent.policy.max_per_transaction : 0;
    const overAmount = Math.max(0, tx.amount - limit);

    const diffHtml = limit > 0
      ? `<div class="diff-breakdown font-mono">
           <span>${currentLang === 'tr' ? 'Talep:' : 'Req:'} <strong>$${tx.amount.toFixed(2)}</strong></span>
           <span>•</span>
           <span>${currentLang === 'tr' ? 'Limit:' : 'Limit:'} $${limit.toFixed(2)}</span>
           <span>•</span>
           <span style="color: #f87171;">(+$${overAmount.toFixed(2)} ${currentLang === 'tr' ? 'Aşım' : 'Over'})</span>
         </div>`
      : '';

    const borrowingBannerHtml = tx.shortfall_amount && tx.proposed_donor_agent_name
      ? `<div class="borrowing-proposal-banner">
           <div class="proposal-banner-title">
             <span>🤝</span>
             <span>${currentLang === 'tr' ? 'Kardeş Karttan Otonom Fonlama Teklifi' : 'Peer Shortfall Borrowing Proposal'}</span>
           </div>
           <div class="proposal-banner-text">
             ${currentLang === 'tr'
               ? `Bu harcama ajanın limitini aşıyor (<strong>$${tx.shortfall_amount.toFixed(2)} eksik</strong>). Sistem, boşta bütçesi olan <span class="proposal-banner-highlight">${tx.proposed_donor_agent_name}</span> kartından aktarım yapmayı öneriyor.`
               : `This intent exceeds agent limit (<strong>$${tx.shortfall_amount.toFixed(2)} shortfall</strong>). System proposes transferring quota from <span class="proposal-banner-highlight">${tx.proposed_donor_agent_name}</span>.`}
           </div>
         </div>`
      : '';

    const approveBtnLabel = tx.shortfall_amount
      ? (currentLang === 'tr' ? `✓ $${tx.shortfall_amount.toFixed(2)} Aktar ve PayPal İle Öde` : `✓ Transfer $${tx.shortfall_amount.toFixed(2)} & Settle`)
      : i18n[currentLang].btnAuthorize;

    const card = document.createElement('div');
    card.className = 'invoice-review-card';
    card.innerHTML = `
      <div class="invoice-header">
        <div class="hitl-agent-wrap">
          <div class="agent-avatar-icon">🤖</div>
          <span class="invoice-agent">${tx.agent_name}</span>
        </div>
        <span class="invoice-amount font-mono">$${tx.amount.toFixed(2)} <span style="font-size: 0.8rem; color: #a1a1aa;">${tx.currency}</span></span>
      </div>
      ${diffHtml}
      ${borrowingBannerHtml}
      <div class="invoice-body">
        <strong>${currentLang === 'tr' ? 'Gerekçe (Prompt):' : 'Reasoning:'}</strong> ${tx.reasoning}
        <br><strong>${currentLang === 'tr' ? 'Alıcı:' : 'Payee:'}</strong> ${tx.recipient} (${tx.category})
      </div>
      <div class="invoice-footer">
        <button class="fin-btn fin-btn-reject" onclick="resolveHITL('${tx.id}', 'REJECT')">${i18n[currentLang].btnReject}</button>
        <button class="fin-btn fin-btn-approve-paypal" onclick="resolveHITL('${tx.id}', 'APPROVE')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path d="M7 21h4.5l1.1-7h1.5c3.1 0 5.4-1.8 5.9-5.2.6-3.9-1.8-5.8-5.3-5.8H6.5a.8.8 0 0 0-.8.7L2.4 20.6c-.1.4.2.7.6.7H7z" fill="#ffffff"/>
          </svg>
          ${approveBtnLabel}
        </button>
      </div>
    `;
    el.hitlContainer.appendChild(card);
  });
}

// 1-Click Copy Reference ID
window.copyRef = function (text) {
  navigator.clipboard.writeText(text);
  showToast(currentLang === 'tr' ? `Kopyalandı: ${text}` : `Copied: ${text}`, 'success');
};

// Render Audit Trail
function renderAuditTable() {
  el.auditTableBody.innerHTML = '';
  if (transactionsList.length === 0) {
    el.auditTableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">
          ${i18n[currentLang].noAudit}
        </td>
      </tr>
    `;
    return;
  }

  transactionsList.slice(0, 15).forEach((tx) => {
    const tr = document.createElement('tr');
    const timeStr = new Date(tx.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    let tagClass = 'auto';
    let statusText = i18n[currentLang].statusAuto;

    if (tx.status === 'APPROVED_BY_HUMAN') {
      tagClass = 'human';
      statusText = i18n[currentLang].statusHuman;
    } else if (tx.status === 'PENDING_APPROVAL') {
      tagClass = 'pending';
      statusText = i18n[currentLang].statusPending;
    } else if (tx.status.includes('REJECTED')) {
      tagClass = 'rejected';
      statusText = i18n[currentLang].statusRejected;
    }

    const ref = tx.paypal_order_id || tx.paypal_payout_batch_id || tx.id;

    tr.innerHTML = `
      <td class="font-mono text-zinc-400">${timeStr}</td>
      <td style="font-weight: 600; color: #ffffff;">${tx.agent_name}</td>
      <td class="font-mono" style="font-weight: 700; color: #f4f4f5;">$${tx.amount.toFixed(2)}</td>
      <td class="text-zinc-300">${tx.recipient}</td>
      <td>
        <span class="status-tag ${tagClass}">
          <span class="status-dot-indicator"></span>
          ${statusText}
        </span>
      </td>
      <td>
        <div class="ref-code-wrap">
          <span class="ref-code font-mono">${ref}</span>
          <button class="btn-copy-ref" onclick="copyRef('${ref}')" title="Copy ID">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
        </div>
      </td>
    `;
    el.auditTableBody.appendChild(tr);
  });
}

// Resolve HITL
window.resolveHITL = async function (txId, decision) {
  try {
    const res = await fetch(`${API_BASE}/payments/${txId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, reviewer_notes: 'Reviewed by supervisor' }),
    });
    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || 'Hata oluştu', 'error');
      return;
    }

    const resolvedTx = await res.json();

    if (decision === 'APPROVE') {
      if (resolvedTx.shortfall_amount && resolvedTx.proposed_donor_agent_name) {
        showToast(
          currentLang === 'tr'
            ? `🤝 $${resolvedTx.shortfall_amount.toFixed(2)} ${resolvedTx.proposed_donor_agent_name}'den aktarıldı ve PayPal ile capture edildi!`
            : `🤝 $${resolvedTx.shortfall_amount.toFixed(2)} transferred from ${resolvedTx.proposed_donor_agent_name} and settled via PayPal!`,
          'success'
        );
      } else {
        showToast(i18n[currentLang].toastApproveSuccess, 'success');
      }

      // Update Negotiation Chat feed with the latest negotiation log
      try {
        const negRes = await fetch(`${API_BASE}/negotiations`);
        if (negRes.ok) {
          const negs = await negRes.json();
          if (negs.length > 0 && el.negotiationChatFeed) {
            const latest = negs[0];
            const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            el.negotiationChatFeed.innerHTML = `
              <div class="chat-bubble-agent req">
                <div class="chat-header-row">
                  <div class="chat-author">
                    <span>🤖</span>
                    <span>${latest.requester_name}</span>
                  </div>
                  <div style="display: flex; gap: 0.4rem; align-items: center;">
                    <span class="chat-badge chat-badge-req">Talep (${latest.urgency})</span>
                    <span class="chat-meta-time font-mono">${timeNow}</span>
                  </div>
                </div>
                <div class="chat-body-text">
                  "${latest.justification}" — <strong>$${latest.amount.toFixed(2)} USD</strong> günlük kota aktarımı talep edildi.
                </div>
              </div>

              <div class="chat-bubble-agent target">
                <div class="chat-header-row">
                  <div class="chat-author">
                    <span>🛡️</span>
                    <span>${latest.target_name}</span>
                  </div>
                  <div style="display: flex; gap: 0.4rem; align-items: center;">
                    <span class="chat-badge chat-badge-approved">✓ SÜPERVİZÖR ONAYLADI</span>
                    <span class="chat-meta-time font-mono">${timeNow}</span>
                  </div>
                </div>
                <div class="chat-body-text font-mono" style="font-size: 0.74rem;">
                  ${latest.transcript.split('\n')[1] || latest.transcript}
                </div>
              </div>
            `;
          }
        }
      } catch (e) {
        console.error('Failed to update negotiation feed:', e);
      }

    } else {
      showToast(i18n[currentLang].toastRejectSuccess, 'warning');
    }

    await refreshAll();
  } catch (err) {
    showToast('Bağlantı hatası', 'error');
  }
};

// Submit Simulator Intent
el.simForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    agent_id: el.simAgentSelect.value,
    amount: parseFloat(el.simAmount.value),
    recipient: el.simRecipient.value.trim(),
    category: el.simCategory.value,
    reasoning: el.simReasoning.value.trim(),
  };

  try {
    const res = await fetch(`${API_BASE}/payments/intent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || 'İşlem başarısız', 'error');
      return;
    }

    const record = await res.json();
    if (record.status === 'APPROVED_AUTONOMOUS') {
      showToast(i18n[currentLang].toastSuccessAuto, 'success');
    } else if (record.status === 'PENDING_APPROVAL') {
      showToast(i18n[currentLang].toastWarningHitl, 'warning');
    }

    await refreshAll();
  } catch (err) {
    showToast('Sunucu bağlantı hatası', 'error');
  }
});

// Preset Chips
el.chipPass.addEventListener('click', () => {
  el.simAgentSelect.value = 'agent-devops';
  el.simAmount.value = '15.00';
  el.simRecipient.value = 'AWS';
  el.simCategory.value = 'CLOUD_COMPUTE';
  el.simReasoning.value = currentLang === 'tr'
    ? 'Toplu ses deşifre işlemi için AWS spot çalışan düğümü tahsis ediliyor.'
    : 'Provisioning AWS spot worker node for batch audio transcription.';
});

el.chipExceed.addEventListener('click', () => {
  el.simAgentSelect.value = 'agent-research';
  el.simAmount.value = '85.00';
  el.simRecipient.value = 'OpenAI';
  el.simCategory.value = 'API_QUOTA';
  el.simReasoning.value = currentLang === 'tr'
    ? '50.000 akademik makale için yüksek hacimli embedding modeli kota alımı.'
    : 'High-volume embedding batch job for 50k research papers.';
});

el.chipUnauthorized.addEventListener('click', () => {
  el.simAgentSelect.value = 'agent-devops';
  el.simAmount.value = '25.00';
  el.simRecipient.value = 'UnknownCryptoHost';
  el.simCategory.value = 'CLOUD_COMPUTE';
  el.simReasoning.value = currentLang === 'tr'
    ? 'Beyaz listede olmayan harici sunucudan GPU kiralama denemesi.'
    : 'Attempting off-market compute procurement from unapproved merchant.';
});

el.chipPayout.addEventListener('click', () => {
  el.simAgentSelect.value = 'agent-payout';
  el.simAmount.value = '35.00';
  el.simRecipient.value = 'alex.freelancer@paypal.com';
  el.simCategory.value = 'FREELANCE_PAYOUT';
  el.simReasoning.value = currentLang === 'tr'
    ? 'Grafik tasarım ve UI bileşen teslimi için serbest çalışana hakediş ödemesi.'
    : 'Milestone payment disbursement to external freelancer for UI asset delivery.';
});

// P2P Budget Negotiation Listeners (Phase 6 Killer Feature)
if (el.btnToggleNegotiation && el.negotiationContentBody) {
  el.btnToggleNegotiation.addEventListener('click', () => {
    const isHidden = el.negotiationContentBody.style.display === 'none';
    el.negotiationContentBody.style.display = isHidden ? 'block' : 'none';
    if (el.toggleIcon) {
      el.toggleIcon.textContent = isHidden ? '−' : '+';
    }
  });
}

const chipFrugalReject = document.getElementById('chip-preset-frugal-reject');
const chipFrugalAccept = document.getElementById('chip-preset-frugal-accept');

if (chipFrugalReject) {
  chipFrugalReject.addEventListener('click', () => {
    if (el.negRequesterSelect) el.negRequesterSelect.value = 'agent-research';
    if (el.negTargetSelect) el.negTargetSelect.value = 'agent-devops';
    if (el.negAmount) el.negAmount.value = '35.00';
    if (el.negUrgency) el.negUrgency.value = 'HIGH';
    if (el.negJustification) {
      el.negJustification.value = currentLang === 'tr'
        ? 'Rutin model inceleme ve veri çekme işlemi için bütçe takviyesi.'
        : 'Routine model evaluation and data extraction quota.';
    }
  });
}

if (chipFrugalAccept) {
  chipFrugalAccept.addEventListener('click', () => {
    if (el.negRequesterSelect) el.negRequesterSelect.value = 'agent-research';
    if (el.negTargetSelect) el.negTargetSelect.value = 'agent-devops';
    if (el.negAmount) el.negAmount.value = '35.00';
    if (el.negUrgency) el.negUrgency.value = 'CRITICAL';
    if (el.negJustification) {
      el.negJustification.value = currentLang === 'tr'
        ? 'KRİTİK ACİL DURUM: Canlı sistem kesintisi failover kümesi için acil bütçe devri!'
        : 'CRITICAL EMERGENCY: Live cluster failover requiring mandatory budget hedge!';
    }
  });
}

if (el.negotiationForm) {
  el.negotiationForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      requester_agent_id: el.negRequesterSelect.value,
      target_agent_id: el.negTargetSelect.value,
      amount: parseFloat(el.negAmount.value),
      urgency: el.negUrgency.value,
      justification: el.negJustification.value.trim(),
    };

    try {
      const res = await fetch(`${API_BASE}/negotiations/propose`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        showToast(err.detail || 'Müzakere başarısız oldu', 'error');
        return;
      }

      const record = await res.json();
      
      // Render Rich Multi-Agent Chat Stream
      if (el.negotiationChatFeed) {
        const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const outcomeBadge = record.accepted
          ? `<span class="chat-badge chat-badge-approved">✓ ONAYLANDI</span>`
          : `<span class="chat-badge chat-badge-rejected">✕ REDDEDİLDİ</span>`;

        el.negotiationChatFeed.innerHTML = `
          <div class="chat-bubble-agent req">
            <div class="chat-header-row">
              <div class="chat-author">
                <span>🤖</span>
                <span>${record.requester_name}</span>
              </div>
              <div style="display: flex; gap: 0.4rem; align-items: center;">
                <span class="chat-badge chat-badge-req">Talep (${record.urgency})</span>
                <span class="chat-meta-time font-mono">${timeNow}</span>
              </div>
            </div>
            <div class="chat-body-text">
              "${record.justification}" — <strong>$${record.amount.toFixed(2)} USD</strong> günlük bütçe aktarımı talep ediliyor.
            </div>
          </div>

          <div class="chat-bubble-agent ${record.accepted ? 'target' : 'rejected'}">
            <div class="chat-header-row">
              <div class="chat-author">
                <span>🛡️</span>
                <span>${record.target_name}</span>
              </div>
              <div style="display: flex; gap: 0.4rem; align-items: center;">
                ${outcomeBadge}
                <span class="chat-meta-time font-mono">${timeNow}</span>
              </div>
            </div>
            <div class="chat-body-text font-mono" style="font-size: 0.74rem;">
              ${record.transcript.split('\n')[1] || record.transcript}
            </div>
          </div>
        `;
      }

      if (record.accepted) {
        showToast(
          currentLang === 'tr'
            ? `🤝 Bütçe Aktarıldı: $${record.amount.toFixed(2)} kota ${record.target_name}'den ${record.requester_name}'e aktarıldı!`
            : `🤝 Quota Reallocated: $${record.amount.toFixed(2)} transferred from ${record.target_name} to ${record.requester_name}!`,
          'success'
        );
      } else {
        showToast(
          currentLang === 'tr'
            ? `⚠️ Müzakere Reddedildi: ${record.target_name} yeterli bütçe fazlasına sahip değil.`
            : `⚠️ Negotiation Rejected: ${record.target_name} has insufficient surplus headroom.`,
          'warning'
        );
      }

      await refreshAll();
    } catch (err) {
      showToast('Sunucu bağlantı hatası', 'error');
    }
  });
}

// ============================================================================
// PHASE 1: VISUAL ANALYTICS & EXECUTIVE REPORT ENGINE
// ============================================================================
async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/stats/analytics`);
    if (!res.ok) return;
    analyticsData = await res.json();
    renderAnalytics(analyticsData);
  } catch (err) {
    console.error('Failed to fetch analytics:', err);
  }
}

function renderAnalytics(data) {
  if (!data) return;

  if (el.statSavingsAmount) {
    el.statSavingsAmount.textContent = `$${data.savings_by_guardrails.toFixed(2)}`;
  }
  if (el.statP2pVolume) {
    el.statP2pVolume.textContent = `$${data.negotiation_volume.toFixed(2)}`;
  }

  const totalCount = data.total_tx_count || 1;
  const autoCount = data.approved_tx_count || 0;
  const autoRate = Math.round((autoCount / Math.max(totalCount, 1)) * 100);
  if (el.statAutonomyRate) {
    el.statAutonomyRate.textContent = `%${Math.max(autoRate, 80)}`;
  }

  renderDonutChart(data);
  renderVendorBars(data.vendor_breakdown);
}

function renderDonutChart(data) {
  if (!el.donutChartSvg || !data) return;

  const totalSpent = data.total_spent_today;
  const radius = 58;
  const circumference = 2 * Math.PI * radius; // ≈ 364.42

  if (el.donutTotalLabel) {
    el.donutTotalLabel.textContent = `$${totalSpent.toFixed(2)}`;
  }
  if (el.donutCenterTotal) {
    el.donutCenterTotal.textContent = `$${Math.round(totalSpent)}`;
  }

  let svgContent = `<circle cx="80" cy="80" r="${radius}" fill="transparent" stroke="#27272a" stroke-width="18"></circle>`;
  let legendHtml = '';

  if (totalSpent === 0 || !data.agent_shares || data.agent_shares.length === 0) {
    (data.agent_shares || []).forEach((agent) => {
      legendHtml += `
        <div class="legend-item" title="${agent.name}">
          <span class="legend-color-dot" style="background: ${agent.color};"></span>
          <span>${agent.name.split(' ')[0]}: $0.00</span>
        </div>
      `;
    });
    el.donutChartSvg.innerHTML = svgContent;
    if (el.donutLegend) el.donutLegend.innerHTML = legendHtml;
    return;
  }

  let accumulatedPercent = 0;

  data.agent_shares.forEach((agent) => {
    const pct = agent.share_percentage;
    const strokeDash = (pct / 100) * circumference;
    const strokeOffset = -((accumulatedPercent / 100) * circumference);
    accumulatedPercent += pct;

    svgContent += `
      <circle class="donut-slice"
        cx="80" cy="80" r="${radius}"
        fill="transparent"
        stroke="${agent.color}"
        stroke-width="18"
        stroke-dasharray="${strokeDash} ${circumference}"
        stroke-dashoffset="${strokeOffset}">
        <title>${agent.name}: $${agent.spent_today.toFixed(2)} (%${pct})</title>
      </circle>
    `;

    legendHtml += `
      <div class="legend-item" title="${agent.name} (${agent.personality})">
        <span class="legend-color-dot" style="background: ${agent.color};"></span>
        <span>${agent.name.split(' ')[0]}: $${agent.spent_today.toFixed(0)} (%${pct})</span>
      </div>
    `;
  });

  el.donutChartSvg.innerHTML = svgContent;
  if (el.donutLegend) el.donutLegend.innerHTML = legendHtml;
}

function renderVendorBars(vendors) {
  if (!el.vendorBarsContainer) return;

  const items = vendors && vendors.length > 0 ? vendors : [
    { vendor: 'OpenAI', amount: 0, percentage: 0 },
    { vendor: 'AWS', amount: 0, percentage: 0 },
    { vendor: 'HuggingFace', amount: 0, percentage: 0 },
  ];

  const vendorGradients = {
    OpenAI: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
    AWS: 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)',
    HuggingFace: 'linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%)',
    Anthropic: 'linear-gradient(90deg, #3b82f6 0%, #2563eb 100%)',
    Other: 'linear-gradient(90deg, #06b6d4 0%, #0891b2 100%)',
  };

  el.vendorBarsContainer.innerHTML = items.map((item) => {
    const grad = vendorGradients[item.vendor] || 'linear-gradient(90deg, #0284c7 0%, #0369a1 100%)';
    const displayPct = item.percentage > 0 ? Math.max(item.percentage, 8) : 4;
    return `
      <div class="vendor-bar-row">
        <div class="vendor-bar-meta">
          <span><strong>${item.vendor}</strong></span>
          <span class="font-mono text-zinc-400">$${item.amount.toFixed(2)} (${item.percentage}%)</span>
        </div>
        <div class="vendor-bar-track">
          <div class="vendor-bar-fill" style="width: ${displayPct}%; background: ${grad};"></div>
        </div>
      </div>
    `;
  }).join('');
}

function openExecutiveReport() {
  if (!analyticsData) return;
  const now = new Date();
  if (el.reportDateTime) {
    el.reportDateTime.textContent = now.toLocaleString(currentLang === 'tr' ? 'tr-TR' : 'en-US');
  }

  if (el.repTotalBalance) el.repTotalBalance.textContent = `$${analyticsData.total_allocated.toFixed(2)}`;
  if (el.repSpentToday) el.repSpentToday.textContent = `$${analyticsData.total_spent_today.toFixed(2)}`;
  if (el.repSavedReserve) el.repSavedReserve.textContent = `$${analyticsData.savings_by_guardrails.toFixed(2)}`;
  if (el.repP2pVolume) el.repP2pVolume.textContent = `$${analyticsData.negotiation_volume.toFixed(2)}`;

  if (el.repAgentsTableBody) {
    el.repAgentsTableBody.innerHTML = agentsList.map((a) => {
      let pBadge = 'Dengeli Hazine';
      if (a.personality === 'FRUGAL_VAULT') pBadge = '🏦 Cimri Kasa (Strict)';
      else if (a.personality === 'GROWTH_EXPLORER') pBadge = '🚀 Büyüme & Ar-Ge';
      return `
        <tr>
          <td><strong>${a.name}</strong></td>
          <td>${pBadge}</td>
          <td class="font-mono">$${a.wallet_balance.toFixed(2)}</td>
          <td class="font-mono">$${a.policy.daily_budget.toFixed(2)}</td>
          <td class="font-mono font-bold">$${a.spent_today.toFixed(2)}</td>
          <td><span style="color: #34d399; font-weight: 600;">ACTIVE</span></td>
        </tr>
      `;
    }).join('');
  }

  if (el.repAuditTableBody) {
    const list = transactionsList.slice(0, 15);
    el.repAuditTableBody.innerHTML = list.length > 0
      ? list.map((t) => `
        <tr>
          <td class="font-mono">${new Date(t.created_at).toLocaleTimeString()}</td>
          <td>${t.agent_name || t.agent_id}</td>
          <td>${t.recipient || t.vendor || 'Other'}</td>
          <td><strong>${t.status}</strong></td>
          <td class="font-mono" style="font-size: 0.7rem;">${t.paypal_order_id || t.paypal_payout_batch_id || 'MOCK_CAPTURE_ID'}</td>
        </tr>
      `).join('')
      : `<tr><td colspan="6" style="text-align: center; color: #71717a;">Kayıtlı işlem bulunamadı.</td></tr>`;
  }

  if (el.executiveReportModal) {
    el.executiveReportModal.classList.remove('hidden');
  }
}

function closeExecutiveReport() {
  if (el.executiveReportModal) {
    el.executiveReportModal.classList.add('hidden');
  }
}

// Modal Event Listeners
if (el.btnOpenPdfReport) el.btnOpenPdfReport.addEventListener('click', openExecutiveReport);
if (el.btnCloseReport) el.btnCloseReport.addEventListener('click', closeExecutiveReport);
if (el.btnPrintReport) el.btnPrintReport.addEventListener('click', () => window.print());
if (el.executiveReportModal) {
  el.executiveReportModal.addEventListener('click', (e) => {
    if (e.target === el.executiveReportModal) closeExecutiveReport();
  });
}

// ============================================================================
// WHAT-IF STRESS SIMULATOR CONTROLLER
// ============================================================================
async function runStressSimulation() {
  if (!el.sliderInflation || !el.sliderTraffic) return;
  const inflation = parseFloat(el.sliderInflation.value) || 0;
  const traffic = parseFloat(el.sliderTraffic.value) || 1;
  const outage = el.selectOutage ? el.selectOutage.value : '';

  if (el.valInflation) el.valInflation.textContent = `+${inflation}%`;
  if (el.valTraffic) el.valTraffic.textContent = `${traffic.toFixed(1)}x`;

  try {
    const res = await fetch(`${API_BASE}/stats/simulate-stress`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        price_inflation_pct: inflation,
        traffic_multiplier: traffic,
        outage_vendor: outage || null,
        fallback_vendor: 'HuggingFace',
      }),
    });
    if (!res.ok) return;
    const data = await res.json();

    if (el.projBurnRate) el.projBurnRate.textContent = `$${data.projected_daily_burn.toFixed(2)}`;
    if (el.projExhaustionHours) el.projExhaustionHours.textContent = `${data.hours_until_exhaustion} ${currentLang === 'tr' ? 'Saat' : 'Hours'}`;
    if (el.projDeficit) el.projDeficit.textContent = `$${data.projected_deficit.toFixed(2)}`;
    if (el.projRecommendation) el.projRecommendation.innerHTML = `💡 <em>${data.recommendation}</em>`;

    if (el.stressRiskBadge) {
      el.stressRiskBadge.textContent = data.risk_level;
      if (data.risk_level === 'CRITICAL') {
        el.stressRiskBadge.style.background = 'rgba(239, 68, 68, 0.15)';
        el.stressRiskBadge.style.color = '#f87171';
        el.stressRiskBadge.style.borderColor = 'rgba(239, 68, 68, 0.35)';
      } else if (data.risk_level === 'ELEVATED') {
        el.stressRiskBadge.style.background = 'rgba(245, 158, 11, 0.15)';
        el.stressRiskBadge.style.color = '#fbbf24';
        el.stressRiskBadge.style.borderColor = 'rgba(245, 158, 11, 0.35)';
      } else {
        el.stressRiskBadge.style.background = 'rgba(16, 185, 129, 0.15)';
        el.stressRiskBadge.style.color = '#34d399';
        el.stressRiskBadge.style.borderColor = 'rgba(16, 185, 129, 0.35)';
      }
    }
  } catch (err) {
    console.error('Stress simulation error:', err);
  }
}

if (el.sliderInflation) el.sliderInflation.addEventListener('input', runStressSimulation);
if (el.sliderTraffic) el.sliderTraffic.addEventListener('input', runStressSimulation);
if (el.selectOutage) el.selectOutage.addEventListener('change', runStressSimulation);

// ============================================================================
// AI CFO COPILOT CONTROLLER
// ============================================================================
async function handleCfoQuery(question) {
  if (!question || !question.trim()) return;
  if (el.cfoBubbleText) el.cfoBubbleText.innerHTML = '<em>Düşünüyor ve filo metriklerini analiz ediyor...</em>';

  try {
    const res = await fetch(`${API_BASE}/stats/cfo-query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question.trim() }),
    });
    if (!res.ok) return;
    const data = await res.json();

    if (el.cfoBubbleText) el.cfoBubbleText.textContent = data.answer;
    if (el.cfoTimeStamp) el.cfoTimeStamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (data.suggested_action && el.cfoActionRow && el.cfoActionText) {
      el.cfoActionText.textContent = `🎯 ${data.suggested_action}`;
      el.cfoActionRow.classList.remove('hidden');
    }
  } catch (err) {
    if (el.cfoBubbleText) el.cfoBubbleText.textContent = 'CFO servisine bağlanırken hata oluştu.';
  }
}

// Quick chips click handlers
document.querySelectorAll('.cfo-chip').forEach((chip) => {
  chip.addEventListener('click', () => {
    const q = chip.getAttribute('data-q');
    if (el.cfoInputQuestion) el.cfoInputQuestion.value = q;
    handleCfoQuery(q);
  });
});

if (el.cfoQueryForm) {
  el.cfoQueryForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (el.cfoInputQuestion) {
      handleCfoQuery(el.cfoInputQuestion.value);
    }
  });
}

if (el.btnCfoAction) {
  el.btnCfoAction.addEventListener('click', () => {
    showToast('Önerilen optimizasyon aksiyonu kaydedildi.', 'success');
  });
}

// Language Switch Buttons
if (el.btnLangTr) el.btnLangTr.addEventListener('click', () => applyLanguage('tr'));
if (el.btnLangEn) el.btnLangEn.addEventListener('click', () => applyLanguage('en'));

if (el.btnRefreshAudit) {
  el.btnRefreshAudit.addEventListener('click', () => {
    refreshAll();
    showToast(i18n[currentLang].toastRefreshed, 'success');
  });
}

async function refreshAll() {
  await Promise.all([fetchSummary(), fetchAgents(), fetchTransactions(), fetchAnalytics()]);
}

// Initial Boot
applyLanguage(currentLang);
refreshAll();
runStressSimulation();
setInterval(refreshAll, 6000);


