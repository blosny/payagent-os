/**
 * PayAgent OS — Spot Arbitrage & Dynamic Bidding Desk Module
 */

import { API_BASE, appState, showToast } from './state.js';

let refreshAllCallback = null;

export async function fetchSpotRates() {
  try {
    const res = await fetch(`${API_BASE}/arbitrage/rates`);
    if (!res.ok) return;
    const data = await res.json();

    const savedValEl = document.getElementById('arb-total-saved-val');
    const auctionsCountEl = document.getElementById('arb-auctions-count');
    const gridEl = document.getElementById('spot-categories-grid');

    if (savedValEl) savedValEl.textContent = data.total_arbitrage_saved.toFixed(2);
    if (auctionsCountEl) {
      auctionsCountEl.textContent = `${data.total_auctions_conducted} ${
        appState.currentLang === 'tr' ? 'Otonom İhale İcra Edildi' : 'Auctions Executed'
      }`;
    }

    if (gridEl && data.spot_board) {
      gridEl.innerHTML = '';
      const catLabels = {
        gpu_inference: appState.currentLang === 'tr' ? 'GPU Çıkarımı (Inference)' : 'GPU Inference',
        model_fine_tuning: appState.currentLang === 'tr' ? 'Model Fine-Tuning' : 'Model Fine-Tuning',
        bulk_embeddings: appState.currentLang === 'tr' ? 'Toplu Gömme (Embeddings)' : 'Bulk Embeddings',
        serverless_compute: appState.currentLang === 'tr' ? 'Serverless Compute' : 'Serverless Compute',
      };

      Object.entries(data.spot_board).forEach(([catKey, vendors]) => {
        const catCard = document.createElement('div');
        catCard.className = 'spot-cat-card';

        const catTitle = catLabels[catKey] || catKey;
        const ratesHtml = vendors
          .map(
            (v) => `
          <div class="spot-rate-item">
            <span class="spot-vendor-name">${v.vendor_name.split(' ')[0]}</span>
            <span class="spot-rate-val font-mono">$${v.current_rate.toFixed(2)} <span style="font-size:0.6rem;color:#71717a;">${v.unit_label}</span></span>
          </div>
        `
          )
          .join('');

        catCard.innerHTML = `
          <div class="spot-cat-header">${catTitle}</div>
          <div class="spot-rates-list">${ratesHtml}</div>
        `;
        gridEl.appendChild(catCard);
      });
    }
  } catch (err) {
    console.error('Failed to fetch spot rates:', err);
  }
}

export async function fetchArbitrageHistory() {
  try {
    const res = await fetch(`${API_BASE}/arbitrage/history`);
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.getElementById('arb-history-table-body');
    if (!tbody) return;

    if (!data.executions || data.executions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:#71717a;padding:1.5rem;">${
        appState.currentLang === 'tr'
          ? 'Henüz spot ihale kaydı yok. Yukarıdaki formdan bir ihale başlatabilirsiniz.'
          : 'No spot bidding records yet.'
      }</td></tr>`;
      return;
    }

    tbody.innerHTML = '';
    data.executions.forEach((exec) => {
      const tr = document.createElement('tr');
      const timeStr = new Date(exec.executed_at).toLocaleTimeString();
      tr.innerHTML = `
        <td class="font-mono text-xs">${timeStr}</td>
        <td><strong>${exec.agent_name}</strong></td>
        <td><span class="font-mono" style="color:#38bdf8;">${exec.vendor_name}</span></td>
        <td class="font-mono">$${exec.amount_paid.toFixed(2)}</td>
        <td class="font-mono" style="color:#34d399;font-weight:700;">+$${exec.arbitrage_saved.toFixed(2)} (%${exec.savings_percentage})</td>
        <td class="font-mono text-xs text-slate-400">${exec.paypal_order_id || 'COMPLETED'}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Failed to fetch arbitrage history:', err);
  }
}

export async function solicitBids() {
  const agentId = document.getElementById('bid-agent-select')?.value || 'agent-devops';
  const workloadType = document.getElementById('bid-workload-select')?.value || 'gpu_inference';
  const units = parseFloat(document.getElementById('bid-units-input')?.value || '3.5');
  const strategy = document.getElementById('bid-strategy-select')?.value || 'COST_FIRST';
  const desc = document.getElementById('bid-desc-input')?.value || 'GPU compute';

  const btnSolicit = document.getElementById('btn-solicit-bids');
  const badge = document.getElementById('auction-status-badge');
  const emptyState = document.getElementById('auction-empty-state');
  const activeContent = document.getElementById('auction-active-content');

  if (btnSolicit) {
    btnSolicit.disabled = true;
    btnSolicit.innerHTML = '<span>⏳</span> <span>Teklifler Toplanıyor...</span>';
  }
  if (badge) {
    badge.textContent = 'YARIŞIYOR...';
    badge.style.color = '#38bdf8';
  }

  try {
    const res = await fetch(`${API_BASE}/arbitrage/bids/solicit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        requesting_agent_id: agentId,
        workload_type: workloadType,
        workload_description: desc,
        units_required: units,
        strategy: strategy,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || 'İhale başlatılamadı.', 'danger');
      return;
    }

    const data = await res.json();
    appState.currentBiddingResult = data;

    if (emptyState) emptyState.classList.add('hidden');
    if (activeContent) activeContent.classList.remove('hidden');

    // Alpha banner
    const savedSumEl = document.getElementById('alpha-saved-sum');
    const savedPctEl = document.getElementById('alpha-saved-pct');
    const bannerDescEl = document.getElementById('alpha-banner-desc');
    if (savedSumEl) savedSumEl.textContent = `$${data.arbitrage_saved_amount.toFixed(2)}`;
    if (savedPctEl) savedPctEl.textContent = `(%${data.savings_percentage} Tasarruf)`;
    if (bannerDescEl) {
      bannerDescEl.textContent = `En pahalı teklif veren (${data.highest_quote.vendor_name} @ $${data.highest_quote.total_price.toFixed(2)}) ile kazanan arasındaki net alpha.`;
    }

    // Quotes grid
    const quotesGrid = document.getElementById('quotes-grid');
    if (quotesGrid && data.quotes) {
      quotesGrid.innerHTML = '';
      data.quotes.forEach((q) => {
        const isWinner = q.vendor_id === data.winning_quote.vendor_id;
        const card = document.createElement('div');
        card.className = `quote-item-card ${isWinner ? 'is-winner' : ''}`;
        card.innerHTML = `
          ${isWinner ? '<span class="winner-badge">🏆 KAZANAN TEKLİF</span>' : ''}
          <div class="quote-vendor-name">${q.vendor_name}</div>
          <div class="quote-price-wrap">
            <span class="quote-total-price font-mono">$${q.total_price.toFixed(2)}</span>
            <span class="quote-unit-price font-mono">($${q.unit_price.toFixed(2)}${q.unit_label})</span>
          </div>
          <div class="quote-meta-row font-mono">
            <span>Gecikme: ${q.latency_ms}ms</span>
            <span>SLA: %${(q.reliability_sla * 100).toFixed(1)}</span>
          </div>
        `;
        quotesGrid.appendChild(card);
      });
    }

    // Rationale
    const rationaleEl = document.getElementById('rationale-text');
    if (rationaleEl) rationaleEl.textContent = data.decision_rationale;

    // Reset execute button & receipt box
    const btnExec = document.getElementById('btn-execute-winning-bid');
    const receiptBox = document.getElementById('exec-receipt-box');
    if (btnExec) {
      btnExec.disabled = false;
      btnExec.innerHTML = `<span>💳</span> <span>${data.winning_quote.vendor_name} Teklifini PayPal ($${data.winning_quote.total_price.toFixed(2)}) İle Otonom Satın Al</span>`;
    }
    if (receiptBox) {
      receiptBox.classList.add('hidden');
      receiptBox.innerHTML = '';
    }

    if (badge) {
      badge.textContent = 'KAZANAN SEÇİLDİ';
      badge.style.color = '#34d399';
    }

    showToast(
      `İhale sonuçlandı! En ucuz sağlayıcı (${data.winning_quote.vendor_name}) $${data.arbitrage_saved_amount.toFixed(2)} tasarrufla kazandı.`,
      'success'
    );
  } catch (err) {
    showToast(err.message, 'danger');
  } finally {
    if (btnSolicit) {
      btnSolicit.disabled = false;
      btnSolicit.innerHTML = '<span>🚀</span> <span>Canlı İhaleyi Başlat & Teklifleri Topla</span>';
    }
  }
}

export async function executeWinningBid() {
  if (!appState.currentBiddingResult) return;

  const btnExec = document.getElementById('btn-execute-winning-bid');
  const receiptBox = document.getElementById('exec-receipt-box');

  if (btnExec) {
    btnExec.disabled = true;
    btnExec.innerHTML = '<span>⏳</span> <span>PayPal Orders v2 Tahsil Ediliyor...</span>';
  }

  try {
    const res = await fetch(`${API_BASE}/arbitrage/bids/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bidding_id: appState.currentBiddingResult.bidding_id }),
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || 'PayPal siparişi oluşturulamadı.', 'danger');
      if (btnExec) btnExec.disabled = false;
      return;
    }

    const data = await res.json();

    if (receiptBox) {
      receiptBox.classList.remove('hidden');
      receiptBox.innerHTML = `
        <div style="font-weight:700;margin-bottom:0.35rem;color:#ffffff;">✓ OTONOM SATIN ALMA & TAHSİLAT BAŞARILI</div>
        <div>PayPal Sipariş ID: <strong>${data.paypal_order_id}</strong> (${data.paypal_status})</div>
        <div>Sağlayıcı: <strong>${data.vendor_name}</strong> | Ödenen Tutar: <strong>$${data.amount_paid.toFixed(2)} USD</strong></div>
        <div style="color:#34d399;margin-top:0.25rem;">🎉 Doğrudan Hazineye Aktarılan Arbitraj Kârı: <strong>+$${data.arbitrage_saved.toFixed(2)} USD</strong> (%${data.savings_percentage})</div>
      `;
    }

    if (btnExec) {
      btnExec.disabled = true;
      btnExec.innerHTML = '<span>✓</span> <span>Satın Alma Tamamlandı</span>';
    }

    showToast(
      `PayPal Orders v2 tamamlandı! +$${data.arbitrage_saved.toFixed(2)} tasarruf hazineye mühürlendi.`,
      'success'
    );

    if (refreshAllCallback) await refreshAllCallback();
  } catch (err) {
    showToast(err.message, 'danger');
    if (btnExec) btnExec.disabled = false;
  }
}

export async function runRebalanceLiquidity() {
  const btn = document.getElementById('btn-run-rebalance');
  const msg = document.getElementById('rebalance-status-msg');

  if (btn) btn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/arbitrage/rebalance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from_agent_id: 'agent-devops',
        to_agent_id: 'agent-research',
        amount: 35.0,
        reason: 'Gündüz kalan atıl DevOps altyapı bütçesi gece model eğitimine devredildi.',
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      showToast(err.detail || 'Dengeleme başarısız.', 'danger');
      return;
    }

    const data = await res.json();
    if (msg) {
      msg.classList.remove('hidden');
      msg.textContent = `✓ ${data.message}`;
    }
    showToast(
      `Likidite dengelendi: $${data.amount_rebalanced.toFixed(2)} DevOps'tan Araştırma'ya aktarıldı.`,
      'success'
    );

    if (refreshAllCallback) await refreshAllCallback();
  } catch (err) {
    showToast(err.message, 'danger');
  } finally {
    if (btn) btn.disabled = false;
  }
}

export function initArbitrageEvents(refreshCb) {
  refreshAllCallback = refreshCb;

  const btnRefreshSpotRates = document.getElementById('btn-refresh-spot-rates');
  const btnSolicitBids = document.getElementById('btn-solicit-bids');
  const btnExecuteWinningBid = document.getElementById('btn-execute-winning-bid');
  const btnRunRebalance = document.getElementById('btn-run-rebalance');

  if (btnRefreshSpotRates) {
    btnRefreshSpotRates.addEventListener('click', () => {
      fetchSpotRates();
      showToast(
        appState.currentLang === 'tr' ? 'Spot piyasa oranları güncellendi.' : 'Spot rates refreshed.',
        'info'
      );
    });
  }

  if (btnSolicitBids) {
    btnSolicitBids.addEventListener('click', solicitBids);
  }

  if (btnExecuteWinningBid) {
    btnExecuteWinningBid.addEventListener('click', executeWinningBid);
  }

  if (btnRunRebalance) {
    btnRunRebalance.addEventListener('click', runRebalanceLiquidity);
  }

  // Preset Chips
  const chipBidGpu = document.getElementById('chip-bid-gpu');
  const chipBidEmbed = document.getElementById('chip-bid-embed');
  const chipBidTrain = document.getElementById('chip-bid-train');

  if (chipBidGpu) {
    chipBidGpu.addEventListener('click', () => {
      document.getElementById('bid-workload-select').value = 'gpu_inference';
      document.getElementById('bid-units-input').value = '3.5';
      document.getElementById('bid-strategy-select').value = 'COST_FIRST';
      document.getElementById('bid-desc-input').value =
        'Llama-3-70B model çıkarımı için RunPod/AWS spot GPU kümesi kiralama.';
      document.getElementById('bid-unit-hint').textContent = 'GPU-Saat';
      showToast('Örnek GPU Spot senaryosu yüklendi.', 'info');
    });
  }

  if (chipBidEmbed) {
    chipBidEmbed.addEventListener('click', () => {
      document.getElementById('bid-workload-select').value = 'bulk_embeddings';
      document.getElementById('bid-units-input').value = '10.0';
      document.getElementById('bid-strategy-select').value = 'SPEED_FIRST';
      document.getElementById('bid-desc-input').value =
        'Acil 10M token vektör veri tabanı embedding indeksleme pipeline.';
      document.getElementById('bid-unit-hint').textContent = '1M Token';
      showToast('Örnek Toplu Gömme senaryosu yüklendi.', 'info');
    });
  }

  if (chipBidTrain) {
    chipBidTrain.addEventListener('click', () => {
      document.getElementById('bid-workload-select').value = 'model_fine_tuning';
      document.getElementById('bid-units-input').value = '2.0';
      document.getElementById('bid-strategy-select').value = 'BALANCED';
      document.getElementById('bid-desc-input').value =
        '8x H100 SXM5 / p4de kümesinde LoRA fine-tuning eğitimi.';
      document.getElementById('bid-unit-hint').textContent = 'Küme-Saat';
      showToast('Örnek H100 Fine-Tune senaryosu yüklendi.', 'info');
    });
  }
}
