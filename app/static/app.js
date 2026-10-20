// Interactive Frontend Logic for Cisco Security AI Enablement Suite

let sourceDocsMap = {};

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initSourceDocs();
    initPipelineRunner();
    initCopyButtons();
    initVideoPreviewer();
    loadExistingStatus();
});

// Helper to render live outputs & metrics into DOM
function renderPipelineState(state) {
    const logBox = document.getElementById('pipeline-logs');
    const statusBadge = document.getElementById('system-status');

    if (state && state.logs && logBox) {
        logBox.innerHTML = '';
        state.logs.forEach((line, idx) => {
            const el = document.createElement('div');
            el.className = 'log-line ' + (idx === 0 ? 'info' : (idx === state.logs.length - 1 ? 'highlight' : 'success'));
            el.textContent = line;
            logBox.appendChild(el);
        });
        logBox.scrollTop = logBox.scrollHeight;
    }

    if (state && state.live_outputs && Object.keys(state.live_outputs).length > 0) {
        const lo = state.live_outputs;
        const metricTokens = document.getElementById('metric-tokens');
        const metricCost = document.getElementById('metric-cost');
        const metricSource = document.getElementById('metric-source-name');

        if (metricSource && lo.source_name) {
            metricSource.textContent = lo.source_name;
        }
        if (lo.usage) {
            if (metricTokens && lo.usage.total_tokens !== undefined) {
                metricTokens.textContent = `${lo.usage.total_tokens.toLocaleString()} tokens (${lo.usage.input_tokens} in / ${lo.usage.output_tokens} out)`;
            }
            if (metricCost && lo.usage.estimated_cost_usd !== undefined) {
                metricCost.textContent = `Costo real de esta corrida: $${lo.usage.estimated_cost_usd.toFixed(5)} USD`;
            }
        }

        const out1 = document.getElementById('live-out-agent1');
        const out2 = document.getElementById('live-out-agent2');
        const out3 = document.getElementById('live-out-agent3');
        const out4 = document.getElementById('live-out-agent4');
        if (out1 && lo.agent_1_ground_truth) out1.textContent = lo.agent_1_ground_truth;
        if (out2 && lo.agent_2_instructional_brief) out2.textContent = lo.agent_2_instructional_brief;
        if (out3 && lo.agent_3_video_script) out3.textContent = lo.agent_3_video_script;
        if (out4 && lo.agent_4_qa_report) out4.textContent = lo.agent_4_qa_report;

        if (statusBadge) {
            statusBadge.textContent = '● Pipeline Ejecutado en Vivo (Azure OpenAI)';
            statusBadge.style.color = '#34d399';
        }
    }
}

async function loadExistingStatus() {
    try {
        const res = await fetch('/api/status');
        const state = await res.json();
        renderPipelineState(state);
    } catch (err) {
        console.error('Error fetching initial status:', err);
    }
}

// Load Source Documents into Selector & Textarea
async function initSourceDocs() {
    const selector = document.getElementById('source-doc-selector');
    const textarea = document.getElementById('source-doc-textarea');
    const metricSource = document.getElementById('metric-source-name');

    if (!selector || !textarea) return;

    try {
        const res = await fetch('/api/source-docs');
        const data = await res.json();
        if (data.docs) {
            if (Array.isArray(data.docs)) {
                data.docs.forEach(doc => {
                    sourceDocsMap[doc.key] = doc.content;
                });
            } else {
                Object.entries(data.docs).forEach(([key, content]) => {
                    sourceDocsMap[key] = content;
                });
            }
            const defaultContent = sourceDocsMap[selector.value];
            if (defaultContent) {
                textarea.value = defaultContent;
                if (metricSource) metricSource.textContent = selector.value;
            }
        }
    } catch (err) {
        console.error('Error loading source docs:', err);
        textarea.value = '';
    }

    selector.addEventListener('change', () => {
        const key = selector.value;
        if (key === 'custom') {
            textarea.value = '';
            textarea.placeholder = 'Pega aquí cualquier nota de lanzamiento, guía de configuración o CLI de Cisco para que el Agente 1 la procese...';
            if (metricSource) metricSource.textContent = 'Documento Personalizado';
        } else if (sourceDocsMap[key]) {
            textarea.value = sourceDocsMap[key];
            if (metricSource) metricSource.textContent = key;
        }
    });
}

// Tab Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const pageTitle = document.getElementById('page-title');

    const titles = {
        'overview': 'Panel de Control: Cisco Security AI Content Suite',
        'pipeline': 'Arquitectura del Pipeline de Agentes (Azure OpenAI)',
        'script': 'Guion Técnico y Storyboard para Colossyan Studio',
        'simulator': 'Simulador de Escenarios: Caso Andes Freight',
        'architecture': 'Arquitectura de Red e Inspección (Cisco Secure Access)'
    };

    navItems.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;

            navItems.forEach(i => i.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPane = document.getElementById(`tab-${target}`);
            if (targetPane) targetPane.classList.add('active');

            if (pageTitle && titles[target]) {
                pageTitle.textContent = titles[target];
            }
        });
    });
}

// Pipeline Runner (Calls FastAPI backend with real source doc & Azure OpenAI)
function initPipelineRunner() {
    const btnRun = document.getElementById('btn-run-pipeline');
    const logBox = document.getElementById('pipeline-logs');
    const statusBadge = document.getElementById('system-status');
    const selector = document.getElementById('source-doc-selector');
    const textarea = document.getElementById('source-doc-textarea');

    if (!btnRun) return;

    btnRun.addEventListener('click', async () => {
        btnRun.disabled = true;
        btnRun.innerHTML = '<span class="btn-icon">⏳</span> Ejecutando 4 Agentes en Azure (15-25s)...';
        statusBadge.textContent = '● Consultando Azure gpt-5-mini en Vivo...';
        statusBadge.style.color = '#fbbf24';

        const selectedKey = selector ? selector.value : 'cisco_secure_access_source.md';
        const currentText = textarea ? textarea.value.trim() : '';
        const chkForceLive = document.getElementById('chk-force-live');
        const forceLive = chkForceLive ? chkForceLive.checked : false;

        if (logBox) {
            logBox.innerHTML = `
                <div class="log-line info">[00:00] Procesando documento "${selectedKey}" (${currentText.length} caracteres)...</div>
                <div class="log-line highlight">[00:01] ${forceLive ? 'Forzando llamada en vivo a Azure (reasoning=low, ahorro ~80%)...' : 'Verificando caché FinOps en disco ($0.00 si ya existe)...'}</div>
            `;
        }

        try {
            const res = await fetch('/api/run-pipeline', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_doc_key: selectedKey,
                    custom_source_text: currentText,
                    force_live: forceLive
                })
            });
            const data = await res.json();
            if (data.state) {
                renderPipelineState(data.state);
            }
        } catch (err) {
            console.error('Error running pipeline:', err);
            statusBadge.textContent = '● Error al ejecutar';
            statusBadge.style.color = '#f43f5e';
        } finally {
            btnRun.disabled = false;
            btnRun.innerHTML = '<span class="btn-icon">▶</span> Ejecutar Pipeline (Azure en Vivo)';
        }
    });
}

// Copy Buttons
function initCopyButtons() {
    const btnCopyScript = document.getElementById('btn-copy-script');
    if (btnCopyScript) {
        btnCopyScript.addEventListener('click', () => {
            const scriptText = `It's nine a.m. A developer pastes two hundred lines of proprietary code into a public AI assistant to fix a bug. No bad intent. But that code just left your organization.

This is Shadow AI: employees using GenAI apps that IT never approved. And traditional controls fall short. Blocking the category pushes users to personal devices. Pattern-only DLP misses context. And without decryption, you can't even see the prompt.

Cisco Secure Access turns GenAI governance into five steps: discover, decrypt, classify, enforce, and refine.

First, discover. AI Access shows which GenAI apps are in use across your organization, and how risky they are. You can't govern what you can't see.

Second, decrypt. Prompt inspection requires HTTPS inspection on the matching access policy. Skip this step, and every prompt is just encrypted traffic. It's a common misconfiguration.

Next, classify and enforce. In your DLP policy, add an AI Guardrails rule. It inspects prompts, responses, and file uploads for sensitive data and source code, then monitors or blocks the interaction.

Finally, refine. Start in Monitor mode. Baseline real usage, tune out false positives, then move to Block.

Shadow AI is a data-exposure problem. The answer isn't to block AI. It's to govern it. Now, let's put that into practice.`;

            navigator.clipboard.writeText(scriptText).then(() => {
                btnCopyScript.textContent = '¡Copiado al Portapapeles!';
                setTimeout(() => { btnCopyScript.textContent = '📋 Copiar Todo el Guion'; }, 2000);
            });
        });
    }
}

// Copy single scene voiceover text for Colossyan
function copySceneText(btn, text) {
    const originalLabel = btn.textContent;
    navigator.clipboard.writeText(text).then(() => {
        btn.textContent = '✅ ¡Locución Copiada!';
        setTimeout(() => { btn.textContent = originalLabel; }, 2000);
    });
}

// Local Bilingual Video Previewer (Tests MP4 with ES/EN subtitles before YouTube upload)
function initVideoPreviewer() {
    const fileInput = document.getElementById('local-video-input');
    const videoEl = document.getElementById('colossyan-preview-player');
    const wrapper = document.getElementById('video-preview-wrapper');
    const nameLabel = document.getElementById('loaded-video-name');

    if (!fileInput || !videoEl) return;

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const url = URL.createObjectURL(file);
        videoEl.src = url;
        if (wrapper) wrapper.style.display = 'block';
        if (nameLabel) {
            nameLabel.textContent = `✅ Cargado: ${file.name}`;
            nameLabel.style.color = '#10b981';
        }
        videoEl.onloadedmetadata = () => {
            setSubtitleTrack('es');
            videoEl.play().catch(() => {});
        };
    });
}

function setSubtitleTrack(lang) {
    const videoEl = document.getElementById('colossyan-preview-player');
    const btnEs = document.getElementById('btn-sub-es');
    const btnEn = document.getElementById('btn-sub-en');
    const btnOff = document.getElementById('btn-sub-off');

    [btnEs, btnEn, btnOff].forEach(b => {
        if (b) {
            b.style.borderColor = 'var(--border-glass)';
            b.style.color = 'var(--text-primary)';
        }
    });

    const activeBtn = lang === 'es' ? btnEs : (lang === 'en' ? btnEn : btnOff);
    if (activeBtn) {
        activeBtn.style.borderColor = 'var(--cisco-cyan)';
        activeBtn.style.color = 'var(--cisco-cyan)';
    }

    if (!videoEl || !videoEl.textTracks) return;
    for (let i = 0; i < videoEl.textTracks.length; i++) {
        const track = videoEl.textTracks[i];
        if (lang !== 'off' && track.language === lang) {
            track.mode = 'showing';
        } else {
            track.mode = 'disabled';
        }
    }
}

// Decision Simulator Submission
async function submitDecision(decisionId) {
    const selected = document.querySelector(`input[name="d${decisionId}"]:checked`);
    const feedbackBox = document.getElementById(`feedback-d${decisionId}`);

    if (!selected) {
        alert('Por favor selecciona una opción antes de enviar.');
        return;
    }

    try {
        const res = await fetch('/api/evaluate-decision', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                decision_id: decisionId,
                selected_option: selected.value
            })
        });
        const data = await res.json();

        feedbackBox.className = 'feedback-box show ' + (data.is_correct ? 'correct' : 'incorrect');
        feedbackBox.innerHTML = `<strong>${data.feedback}</strong>` + (data.consequence ? `<p style="margin-top:0.4rem;"><em>${data.consequence}</em></p>` : '') + (data.outcome ? `<p style="margin-top:0.4rem;"><em>${data.outcome}</em></p>` : '');

        if (decisionId === 1 && data.is_correct) {
            const card2 = document.getElementById('card-decision-2');
            card2.classList.remove('disabled');
        } else if (decisionId === 2 && data.is_correct) {
            feedbackBox.innerHTML += `<div style="margin-top:0.75rem; font-size:1.1rem; font-weight:700; color:#10b981;">🏅 ¡Insignia desbloqueada: Leak Stopper!</div>`;
        }
    } catch (err) {
        console.error('Error submitting decision:', err);
    }
}
