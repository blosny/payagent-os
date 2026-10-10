/**
 * PayAgent OS — PayPal AI Toolkit & MCP Interceptor Module
 */

import { API_BASE, appState, el, showToast } from './state.js';

let refreshAllCallback = null;

export async function runMcpScenario(scenarioKey) {
  const terminalPre = document.getElementById('mcp-terminal-pre');
  const statusPill = document.getElementById('mcp-test-status-pill');
  const termTime = document.getElementById('mcp-term-time');

  if (statusPill) {
    statusPill.textContent = 'INTERCEPTING...';
    statusPill.style.color = '#38bdf8';
  }

  try {
    const res = await fetch(`${API_BASE}/toolkit/test-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: scenarioKey, agent_id: 'agent-devops' }),
    });

    const data = await res.json();
    if (termTime) termTime.textContent = new Date().toLocaleTimeString();

    if (terminalPre) {
      if (data.execution_trace && Array.isArray(data.execution_trace)) {
        const traceText = data.execution_trace.join('\n');
        const summaryJson = JSON.stringify(
          {
            guardian_verdict: data.guardian_verdict,
            status: data.status,
            transaction_id: data.transaction_id,
            paypal_order_id:
              (data.output_data && data.output_data.paypal_ref) ||
              data.paypal_order_id ||
              null,
            message: data.message,
          },
          null,
          2
        );
        terminalPre.textContent = `${traceText}\n\n--- [PAYAGENT OS GUARDIAN RESULT] ---\n${summaryJson}`;
      } else {
        terminalPre.textContent = JSON.stringify(data, null, 2);
      }
    }

    if (statusPill) {
      if (data.guardian_verdict === 'AUTONOMOUS_APPROVED') {
        statusPill.textContent = '✓ AUTONOMOUS APPROVED';
        statusPill.style.color = '#34d399';
        showToast(
          appState.currentLang === 'tr'
            ? 'MCP Sipariş onaylandı ve PayPal Sandbox Orders v2 üzerinden icra edildi!'
            : 'MCP Order approved and executed via PayPal Sandbox Orders v2!',
          'success'
        );
      } else if (data.guardian_verdict === 'HITL_HOLD_REQUIRED') {
        statusPill.textContent = '⚠ HITL HOLD (HALTED)';
        statusPill.style.color = '#f59e0b';
        showToast(
          appState.currentLang === 'tr'
            ? 'Limit aşımı! MCP çağrısı durduruldu ve İnsan Onay Kuyruğuna (HITL) iletildi.'
            : 'Limit exceeded! MCP tool call suspended and routed to HITL queue.',
          'warning'
        );
      } else if (data.guardian_verdict === 'BLOCKED_BY_POLICY') {
        statusPill.textContent = '✕ BLOCKED BY POLICY';
        statusPill.style.color = '#f43f5e';
        showToast(
          appState.currentLang === 'tr'
            ? 'Yetkisiz satıcı! MCP çağrısı kalkan tarafından engellendi.'
            : 'Unauthorized vendor! MCP tool blocked by policy.',
          'danger'
        );
      } else {
        statusPill.textContent = '✓ SAFE PASSTHROUGH';
        statusPill.style.color = '#38bdf8';
        showToast(
          appState.currentLang === 'tr'
            ? 'Salt okunur MCP çağrısı güvenle tamamlandı.'
            : 'Read-only MCP query finished safely.',
          'info'
        );
      }
    }

    // Refresh KPIs and transaction history
    if (refreshAllCallback) {
      await refreshAllCallback();
    }
  } catch (err) {
    if (terminalPre) terminalPre.textContent = JSON.stringify({ error: err.message }, null, 2);
    if (statusPill) statusPill.textContent = 'ERROR';
  }
}

export function initToolkitEvents(refreshCb) {
  refreshAllCallback = refreshCb;

  // Copy Code Snippet Listener
  if (el.btnCopyToolkitCode) {
    el.btnCopyToolkitCode.addEventListener('click', () => {
      const code = `from payagent_os import PolicyEngine, PayAgentGuardian
from paypal_ai_toolkit import PayPalAgentToolkit

# 1. PayPal resmi AI Toolkit'i başlat
toolkit = PayPalAgentToolkit(sandbox=True)

# 2. PayAgent OS kurumsal koruma kalkanını bağla (Drop-In Middleware)
guardian = PayAgentGuardian(
    policy_engine=PolicyEngine(max_per_tx=50.0, daily_limit=150.0),
    hitl_threshold=50.0,
    allowlist=["AWS", "OpenAI", "HuggingFace"]
)

# 3. Otonom yapay zeka ajanına güvenli cüzdan sağla
safe_tools = guardian.wrap_tools(toolkit.get_tools())`;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(code)
          .then(() => {
            showToast(
              appState.currentLang === 'tr'
                ? 'Entegrasyon Python kodu panoya kopyalandı!'
                : 'Integration Python snippet copied to clipboard!',
              'success'
            );
          })
          .catch(() => {
            showToast(
              appState.currentLang === 'tr' ? 'Kopyalama başarısız oldu.' : 'Failed to copy snippet.',
              'warning'
            );
          });
      } else {
        showToast(
          appState.currentLang === 'tr'
            ? 'Entegrasyon Python kodu seçildi.'
            : 'Integration snippet selected.',
          'info'
        );
      }
    });
  }

  // Interceptor test triggers
  const btnMcpSafe = document.getElementById('btn-mcp-safe');
  const btnMcpHitl = document.getElementById('btn-mcp-hitl');
  const btnMcpBlocked = document.getElementById('btn-mcp-blocked');
  const btnMcpReadonly = document.getElementById('btn-mcp-readonly');

  if (btnMcpSafe) btnMcpSafe.addEventListener('click', () => runMcpScenario('SAFE_PASS'));
  if (btnMcpHitl) btnMcpHitl.addEventListener('click', () => runMcpScenario('HITL_HOLD'));
  if (btnMcpBlocked) btnMcpBlocked.addEventListener('click', () => runMcpScenario('BLOCKED_VENDOR'));
  if (btnMcpReadonly) btnMcpReadonly.addEventListener('click', () => runMcpScenario('READONLY'));
}
