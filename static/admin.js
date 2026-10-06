const state = { config: null, providers: [] };

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
  return data;
}

function showAlert(message, type = 'success') {
  document.getElementById('alert-area').innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

function input(label, name, value, type = 'text') {
  const checked = type === 'checkbox' ? (value ? ' checked' : '') : '';
  const display = type === 'checkbox' ? `<div class="form-check form-switch"><input class="form-check-input" name="${name}" type="checkbox"${checked}><label class="form-check-label">${label}</label></div>` : `<label class="form-label">${label}</label><input class="form-control" name="${name}" type="${type}" value="${String(value ?? '').replaceAll('"', '&quot;')}">`;
  return `<div class="col-md-6">${display}</div>`;
}

function populateDynamicForm(formId, section, labels) {
  const form = document.querySelector(`[data-section="${section}"]`);
  const target = document.getElementById(formId);
  target.innerHTML = Object.entries(labels).map(([name, label]) => {
    const value = state.config[section][name];
    const type = typeof value === 'boolean' ? 'checkbox' : (typeof value === 'number' ? 'number' : 'text');
    return type === 'checkbox' ? input(label, name, value, type) : `<div class="col-md-6">${input(label, name, value, type)}</div>`;
  }).join('');
}

function populatePrompts() {
  const prompts = state.config.prompts;
  const labels = { system_prompt: 'System prompt', rag_prompt: 'RAG prompt', no_answer_prompt: 'No-answer prompt', greeting_prompt: 'Greeting prompt', context_instructions: 'Context instructions' };
  document.getElementById('prompt-form').innerHTML = Object.entries(labels).map(([name, label]) => `<div class="mb-3"><label class="form-label">${label} <span class="text-muted">${prompts[name].length} chars</span></label><textarea class="form-control" name="${name}" maxlength="20000">${prompts[name]}</textarea></div>`).join('') + '<button class="btn btn-primary save-section">Save prompts</button>';
}

function fillForms() {
  const modelForm = document.querySelector('[data-section="models"]');
  Object.entries(state.config.models).forEach(([name, value]) => { const el = modelForm.elements[name]; if (el) el.type === 'checkbox' ? el.checked = value : el.value = value; });
  populatePrompts();
  populateDynamicForm('rag-fields', 'rag', { vector_top_k: 'Vector top-k', bm25_top_k: 'BM25 top-k', final_top_k: 'Final top-k', similarity_threshold: 'Similarity threshold', chunk_size: 'Chunk size', chunk_overlap: 'Chunk overlap', retrieval_strategy: 'Retrieval strategy' });
  populateDynamicForm('performance-fields', 'performance', { cache_enabled: 'Cache enabled', semantic_cache_threshold: 'Semantic cache threshold', max_history_messages: 'Maximum history messages', max_history_chars: 'Maximum history characters', request_timeout: 'Request timeout' });
  populateDynamicForm('guardrail-fields', 'guardrails', { strict_rag_mode: 'Strict RAG mode', allow_general_questions: 'Allow general questions', hallucination_protection: 'Hallucination protection', minimum_retrieval_score: 'Minimum retrieval score', out_of_scope_response: 'Out-of-scope response' });
}

function serialize(form) {
  const result = {};
  Array.from(form.elements).filter(el => el.name).forEach(el => { result[el.name] = el.type === 'checkbox' ? el.checked : (el.type === 'number' ? Number(el.value) : el.value); });
  return result;
}

async function loadAll() {
  const [config, providersResponse] = await Promise.all([api('/admin/config'), api('/admin/providers')]);
  state.config = config;
  state.providers = providersResponse.providers || [];
  const providers = state.providers;
  ['primary_provider', 'fallback_provider'].forEach(name => { const select = document.querySelector(`[name="${name}"]`); select.innerHTML = name === 'fallback_provider' ? '<option value="">None</option>' : ''; providers.forEach(p => { select.insertAdjacentHTML('beforeend', `<option value="${p.id}">${p.name}</option>`); }); select.value = state.config.models[name]; });
  const modelSelect = document.querySelector('[name="primary_model"]'); const primary = providers.find(p => p.id === state.config.models.primary_provider); modelSelect.innerHTML = (primary?.models || []).map(m => `<option>${m}</option>`).join(''); modelSelect.value = state.config.models.primary_model;
  fillForms(); renderActive(); await refreshHealth();
}

function renderActive() { document.getElementById('active-config').innerHTML = `<div class="row"><div class="col-md-3"><strong>Model</strong><br>${state.config.models.primary_model}</div><div class="col-md-3"><strong>RAG</strong><br>Vector ${state.config.rag.vector_top_k} / BM25 ${state.config.rag.bm25_top_k} / Final ${state.config.rag.final_top_k}</div><div class="col-md-3"><strong>History</strong><br>${state.config.performance.max_history_messages} messages / ${state.config.performance.max_history_chars} chars</div><div class="col-md-3"><strong>Version</strong><br>${state.config.version}</div></div>`; }

async function refreshHealth() { const health = await api('/admin/health'); const cards = Object.entries(health).map(([name, item]) => `<div class="col-md-4 col-xl-2"><div class="card health-card"><div class="card-body"><div class="text-capitalize">${name.replaceAll('_', ' ')}</div><span class="badge text-bg-${item.status === 'healthy' ? 'success' : item.status === 'disabled' ? 'secondary' : 'warning'}">${item.status}</span><small class="d-block text-muted mt-2">${item.detail || ''}</small></div></div></div>`).join(''); document.getElementById('health-cards').innerHTML = cards; document.getElementById('header-status').textContent = Object.values(health).every(x => ['healthy', 'disabled'].includes(x.status)) ? 'System OK' : 'Attention needed'; }

document.addEventListener('click', async event => {
  const link = event.target.closest('.nav-link'); if (link) { document.querySelectorAll('.admin-section').forEach(s => s.classList.toggle('d-none', `#${s.id}` !== link.getAttribute('href'))); document.querySelectorAll('.nav-link').forEach(n => n.classList.toggle('active', n === link)); }
  if (event.target.closest('#refresh-btn')) { try { await loadAll(); showAlert('Control Center refreshed.'); } catch (e) { showAlert(e.message, 'danger'); } }
  const save = event.target.closest('.save-section'); if (save) { const form = save.closest('form'); try { state.config = await api('/admin/config', { method: 'PUT', body: JSON.stringify({ [form.dataset.section]: serialize(form) }) }); fillForms(); renderActive(); showAlert('Configuration saved and applied.'); } catch (e) { showAlert(e.message, 'danger'); } }
  if (event.target.closest('#test-btn')) { try { const result = await api('/admin/config/test', { method: 'POST', body: JSON.stringify({ question: document.getElementById('test-question').value }) }); document.getElementById('test-result').textContent = JSON.stringify(result, null, 2); } catch (e) { showAlert(e.message, 'danger'); } }
});

loadAll().catch(error => showAlert(error.message, 'danger'));
