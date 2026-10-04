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
  },
};

// Current Language (default: TR)
let currentLang = localStorage.getItem('payagent_lang') || 'tr';

// State
let agentsList = [];
let transactionsList = [];

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

    el.statAllocated.textContent = `$${data.total_allocated_funds.toFixed(2)}`;
    el.statSpentToday.textContent = `$${data.total_spent_today.toFixed(2)}`;
    el.statPending.textContent = data.pending_approval_count;
    el.statVolume.textContent = `$${data.total_volume_processed.toFixed(2)}`;
    
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

    card.innerHTML = `
      <div class="agent-card-top">
        <span class="agent-card-title">${agent.name}</span>
        <span class="agent-card-balance">$${agent.wallet_balance.toFixed(2)}</span>
      </div>

      <div class="budget-bar-wrap">
        <div class="budget-bar-labels">
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

// Render HITL Queue (Invoice style)
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
    const card = document.createElement('div');
    card.className = 'invoice-review-card';
    card.innerHTML = `
      <div class="invoice-header">
        <span class="invoice-agent">${tx.agent_name}</span>
        <span class="invoice-amount">$${tx.amount.toFixed(2)} ${tx.currency}</span>
      </div>
      <div class="invoice-flag">⚠️ ${tx.policy_evaluation_reason}</div>
      <div class="invoice-body">
        <strong>${currentLang === 'tr' ? 'Niyet / Gerekçe:' : 'Reasoning:'}</strong> ${tx.reasoning}
        <br><strong>${currentLang === 'tr' ? 'Alıcı:' : 'Payee:'}</strong> ${tx.recipient} (${tx.category})
      </div>
      <div class="invoice-footer">
        <button class="fin-btn fin-btn-sm fin-btn-reject" onclick="resolveHITL('${tx.id}', 'REJECT')">${i18n[currentLang].btnReject}</button>
        <button class="fin-btn fin-btn-sm fin-btn-approve" onclick="resolveHITL('${tx.id}', 'APPROVE')">${i18n[currentLang].btnAuthorize}</button>
      </div>
    `;
    el.hitlContainer.appendChild(card);
  });
}

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
      <td>${timeStr}</td>
      <td style="font-weight: 700; color: #ffffff;">${tx.agent_name}</td>
      <td style="font-weight: 800; color: #f8fafc;">$${tx.amount.toFixed(2)}</td>
      <td>${tx.recipient}</td>
      <td><span class="status-tag ${tagClass}">${statusText}</span></td>
      <td class="ref-code">${ref}</td>
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
    showToast(
      decision === 'APPROVE' ? i18n[currentLang].toastApproveSuccess : i18n[currentLang].toastRejectSuccess,
      decision === 'APPROVE' ? 'success' : 'warning'
    );
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

// Language Switch Buttons
el.btnLangTr.addEventListener('click', () => applyLanguage('tr'));
el.btnLangEn.addEventListener('click', () => applyLanguage('en'));

el.btnRefreshAudit.addEventListener('click', () => {
  refreshAll();
  showToast(i18n[currentLang].toastRefreshed, 'success');
});

async function refreshAll() {
  await Promise.all([fetchSummary(), fetchAgents(), fetchTransactions()]);
}

// Initial Boot
applyLanguage(currentLang);
refreshAll();
setInterval(refreshAll, 6000);
