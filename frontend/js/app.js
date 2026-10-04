/**
 * PayAgent OS — Frontend Dashboard Application
 * Connects to FastAPI backend (/api/v1) for metrics, agents, simulator, HITL, and audit logs.
 */

const API_BASE = '/api/v1';

// State
let agentsList = [];
let transactionsList = [];

// DOM Elements
const el = {
  paypalModeLabel: document.getElementById('paypal-mode-label'),
  valAllocated: document.getElementById('val-allocated'),
  valSpentToday: document.getElementById('val-spent-today'),
  valPending: document.getElementById('val-pending'),
  valVolume: document.getElementById('val-volume'),
  subActiveAgents: document.getElementById('sub-active-agents'),
  simAgentSelect: document.getElementById('sim-agent-select'),
  simAmount: document.getElementById('sim-amount'),
  simRecipient: document.getElementById('sim-recipient'),
  simCategory: document.getElementById('sim-category'),
  simReasoning: document.getElementById('sim-reasoning'),
  simulatorForm: document.getElementById('intent-simulator-form'),
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

// Toast Notifications
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : type === 'warning' ? '⚠️' : '✕'}</span> ${message}`;
  el.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Fetch Metrics & Summary
async function fetchSummary() {
  try {
    const res = await fetch(`${API_BASE}/stats/summary`);
    if (!res.ok) return;
    const data = await res.json();

    el.valAllocated.textContent = `$${data.total_allocated_funds.toFixed(2)}`;
    el.valSpentToday.textContent = `$${data.total_spent_today.toFixed(2)}`;
    el.valPending.textContent = data.pending_approval_count;
    el.valVolume.textContent = `$${data.total_volume_processed.toFixed(2)}`;
    el.subActiveAgents.textContent = `Across ${data.active_agents_count} active AI agents`;
    el.badgeHitlCount.textContent = `${data.pending_approval_count} Pending`;

    if (data.is_live_sandbox) {
      el.paypalModeLabel.textContent = 'PayPal Sandbox: Connected';
    } else {
      el.paypalModeLabel.textContent = 'PayPal Sandbox: Ready (Dev Simulation)';
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

    // Populate dropdown
    const currentVal = el.simAgentSelect.value;
    el.simAgentSelect.innerHTML = '';
    agentsList.forEach((agent) => {
      const opt = document.createElement('option');
      opt.value = agent.id;
      opt.textContent = `${agent.name} ($${agent.wallet_balance.toFixed(2)} available)`;
      el.simAgentSelect.appendChild(opt);
    });
    if (currentVal && agentsList.some((a) => a.id === currentVal)) {
      el.simAgentSelect.value = currentVal;
    }

    // Render Fleet Cards
    renderFleet();
  } catch (err) {
    console.error('Failed to fetch agents:', err);
  }
}

function renderFleet() {
  el.fleetContainer.innerHTML = '';
  agentsList.forEach((agent) => {
    const card = document.createElement('div');
    card.className = 'fleet-card';
    const vendorsHtml = agent.policy.allowed_vendors.length
      ? agent.policy.allowed_vendors.map((v) => `<span class="vendor-tag">${v}</span>`).join('')
      : '<span class="vendor-tag">All Vendors (Open Payout)</span>';

    card.innerHTML = `
      <div class="fleet-card-title">${agent.name}</div>
      <div class="fleet-card-balance">$${agent.wallet_balance.toFixed(2)}</div>
      <div class="fleet-limits">
        <span>Max Per Tx: <strong>$${agent.policy.max_per_transaction.toFixed(2)}</strong></span>
        <span>Daily Budget: <strong>$${agent.policy.daily_budget.toFixed(2)}</strong> (Spent: $${agent.spent_today.toFixed(2)})</span>
      </div>
      <div class="fleet-vendors">
        ${vendorsHtml}
      </div>
    `;
    el.fleetContainer.appendChild(card);
  });
}

// Fetch Transactions & HITL
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

function renderHITLQueue() {
  const pending = transactionsList.filter((t) => t.status === 'PENDING_APPROVAL');
  el.hitlContainer.innerHTML = '';

  if (pending.length === 0) {
    el.hitlContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">✓</div>
        <p>No transactions pending human review. All agents operating safely within policies.</p>
      </div>
    `;
    return;
  }

  pending.forEach((tx) => {
    const item = document.createElement('div');
    item.className = 'hitl-item';
    item.innerHTML = `
      <div class="hitl-top">
        <span class="hitl-agent-name">${tx.agent_name}</span>
        <span class="hitl-amount">$${tx.amount.toFixed(2)} ${tx.currency}</span>
      </div>
      <div class="hitl-policy-tag">⚠️ Flagged: ${tx.policy_evaluation_reason}</div>
      <div class="hitl-reason">
        <strong>Intent:</strong> ${tx.reasoning}
        <br><strong>Vendor:</strong> ${tx.recipient} (${tx.category})
      </div>
      <div class="hitl-actions">
        <button class="btn btn-sm btn-danger" onclick="resolveHITL('${tx.id}', 'REJECT')">✕ Reject</button>
        <button class="btn btn-sm btn-success" onclick="resolveHITL('${tx.id}', 'APPROVE')">✓ Authorize via PayPal</button>
      </div>
    `;
    el.hitlContainer.appendChild(item);
  });
}

function renderAuditTable() {
  el.auditTableBody.innerHTML = '';
  if (transactionsList.length === 0) {
    el.auditTableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">
          No transactions recorded yet. Use the simulator above to trigger an autonomous intent!
        </td>
      </tr>
    `;
    return;
  }

  transactionsList.slice(0, 15).forEach((tx) => {
    const tr = document.createElement('tr');
    const timeStr = new Date(tx.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    let badgeClass = 'badge-blue';
    let statusText = tx.status;
    if (tx.status === 'APPROVED_AUTONOMOUS') {
      badgeClass = 'badge-green';
      statusText = '⚡ Autonomous';
    } else if (tx.status === 'APPROVED_BY_HUMAN') {
      badgeClass = 'badge-green';
      statusText = '👤 Approved';
    } else if (tx.status === 'PENDING_APPROVAL') {
      badgeClass = 'badge-amber';
      statusText = '⏳ In Review';
    } else if (tx.status.includes('REJECTED')) {
      badgeClass = 'badge-rose';
      statusText = '✕ Rejected';
    }

    const ref = tx.paypal_order_id || tx.paypal_payout_batch_id || tx.id;

    tr.innerHTML = `
      <td>${timeStr}</td>
      <td style="font-weight: 600; color: var(--text-primary);">${tx.agent_name}</td>
      <td style="font-weight: 700; color: #f8fafc;">$${tx.amount.toFixed(2)}</td>
      <td>${tx.recipient}</td>
      <td><span class="badge ${badgeClass}">${statusText}</span></td>
      <td class="ref-cell">${ref}</td>
    `;
    el.auditTableBody.appendChild(tr);
  });
}

// Resolve Pending HITL Transaction
window.resolveHITL = async function (txId, decision) {
  try {
    const res = await fetch(`${API_BASE}/payments/${txId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, reviewer_notes: 'Reviewed by supervisor' }),
    });
    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || 'Failed to resolve transaction', 'error');
      return;
    }
    showToast(
      decision === 'APPROVE'
        ? `Payment authorized and captured via PayPal Sandbox!`
        : `Payment successfully rejected.`,
      decision === 'APPROVE' ? 'success' : 'warning'
    );
    await refreshAll();
  } catch (err) {
    showToast('Network error resolving transaction', 'error');
  }
};

// Submit Autonomous Simulator Intent
el.simulatorForm.addEventListener('submit', async (e) => {
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
      showToast(err.detail || 'Execution failed', 'error');
      return;
    }

    const record = await res.json();
    if (record.status === 'APPROVED_AUTONOMOUS') {
      showToast(`Autonomous payment executed! PayPal Ref: ${record.paypal_order_id || record.paypal_payout_batch_id}`, 'success');
    } else if (record.status === 'PENDING_APPROVAL') {
      showToast(`Policy Limit Exceeded: Moved to Human-in-the-Loop approval queue!`, 'warning');
    }

    await refreshAll();
  } catch (err) {
    showToast('Failed to connect to PayAgent server', 'error');
  }
});

// Quick Scenarios Buttons
el.chipPass.addEventListener('click', () => {
  el.simAgentSelect.value = 'agent-devops';
  el.simAmount.value = '15.00';
  el.simRecipient.value = 'AWS';
  el.simCategory.value = 'CLOUD_COMPUTE';
  el.simReasoning.value = 'Provisioning spot worker node for batch audio transcription.';
});

el.chipExceed.addEventListener('click', () => {
  el.simAgentSelect.value = 'agent-research';
  el.simAmount.value = '85.00';
  el.simRecipient.value = 'OpenAI';
  el.simCategory.value = 'API_QUOTA';
  el.simReasoning.value = 'High-volume embedding batch job for 50k research papers.';
});

el.chipUnauthorized.addEventListener('click', () => {
  el.simAgentSelect.value = 'agent-devops';
  el.simAmount.value = '25.00';
  el.simRecipient.value = 'UnknownCryptoHost';
  el.simCategory.value = 'CLOUD_COMPUTE';
  el.simReasoning.value = 'Attempting off-market compute procurement.';
});

el.btnRefreshAudit.addEventListener('click', () => {
  refreshAll();
  showToast('Dashboard metrics refreshed', 'success');
});

async function refreshAll() {
  await Promise.all([fetchSummary(), fetchAgents(), fetchTransactions()]);
}

// Initial Boot
refreshAll();
setInterval(refreshAll, 6000);
