// API URL - detecta automaticamente em produção
const API_URL = (() => {
    // Se estiver em produção (não localhost), usar mesmo domínio
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        // Se API estiver no mesmo domínio com /api
        return window.location.origin + '/api';
    }
    // Desenvolvimento local
    return 'http://localhost:8000';
})();

// Tab management
function openTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Update nav item active state
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach((item, index) => {
        const tabs = ['home', 'query', 'cqs', 'reasoner', 'metrics', 'about'];
        if (tabs[index] === tabName) {
            item.classList.add('active');
        }
    });
    
    // Load metrics if metrics tab is opened
    if (tabName === 'metrics') {
        loadMetrics();
    }
}

// Load metrics from API
async function loadMetrics() {
    try {
        const response = await fetch(`${API_URL}/metrics`);
        const metrics = await response.json();
        
        // Update ontology metrics
        document.getElementById('metric-classes').textContent = metrics.ontology.classes;
        document.getElementById('metric-properties').textContent = metrics.ontology.properties;
        document.getElementById('metric-cqs').textContent = `${metrics.ontology.cqs_passed}/${metrics.ontology.cqs_total}`;
        
        // Update RAG metrics
        document.getElementById('metric-docs').textContent = metrics.rag.documents_indexed;
        
        // Update agent metrics
        document.getElementById('metric-agents-total').textContent = metrics.agents.total_agents;
        
        // Update reasoner metrics
        document.getElementById('metric-classified').textContent = `${metrics.reasoner.classes_classified}/47`;
        document.getElementById('metric-realized').textContent = `${metrics.reasoner.individuals_realized}/10`;
        document.getElementById('metric-triples').textContent = `+${metrics.reasoner.triples_added}`;
        document.getElementById('metric-inference').textContent = `${metrics.reasoner.inference_rate}%`;
    } catch (error) {
        console.error('Erro ao carregar métricas:', error);
    }
}

// Query functions
function setQuery(text) {
    const input = document.getElementById('query-input');
    if (input) {
        input.value = text;
        input.focus();
        // Auto-resize
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
    }
}

function clearChat() {
    document.getElementById('chat-container').innerHTML = '';
}

async function sendQuery() {
    const query = document.getElementById('query-input').value.trim();
    if (!query) return;
    
    const chatContainer = document.getElementById('chat-container');
    
    // Add user message
    addMessage('user', query, 'Você');
    
    // Show loading
    const loadingId = addMessage('assistant', 'Analisando sua consulta e buscando informações relevantes...', 'Sistema', true);
    
    // Clear input
    document.getElementById('query-input').value = '';
    
    try {
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        // Remove loading
        document.getElementById(loadingId).remove();
        
        // Check for errors
        if (data.error) {
            addError(data.response || 'Erro ao processar consulta');
            return;
        }
        
        // Add response
        addMessage('assistant', data.response || data.answer || 'Sem resposta', data.agent || 'Sistema', false, data.citations);
        
    } catch (error) {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        addError('Erro ao processar consulta: ' + error.message);
        console.error('Error:', error);
    }
}

function addMessage(role, content, agent, isLoading = false, citations = null) {
    const chatContainer = document.getElementById('chat-container');
    const messageId = 'msg-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `message ${role}`;
    
    let html = `
        <div class="message-header">
            <span>${agent}</span>
            <span>${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="message-content">${isLoading ? '<div class="loading">⏳ Processando sua consulta</div>' : formatContent(content)}</div>
    `;
    
    if (citations && !isLoading) {
        html += formatCitations(citations);
    }
    
    messageDiv.innerHTML = html;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageId;
}

function formatContent(content) {
    // Simple formatting
    return content.replace(/\n/g, '<br>');
}

function formatCitations(citations) {
    if (!citations || (!citations.documents?.length && !citations.iris?.length)) {
        return '';
    }
    
    let html = '<div class="citations"><div class="citations-title">📚 Fontes e Referências</div>';
    
    if (citations.documents?.length > 0) {
        html += '<div style="margin-bottom: 12px;"><strong style="color: var(--primary); font-size: 0.9em;">Documentos:</strong></div>';
        citations.documents.forEach((doc, idx) => {
            const source = typeof doc === 'string' ? doc : (doc.source || doc.chunk || 'Documento');
            const score = doc.score ? ` <span style="color: var(--text-light); font-size: 0.85em;">(${(doc.score * 100).toFixed(1)}%)</span>` : '';
            html += `<div class="citation-item">📄 ${source}${score}</div>`;
        });
    }
    
    if (citations.iris?.length > 0) {
        html += '<div style="margin-top: 16px; margin-bottom: 12px;"><strong style="color: var(--primary); font-size: 0.9em;">IRIs da Ontologia:</strong></div>';
        citations.iris.forEach((iri, idx) => {
            const iriStr = typeof iri === 'string' ? iri : (iri.iri || iri);
            const shortIri = iriStr.length > 60 ? iriStr.substring(0, 60) + '...' : iriStr;
            html += `<div class="citation-item">🔗 <a href="${iriStr}" target="_blank" style="color: var(--primary); text-decoration: none;">${shortIri}</a></div>`;
        });
    }
    
    html += '</div>';
    return html;
}

function addError(message) {
    const chatContainer = document.getElementById('chat-container');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    chatContainer.appendChild(errorDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// CQ functions
function toggleCQ(cqNumber) {
    const resultContainer = document.getElementById(`cq-result-${cqNumber}`);
    if (resultContainer) {
        resultContainer.classList.toggle('expanded');
    }
}

async function runCQ(cqNumber) {
    const resultContainer = document.getElementById(`cq-result-${cqNumber}`);
    if (!resultContainer) return;
    
    resultContainer.innerHTML = '<div class="cq-loading">⏳ Executando CQ' + cqNumber + '...</div>';
    resultContainer.classList.add('expanded');
    
    // Scroll to result
    resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    try {
        const response = await fetch(`${API_URL}/cq/${cqNumber}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        displayCQResultInline(cqNumber, data);
    } catch (error) {
        resultContainer.innerHTML = `<div class="cq-error">❌ Erro ao executar CQ${cqNumber}: ${error.message}</div>`;
    }
}

function displayCQResultInline(cqNumber, data) {
    const resultContainer = document.getElementById(`cq-result-${cqNumber}`);
    if (!resultContainer) return;
    
    let html = '<div class="cq-result-content">';
    
    if (data.status === 'success') {
        html += '<div class="cq-result-header">';
        html += '<span class="cq-status-success">✅ Sucesso</span>';
        html += `<span class="cq-result-count">${data.results?.length || 0} resultado(s)</span>`;
        html += '</div>';
        
        if (data.results && data.results.length > 0) {
            html += '<div class="cq-result-items">';
            data.results.slice(0, 5).forEach((result, idx) => {
                html += '<div class="cq-result-item">';
                Object.entries(result).forEach(([key, value]) => {
                    html += `<div class="cq-result-field"><strong>${key}:</strong> ${value}</div>`;
                });
                html += '</div>';
            });
            if (data.results.length > 5) {
                html += `<div class="cq-result-more">... e mais ${data.results.length - 5} resultado(s)</div>`;
            }
            html += '</div>';
        } else {
            html += '<div class="cq-result-empty">Nenhum resultado encontrado.</div>';
        }
    } else {
        html += `<div class="cq-error">❌ ${data.error || 'Erro ao executar CQ'}</div>`;
    }
    
    html += '</div>';
    resultContainer.innerHTML = html;
}

async function runAllCQs() {
    // Execute all CQs sequentially
    for (let i = 1; i <= 10; i++) {
        await runCQ(i);
        // Small delay between executions
        await new Promise(resolve => setTimeout(resolve, 300));
    }
}

function displayCQResults(cqNumber, data) {
    const resultsContainer = document.getElementById('cqs-results');
    let html = `<div class="result-item"><h3>CQ${cqNumber} - Resultados</h3>`;
    
    if (data.results && data.results.length > 0) {
        html += '<ul>';
        data.results.forEach(result => {
            html += '<li>' + JSON.stringify(result) + '</li>';
        });
        html += '</ul>';
    } else {
        html += '<p>Nenhum resultado encontrado.</p>';
    }
    
    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayAllCQsResults(data) {
    const resultsContainer = document.getElementById('cqs-results');
    let html = '<h3>Todas as CQs</h3>';
    
    if (data.results) {
        Object.keys(data.results).forEach(cq => {
            html += `<div class="result-item"><h4>${cq}</h4><pre>${JSON.stringify(data.results[cq], null, 2)}</pre></div>`;
        });
    }
    
    resultsContainer.innerHTML = html;
}

// Reasoner functions
async function runClassification() {
    const resultsContainer = document.getElementById('reasoner-results');
    resultsContainer.innerHTML = '<div class="loading">Executando classificação...</div>';
    
    try {
        const response = await fetch(`${API_URL}/reasoner/classify`, {
            method: 'POST'
        });
        
        const data = await response.json();
        displayReasonerResults('Classificação', data);
    } catch (error) {
        resultsContainer.innerHTML = `<div class="error">Erro: ${error.message}</div>`;
    }
}

async function runConsistency() {
    const resultsContainer = document.getElementById('reasoner-results');
    resultsContainer.innerHTML = '<div class="loading">Verificando consistência...</div>';
    
    try {
        const response = await fetch(`${API_URL}/reasoner/consistency`, {
            method: 'POST'
        });
        
        const data = await response.json();
        displayReasonerResults('Consistência', data);
    } catch (error) {
        resultsContainer.innerHTML = `<div class="error">Erro: ${error.message}</div>`;
    }
}

async function runRealization() {
    const resultsContainer = document.getElementById('reasoner-results');
    resultsContainer.innerHTML = '<div class="loading">Executando realização...</div>';
    
    try {
        const response = await fetch(`${API_URL}/reasoner/realize`, {
            method: 'POST'
        });
        
        const data = await response.json();
        displayReasonerResults('Realização', data);
    } catch (error) {
        resultsContainer.innerHTML = `<div class="error">Erro: ${error.message}</div>`;
    }
}

async function runMaterialization() {
    const resultsContainer = document.getElementById('reasoner-results');
    resultsContainer.innerHTML = '<div class="loading">Executando materialização...</div>';
    
    try {
        const response = await fetch(`${API_URL}/reasoner/materialize`, {
            method: 'POST'
        });
        
        const data = await response.json();
        displayReasonerResults('Materialização', data);
    } catch (error) {
        resultsContainer.innerHTML = `<div class="error">Erro: ${error.message}</div>`;
    }
}

async function runAllReasoning() {
    const resultsContainer = document.getElementById('reasoner-results');
    resultsContainer.innerHTML = '<div class="loading">Executando todos os testes...</div>';
    
    try {
        const response = await fetch(`${API_URL}/reasoner/all`, {
            method: 'POST'
        });
        
        const data = await response.json();
        displayAllReasonerResults(data);
    } catch (error) {
        resultsContainer.innerHTML = `<div class="error">Erro: ${error.message}</div>`;
    }
}

function displayReasonerResults(title, data) {
    const resultsContainer = document.getElementById('reasoner-results');
    let html = `<div class="result-item"><h3>${title}</h3>`;
    html += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
    html += '</div>';
    resultsContainer.innerHTML = html;
}

function displayAllReasonerResults(data) {
    const resultsContainer = document.getElementById('reasoner-results');
    let html = '<h3>Todos os Resultados do Reasoner</h3>';
    html += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
    resultsContainer.innerHTML = html;
}

// Enter key to send query
document.getElementById('query-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
        sendQuery();
    }
});

