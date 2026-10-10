/**
 * PayAgent OS — Autonomous Peer-to-Peer (P2P) Budget Negotiation & Debt Ledger Module
 */

import { API_BASE, appState, el, showToast } from './state.js';

let refreshAllCallback = null;

export async function fetchDebts() {
  const tbody = document.getElementById('debt-table-body');
  if (!tbody) return;

  try {
    const res = await fetch(`${API_BASE}/negotiations/debts`);
    if (!res.ok) return;
    const debts = await res.json();

    const activeDebts = debts ? debts.filter((d) => d.status !== 'SETTLED') : [];
    const btnRollover = document.getElementById('btn-trigger-rollover');
    if (btnRollover) {
      if (activeDebts.length === 0) {
        btnRollover.disabled = true;
        btnRollover.classList.add('btn-disabled-context');
        btnRollover.title =
          appState.currentLang === 'tr'
            ? 'Ödenecek aktif borç bulunmuyor'
            : 'No outstanding debts to settle';
      } else {
        btnRollover.disabled = false;
        btnRollover.classList.remove('btn-disabled-context');
        btnRollover.title = '';
      }
    }

    if (!debts || debts.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" class="empty-table-cell">
            Aktif borç kaydı bulunmuyor. Tüm ajanlar kendi bütçesi dahilinde veya borçsuz çalışıyor.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = debts
      .map((d) => {
        const isSettled = d.status === 'SETTLED';
        const statusBadge = isSettled
          ? `<span class="badge-approved" style="font-size: 0.65rem;">✓ SETTLED</span>`
          : `<span class="badge-pending" style="font-size: 0.65rem;">⏳ OUTSTANDING</span>`;

        const actionBtn = isSettled
          ? `<span style="font-size: 0.7rem; color: #10b981;">✓ Kapatıldı</span>`
          : `<button type="button" class="fin-btn fin-btn-secondary fin-btn-sm" style="padding: 0.25rem 0.6rem; font-size: 0.68rem;" onclick="settleSingleDebt('${d.id}')">
            <span>💸</span> Geri Öde
          </button>`;

        return `
        <tr>
          <td class="font-mono" style="font-size: 0.72rem; color: #38bdf8;">${d.id}</td>
          <td><strong>${d.debtor_name}</strong></td>
          <td>${d.creditor_name}</td>
          <td class="font-mono">$${d.principal_amount.toFixed(2)}</td>
          <td class="font-mono font-bold" style="color: ${
            isSettled ? '#10b981' : '#f59e0b'
          };">$${d.remaining_balance.toFixed(2)}</td>
          <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${
            d.reason
          }">${d.reason}</td>
          <td>${statusBadge}</td>
          <td>${actionBtn}</td>
        </tr>
      `;
      })
      .join('');
  } catch (err) {
    console.error('Error fetching debts:', err);
  }
}

export async function settleSingleDebt(debtId) {
  try {
    const res = await fetch(`${API_BASE}/negotiations/debts/settle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ debt_id: debtId }),
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Borç başarıyla kapatıldı.', 'success');
      if (refreshAllCallback) await refreshAllCallback();
    } else {
      showToast(data.detail || 'Borç ödenirken hata oluştu.', 'warning');
    }
  } catch (err) {
    showToast('Bağlantı hatası.', 'danger');
  }
}

// Bind to window for HTML onclick compatibility
window.settleSingleDebt = settleSingleDebt;

export function initP2PEvents(refreshCb) {
  refreshAllCallback = refreshCb;

  // Toggle drawer listener
  if (el.btnToggleNegotiation && el.negotiationContentBody) {
    el.btnToggleNegotiation.addEventListener('click', () => {
      const isHidden = el.negotiationContentBody.style.display === 'none';
      el.negotiationContentBody.style.display = isHidden ? 'block' : 'none';
      if (el.toggleIcon) {
        el.toggleIcon.textContent = isHidden ? '−' : '+';
      }
    });
  }

  // Preset chips
  const chipFrugalReject = document.getElementById('chip-preset-frugal-reject');
  const chipFrugalAccept = document.getElementById('chip-preset-frugal-accept');

  if (chipFrugalReject) {
    chipFrugalReject.addEventListener('click', () => {
      if (el.negRequesterSelect) el.negRequesterSelect.value = 'agent-research';
      if (el.negTargetSelect) el.negTargetSelect.value = 'agent-devops';
      if (el.negAmount) el.negAmount.value = '35.00';
      if (el.negUrgency) el.negUrgency.value = 'HIGH';
      if (el.negJustification) {
        el.negJustification.value =
          appState.currentLang === 'tr'
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
        el.negJustification.value =
          appState.currentLang === 'tr'
            ? 'KRİTİK ACİL DURUM: Canlı sistem kesintisi failover kümesi için acil bütçe devri!'
            : 'CRITICAL EMERGENCY: Live cluster failover requiring mandatory budget hedge!';
      }
    });
  }

  // Negotiation form submit
  if (el.negotiationForm) {
    el.negotiationForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('btn-submit-negotiation');
      const reqAgent = appState.agentsList.find((a) => a.id === el.negRequesterSelect.value);
      const targetAgent = appState.agentsList.find((a) => a.id === el.negTargetSelect.value);
      const reqName = reqAgent ? reqAgent.name : 'Requester Agent';
      const targetName = targetAgent ? targetAgent.name : 'Target Agent';

      const payload = {
        requester_agent_id: el.negRequesterSelect.value,
        target_agent_id: el.negTargetSelect.value,
        amount: parseFloat(el.negAmount.value),
        urgency: el.negUrgency.value,
        justification: el.negJustification.value.trim(),
      };

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>⏳</span> <span>Ajanlar Müzakere Ediyor...</span>';
      }

      if (el.negotiationChatFeed) {
        const timeNow = new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        });
        el.negotiationChatFeed.innerHTML = `
          <div class="chat-bubble-agent req">
            <div class="chat-header-row">
              <div class="chat-author">
                <span>🤖</span>
                <span>${reqName}</span>
              </div>
              <div style="display: flex; gap: 0.4rem; align-items: center;">
                <span class="chat-badge chat-badge-req">Talep (${payload.urgency})</span>
                <span class="chat-meta-time font-mono">${timeNow}</span>
              </div>
            </div>
            <div class="chat-body-text">
              "${payload.justification}" — <strong>$${payload.amount.toFixed(
          2
        )} USD</strong> günlük bütçe aktarımı talep ediliyor.
            </div>
          </div>

          <div class="thinking-bubble" id="p2p-thinking-indicator">
            <span>🧠</span>
            <span><strong>${targetName}</strong> politika kurallarını ve rezerv bütçesini değerlendiriyor...</span>
            <div class="thinking-dots">
              <span class="thinking-dot"></span>
              <span class="thinking-dot"></span>
              <span class="thinking-dot"></span>
            </div>
          </div>
        `;
      }

      try {
        const [res] = await Promise.all([
          fetch(`${API_BASE}/negotiations/propose`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
          }),
          new Promise((resolve) => setTimeout(resolve, 2000)),
        ]);

        if (!res.ok) {
          const err = await res.json();
          showToast(err.detail || 'Müzakere başarısız oldu', 'danger');
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<span>🤝</span> <span>Otonom Müzakereyi Başlat</span>';
          }
          return;
        }

        const record = await res.json();

        if (el.negotiationChatFeed) {
          const timeNow = new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          });
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
                "${record.justification}" — <strong>$${record.amount.toFixed(
            2
          )} USD</strong> günlük bütçe aktarımı talep ediliyor.
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
            appState.currentLang === 'tr'
              ? `🤝 Bütçe Aktarıldı: $${record.amount.toFixed(2)} kota ${record.target_name}'den ${
                  record.requester_name
                }'e aktarıldı ve borç defterine kaydedildi!`
              : `🤝 Quota Reallocated: $${record.amount.toFixed(2)} transferred from ${
                  record.target_name
                } to ${record.requester_name} and recorded in debt ledger!`,
            'success'
          );
        } else {
          const isFrugal = (record.transcript || '').includes('Cimri');
          showToast(
            isFrugal
              ? `🏦 Müzakere Reddedildi: ${record.target_name} (Cimri Kasa) rezervlerini korumak için ${record.urgency} talebini geri çevirdi.`
              : `⚠️ Müzakere Reddedildi: ${record.target_name} yeterli bütçe fazlasına sahip değil.`,
            'warning'
          );
        }

        if (refreshAllCallback) await refreshAllCallback();
      } catch (err) {
        showToast('Bağlantı hatası.', 'danger');
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<span>🤝</span> <span>Otonom Müzakereyi Başlat</span>';
        }
      }
    });
  }

  // Debt Rollover & Refresh buttons
  const btnTriggerRollover = document.getElementById('btn-trigger-rollover');
  if (btnTriggerRollover) {
    btnTriggerRollover.addEventListener('click', async () => {
      try {
        btnTriggerRollover.disabled = true;
        btnTriggerRollover.innerHTML = '<span>⏳</span> <span>Mutabakat Yapılıyor...</span>';

        const res = await fetch(`${API_BASE}/negotiations/debts/rollover`, { method: 'POST' });
        const data = await res.json();

        showToast(data.message || 'Gün sonu devri ve borç mutabakatı tamamlandı!', 'success');
        if (refreshAllCallback) await refreshAllCallback();
      } catch (err) {
        showToast('Rollover sırasında hata oluştu.', 'danger');
      } finally {
        btnTriggerRollover.disabled = false;
        btnTriggerRollover.innerHTML =
          '<span>⚡</span> <span>24h Kota Yenile & Otonom Borçları Kapat</span>';
      }
    });
  }

  const btnRefreshDebts = document.getElementById('btn-refresh-debts');
  if (btnRefreshDebts) {
    btnRefreshDebts.addEventListener('click', () => {
      fetchDebts();
      showToast('Borç defteri güncellendi.', 'info');
    });
  }
}
