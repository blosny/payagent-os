/**
 * PayAgent OS — Visual Analytics, Stress Simulator & AI CFO Copilot Module
 */

import { API_BASE, appState, el, showToast } from './state.js';

export async function fetchAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/stats/analytics`);
    if (!res.ok) return;
    appState.analyticsData = await res.json();
    renderAnalytics(appState.analyticsData);
  } catch (err) {
    console.error('Failed to fetch analytics:', err);
  }
}

export function renderAnalytics(data) {
  if (!data) return;

  if (el.statSavingsAmount) {
    el.statSavingsAmount.textContent = `$${data.savings_by_guardrails.toFixed(2)}`;
  }
  if (el.statP2pVolume) {
    el.statP2pVolume.textContent = `$${data.negotiation_volume.toFixed(2)}`;
  }
  if (el.p2pDeskTradedVol) {
    el.p2pDeskTradedVol.textContent = `$${data.negotiation_volume.toFixed(2)}`;
  }

  if (el.statAutonomyRate) {
    if (!data.total_tx_count || data.total_tx_count === 0) {
      el.statAutonomyRate.textContent = '—';
    } else {
      const autoCount = data.approved_tx_count || 0;
      const autoRate = Math.round((autoCount / data.total_tx_count) * 100);
      el.statAutonomyRate.textContent = `%${autoRate}`;
    }
  }

  renderDonutChart(data);
  renderVendorBars(data.vendor_breakdown);

  const emptyHintEl = document.getElementById('charts-empty-hint');
  if (emptyHintEl) {
    if (!data.total_spent_today || data.total_spent_today === 0) {
      emptyHintEl.classList.remove('hidden');
    } else {
      emptyHintEl.classList.add('hidden');
    }
  }
}

export function renderDonutChart(data) {
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

export function renderVendorBars(vendors) {
  if (!el.vendorBarsContainer) return;

  const items =
    vendors && vendors.length > 0
      ? vendors
      : [
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

  el.vendorBarsContainer.innerHTML = items
    .map((item) => {
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
    })
    .join('');
}

export function openExecutiveReport() {
  if (!appState.analyticsData) return;
  const now = new Date();
  if (el.reportDateTime) {
    el.reportDateTime.textContent = now.toLocaleString(
      appState.currentLang === 'tr' ? 'tr-TR' : 'en-US'
    );
  }

  if (el.repTotalBalance)
    el.repTotalBalance.textContent = `$${appState.analyticsData.total_allocated.toFixed(2)}`;
  if (el.repSpentToday)
    el.repSpentToday.textContent = `$${appState.analyticsData.total_spent_today.toFixed(2)}`;
  if (el.repSavedReserve)
    el.repSavedReserve.textContent = `$${appState.analyticsData.savings_by_guardrails.toFixed(2)}`;
  if (el.repP2pVolume)
    el.repP2pVolume.textContent = `$${appState.analyticsData.negotiation_volume.toFixed(2)}`;

  if (el.repAgentsTableBody) {
    el.repAgentsTableBody.innerHTML = appState.agentsList
      .map((a) => {
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
      })
      .join('');
  }

  if (el.repAuditTableBody) {
    const list = appState.transactionsList.slice(0, 15);
    el.repAuditTableBody.innerHTML =
      list.length > 0
        ? list
            .map(
              (t) => `
        <tr>
          <td class="font-mono">${new Date(t.created_at).toLocaleTimeString()}</td>
          <td>${t.agent_name || t.agent_id}</td>
          <td>${t.recipient || t.vendor || 'Other'}</td>
          <td><strong>${t.status}</strong></td>
          <td class="font-mono" style="font-size: 0.7rem;">${
            t.paypal_order_id || t.paypal_payout_batch_id || 'MOCK_CAPTURE_ID'
          }</td>
        </tr>
      `
            )
            .join('')
        : `<tr><td colspan="6" style="text-align: center; color: #71717a;">Kayıtlı işlem bulunamadı.</td></tr>`;
  }

  if (el.executiveReportModal) {
    el.executiveReportModal.classList.remove('hidden');
  }
}

export function closeExecutiveReport() {
  if (el.executiveReportModal) {
    el.executiveReportModal.classList.add('hidden');
  }
}

export async function runStressSimulation() {
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
    if (el.projExhaustionHours)
      el.projExhaustionHours.textContent = `${data.hours_until_exhaustion} ${
        appState.currentLang === 'tr' ? 'Saat' : 'Hours'
      }`;
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

export async function handleCfoQuery(question) {
  if (!question || !question.trim()) return;
  if (el.cfoBubbleText)
    el.cfoBubbleText.innerHTML = '<em>Düşünüyor ve filo metriklerini analiz ediyor...</em>';

  try {
    const res = await fetch(`${API_BASE}/stats/cfo-query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question.trim() }),
    });
    if (!res.ok) return;
    const data = await res.json();

    if (el.cfoBubbleText) el.cfoBubbleText.textContent = data.answer;
    if (el.cfoTimeStamp)
      el.cfoTimeStamp.textContent = new Date().toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      });

    if (data.suggested_action && el.cfoActionRow && el.cfoActionText) {
      el.cfoActionText.textContent = `🎯 ${data.suggested_action}`;
      el.cfoActionRow.classList.remove('hidden');
    }
  } catch (err) {
    if (el.cfoBubbleText) el.cfoBubbleText.textContent = 'CFO servisine bağlanırken hata oluştu.';
  }
}

export function initAnalyticsEvents() {
  if (el.btnOpenPdfReport) el.btnOpenPdfReport.addEventListener('click', openExecutiveReport);
  if (el.btnCloseReport) el.btnCloseReport.addEventListener('click', closeExecutiveReport);
  if (el.btnPrintReport) el.btnPrintReport.addEventListener('click', () => window.print());
  if (el.executiveReportModal) {
    el.executiveReportModal.addEventListener('click', (e) => {
      if (e.target === el.executiveReportModal) closeExecutiveReport();
    });
  }

  if (el.sliderInflation) el.sliderInflation.addEventListener('input', runStressSimulation);
  if (el.sliderTraffic) el.sliderTraffic.addEventListener('input', runStressSimulation);
  if (el.selectOutage) el.selectOutage.addEventListener('change', runStressSimulation);

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
}
