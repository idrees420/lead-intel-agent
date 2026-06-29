const elements = {
  researchForm: document.querySelector('#research-form'),
  companyName: document.querySelector('#company-name'),
  targetIndustry: document.querySelector('#target-industry'),
  targetRole: document.querySelector('#target-role'),
  maxAttempts: document.querySelector('#max-attempts'),
  attemptsVal: document.querySelector('#attempts-val'),
  
  researchBtnText: document.querySelector('#research-btn-text'),
  researchLoader: document.querySelector('#research-loader'),
  runResearchBtn: document.querySelector('#run-research-btn'),
  
  insightsGrid: document.querySelector('#insights-grid'),
  emptyState: document.querySelector('#empty-state'),
  summaryCard: document.querySelector('#summary-card'),
  notesCard: document.querySelector('#notes-card'),
  emailCard: document.querySelector('#email-card'),
  
  researchSummary: document.querySelector('#research-summary'),
  researchNotes: document.querySelector('#research-notes'),
  
  generateEmail: document.querySelector('#generate-email'),
  generateText: document.querySelector('#generate-text'),
  emailLoader: document.querySelector('#email-loader'),
  
  emailSubjectContainer: document.querySelector('#email-subject-container'),
  emailSubject: document.querySelector('#email-subject'),
  emailOutput: document.querySelector('#email-output'),
  
  recipientEmail: document.querySelector('#recipient-email'),
  sendSmtpEmail: document.querySelector('#send-smtp-email'),
  sendSmtpText: document.querySelector('#send-smtp-text'),
  sendSmtpLoader: document.querySelector('#send-smtp-loader'),
  emailActionsContainer: document.querySelector('#email-actions-container'),
  
  downloadReport: document.querySelector('#download-report'),
  sessionList: document.querySelector('#session-list'),
  refreshSessions: document.querySelector('#refresh-sessions'),
};

let currentSession = null;

const api = {
  research: '/api/research',
  email: '/api/email',
  sessions: '/api/sessions',
  session: (id) => `/api/session/${id}`,
};

// Update slider value display
if (elements.maxAttempts && elements.attemptsVal) {
  elements.maxAttempts.addEventListener('input', (e) => {
    elements.attemptsVal.textContent = e.target.value;
  });
}

// Toast Notifications
const showToast = (message, type = 'info') => {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let iconHtml = '';
  if (type === 'success') {
    iconHtml = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  } else if (type === 'error') {
    iconHtml = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  } else {
    iconHtml = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 16v-4M12 8h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }

  toast.innerHTML = `
    <div class="toast-icon">${iconHtml}</div>
    <div class="toast-message">${message}</div>
  `;
  
  container.appendChild(toast);
  
  // Trigger animation
  setTimeout(() => toast.classList.add('show'), 10);
  
  // Remove after 4s
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};

const formatDate = (dateString) => {
  const d = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', { 
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' 
  }).format(d);
};

const populateSessionCards = (sessions) => {
  elements.sessionList.innerHTML = '';
  if (!sessions.length) {
    elements.sessionList.innerHTML = `
      <div style="color: var(--text-tertiary); font-size: 0.85rem; text-align: center; margin-top: 20px;">
        No history available.
      </div>`;
    return;
  }

  sessions.forEach((session) => {
    const card = document.createElement('div');
    card.className = `session-card ${currentSession?.session_id === session.session_id ? 'active' : ''}`;
    
    // Status color class mapping
    let statusClass = 'status-research_complete';
    if (session.status === 'completed') statusClass = 'status-completed';
    if (session.status === 'failed') statusClass = 'status-failed';

    card.innerHTML = `
      <div class="session-header">
        <span class="session-title">${session.company_name}</span>
        <span class="status-badge ${statusClass}">${session.status.replace('_', ' ')}</span>
      </div>
      <div class="session-meta">
        ${session.target_industry || 'General Industry'} &bull; ${formatDate(session.updated_at)}
      </div>
    `;

    card.addEventListener('click', () => {
      document.querySelectorAll('.session-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      loadSession(session.session_id);
    });
    
    elements.sessionList.appendChild(card);
  });
};

const fetchSessions = async () => {
  try {
    const response = await fetch(api.sessions);
    if (!response.ok) throw new Error('Unable to load history.');
    const sessions = await response.json();
    populateSessionCards(sessions);
  } catch (error) {
    showToast(error.message, 'error');
  }
};

const renderMarkdown = (text) => {
  if (!text) return '';
  // Use marked.js if available, else simple replacement
  if (typeof marked !== 'undefined') {
    return marked.parse(text);
  }
  return text.replace(/\n/g, '<br>');
};

const showInsightsGrid = () => {
  elements.emptyState.style.display = 'none';
  elements.summaryCard.style.display = 'flex';
  elements.notesCard.style.display = 'flex';
  elements.emailCard.style.display = 'flex';
  elements.downloadReport.style.display = 'inline-flex';
  
  // Also remove hidden classes just in case
  elements.summaryCard.classList.remove('hidden');
  elements.notesCard.classList.remove('hidden');
  elements.emailCard.classList.remove('hidden');
  elements.downloadReport.classList.remove('hidden');
};

const renderSession = (session) => {
  currentSession = session;
  showInsightsGrid();

  // Populate form with session data
  elements.companyName.value = session.company_name || '';
  elements.targetIndustry.value = session.target_industry || '';

  // Render Research
  elements.researchSummary.innerHTML = renderMarkdown(session.research_summary || 'No summary available.');
  elements.researchNotes.innerHTML = renderMarkdown(session.research_notes || 'No notes available.');
  
  // Render Email
  if (session.email_draft) {
    elements.emailSubjectContainer.style.display = 'block';
    elements.emailSubjectContainer.classList.remove('hidden');
    elements.emailSubject.textContent = session.email_subject || 'No Subject';
    elements.emailOutput.innerHTML = renderMarkdown(session.email_draft);
    if(elements.emailActionsContainer) {
        elements.emailActionsContainer.style.display = 'block';
        elements.emailActionsContainer.classList.remove('hidden');
    }
  } else {
    elements.emailSubjectContainer.style.display = 'none';
    elements.emailOutput.innerHTML = '<p style="color: var(--text-tertiary)">Email has not been generated yet. Click "Generate Email" to draft outreach.</p>';
    if(elements.emailActionsContainer) elements.emailActionsContainer.style.display = 'none';
  }
};

const loadSession = async (sessionId) => {
  try {
    const response = await fetch(api.session(sessionId));
    if (!response.ok) throw new Error('Could not load session.');
    const data = await response.json();
    renderSession(data);
    showToast('Session loaded.', 'info');
  } catch (error) {
    showToast(error.message, 'error');
  }
};

const setLoadingState = (isLoading, context) => {
  if (context === 'research') {
    elements.runResearchBtn.disabled = isLoading;
    if (isLoading) {
      elements.researchBtnText.textContent = 'Scanning...';
      elements.researchLoader.classList.remove('hidden');
    } else {
      elements.researchBtnText.textContent = 'Run Intelligence Scan';
      elements.researchLoader.classList.add('hidden');
    }
  } else if (context === 'email') {
    elements.generateEmail.disabled = isLoading;
    if (isLoading) {
      elements.generateText.textContent = 'Drafting...';
      elements.emailLoader.classList.remove('hidden');
    } else {
      elements.generateText.textContent = 'Generate Email';
      elements.emailLoader.classList.add('hidden');
    }
  }
};

const handleResearchSubmit = async (event) => {
  event.preventDefault();
  
  const payload = {
    company_name: elements.companyName.value.trim(),
    target_industry: elements.targetIndustry.value.trim(),
    max_attempts: elements.maxAttempts.value,
  };

  if (!payload.company_name) return;

  setLoadingState(true, 'research');
  showInsightsGrid();
  
  // Loading skeleton content
  elements.researchSummary.innerHTML = '<div class="loader-spinner" style="border-top-color: var(--accent-primary-start);"></div><p style="margin-top:12px; color:var(--text-tertiary);">Gathering data streams...</p>';
  elements.researchNotes.innerHTML = '<div class="loader-spinner" style="border-top-color: var(--accent-success);"></div><p style="margin-top:12px; color:var(--text-tertiary);">Extracting key insights...</p>';
  elements.emailSubjectContainer.style.display = 'none';
  elements.emailOutput.innerHTML = '<p style="color: var(--text-tertiary)">Pending research completion...</p>';

  try {
    const response = await fetch(api.research, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) throw new Error(data.error || 'Scan failed.');

    renderSession(data);
    showToast('Intelligence scan complete.', 'success');
    await fetchSessions(); // update sidebar
  } catch (error) {
    showToast(error.message, 'error');
    elements.researchSummary.innerHTML = `<p style="color: var(--accent-error)">Scan failed: ${error.message}</p>`;
    elements.researchNotes.innerHTML = '';
  } finally {
    setLoadingState(false, 'research');
  }
};

const handleGenerateEmail = async () => {
  if (!currentSession || !currentSession.session_id) {
    showToast('Please run a scan first.', 'warning');
    return;
  }

  setLoadingState(true, 'email');
  elements.emailSubjectContainer.style.display = 'none';
  elements.emailOutput.innerHTML = '<div class="loader-spinner" style="border-top-color: var(--accent-primary-start);"></div><p style="margin-top:12px; color:var(--text-tertiary);">Drafting personalized outreach...</p>';

  try {
    const response = await fetch(api.email, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        session_id: currentSession.session_id, 
        target_role: elements.targetRole.value.trim() 
      }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Drafting failed.');

    currentSession = { ...currentSession, ...data, status: 'completed' };
    renderSession(currentSession);
    showToast('Email drafted successfully.', 'success');
    await fetchSessions();
  } catch (error) {
    showToast(error.message, 'error');
    elements.emailOutput.innerHTML = `<p style="color: var(--accent-error)">Failed: ${error.message}</p>`;
  } finally {
    setLoadingState(false, 'email');
  }
};

const handleSendSmtpEmail = async () => {
  if (!currentSession || !currentSession.session_id) return;
  const recipient = elements.recipientEmail.value.trim();
  if (!recipient) {
    showToast('Please enter a recipient email address.', 'warning');
    return;
  }

  elements.sendSmtpEmail.disabled = true;
  elements.sendSmtpText.textContent = 'Sending...';
  elements.sendSmtpLoader.classList.remove('hidden');

  try {
    const response = await fetch('/api/send_email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        session_id: currentSession.session_id, 
        recipient_email: recipient 
      }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Sending failed.');

    showToast('Email sent successfully!', 'success');
    elements.recipientEmail.value = '';
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    elements.sendSmtpEmail.disabled = false;
    elements.sendSmtpText.textContent = 'Send Now';
    elements.sendSmtpLoader.classList.add('hidden');
  }
};

const downloadReport = () => {
  if (!currentSession) return;

  const content = [
    `INTELLIGENCE REPORT: ${currentSession.company_name.toUpperCase()}`,
    `Generated: ${new Date().toLocaleString()}`,
    `Status: ${currentSession.status}`,
    '=========================================',
    '\n## RESEARCH SUMMARY',
    currentSession.research_summary || 'N/A',
    '\n## KEY NOTES',
    currentSession.research_notes || 'N/A',
    '\n=========================================',
    '\n## DRAFTED OUTREACH',
    `Subject: ${currentSession.email_subject || 'N/A'}`,
    '\n' + (currentSession.email_draft || 'N/A'),
  ].join('\n');

  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = `Intel_${currentSession.company_name.replace(/\s+/g, '_')}.md`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  
  showToast('Report exported successfully.', 'success');
};

// Event Listeners
elements.researchForm?.addEventListener('submit', handleResearchSubmit);
elements.generateEmail?.addEventListener('click', handleGenerateEmail);
elements.downloadReport?.addEventListener('click', downloadReport);
elements.refreshSessions?.addEventListener('click', fetchSessions);
elements.sendSmtpEmail?.addEventListener('click', handleSendSmtpEmail);

// Initial load
fetchSessions();
