// ShadowChat Widget JavaScript
// Vanilla JS implementation that creates a floating chat button and panel.
// Sends user queries to the backend RAG API and displays responses.

(() => {
  const API_URL = "/api/chat"; // relative URL, works with dev server (localhost:8000) and can be overridden via data-api-url attribute

  // Helper to create DOM elements
  const el = (tag, attrs = {}, ...children) => {
    const element = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k.startsWith('on') && typeof v === 'function') {
        element.addEventListener(k.substring(2).toLowerCase(), v);
      } else if (k === 'class') {
        element.className = v;
      } else {
        element.setAttribute(k, v);
      }
    });
    children.forEach(child => {
      if (typeof child === 'string') {
        element.appendChild(document.createTextNode(child));
      } else if (child) {
        element.appendChild(child);
      }
    });
    return element;
  };

  // Build the widget elements
  const fab = el('div', { id: 'sc-fab', title: 'Chat with Shadow' }, '💬');
  const panel = el('div', { id: 'sc-panel' },
    el('div', { id: 'sc-header' }, 'ShadowChat'),
    el('div', { id: 'sc-messages' }),
    el('div', { id: 'sc-input-wrapper' },
      el('input', { id: 'sc-input', type: 'text', placeholder: 'Ask me something…' }),
      el('button', { id: 'sc-send' }, 'Send')
    )
  );

  // Insert into page
  document.body.appendChild(fab);
  document.body.appendChild(panel);

  // State
  let typing = false;

  const togglePanel = () => {
    panel.classList.toggle('open');
    if (panel.classList.contains('open')) {
      document.getElementById('sc-input').focus();
    }
  };

  const appendMessage = (text, sender = 'bot') => {
    const messages = document.getElementById('sc-messages');
    const msgEl = el('div', { class: `sc-msg ${sender}` },
      el('div', { class: 'sc-bubble' }, text)
    );
    messages.appendChild(msgEl);
    messages.scrollTop = messages.scrollHeight;
  };

  const showTyping = () => {
    const messages = document.getElementById('sc-messages');
    const typingEl = el('div', { class: 'sc-msg bot', id: 'sc-typing' },
      el('div', { class: 'sc-bubble' },
        el('div', { class: 'sc-typing' },
          el('span'), el('span'), el('span')
        )
      )
    );
    messages.appendChild(typingEl);
    messages.scrollTop = messages.scrollHeight;
    typing = true;
  };

  const hideTyping = () => {
    const typingEl = document.getElementById('sc-typing');
    if (typingEl) typingEl.remove();
    typing = false;
  };

  const sendMessage = async () => {
    const input = document.getElementById('sc-input');
    const question = input.value.trim();
    if (!question || typing) return;
    appendMessage(question, 'user');
    input.value = '';
    showTyping();
    try {
      const url = fab.dataset.apiUrl || API_URL; // allow overriding via data attribute on FAB
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await response.json();
      hideTyping();
      if (response.ok) {
        const answer = data.answer ?? 'Sorry, I could not answer that.';
        appendMessage(answer, 'bot');
      } else {
        const err = data.error || response.statusText;
        appendMessage(`⚠️ Error: ${err}`, 'bot');
      }
    } catch (e) {
      hideTyping();
      appendMessage(`⚠️ Network error: ${e.message}`, 'bot');
    }
  };

  // Event listeners
  fab.addEventListener('click', togglePanel);
  document.getElementById('sc-send').addEventListener('click', sendMessage);
  document.getElementById('sc-input').addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
  });
})();
