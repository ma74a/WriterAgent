// WriterAgent Frontend Application Logic with VS Code Theme & Fit-to-Screen Layout
document.addEventListener('DOMContentLoaded', () => {
  
  // State
  let activeBlog = null;

  // DOM Element References
  const healthBadge = document.getElementById('health-badge');
  const healthText = document.getElementById('health-text');
  const historyList = document.getElementById('history-list');
  const btnRefreshHistory = document.getElementById('btn-refresh-history');
  
  const promptInput = document.getElementById('prompt-input');
  const streamToggle = document.getElementById('stream-toggle');
  const btnGenerate = document.getElementById('btn-generate');
  
  const streamTerminal = document.getElementById('stream-terminal');
  const terminalStatusText = document.getElementById('terminal-status-text');
  const terminalLogs = document.getElementById('terminal-logs');
  const jobIdDisplay = document.getElementById('job-id-display');
  
  const blogWorkspace = document.getElementById('blog-workspace');
  const activeBlogTitle = document.getElementById('active-blog-title');
  const activeBlogDate = document.getElementById('active-blog-date');
  const articleContainer = document.getElementById('article-container');
  const analysisMetricsGrid = document.getElementById('analysis-metrics-grid');
  const planSectionsList = document.getElementById('plan-sections-list');
  const imagesContainer = document.getElementById('images-container');
  const codeBlocksContainer = document.getElementById('code-blocks-container');
  const rawMarkdownVscodeWrapper = document.getElementById('raw-markdown-vscode-wrapper');
  
  const btnCopyMd = document.getElementById('btn-copy-md');
  const btnDownloadMd = document.getElementById('btn-download-md');
  const btnOpenHtmlWindow = document.getElementById('btn-open-html-window');

  const btnOpenResearch = document.getElementById('btn-open-research');
  const btnCloseResearch = document.getElementById('btn-close-research');
  const researchModal = document.getElementById('research-modal');
  const researchQueryInput = document.getElementById('research-query-input');
  const btnRunResearch = document.getElementById('btn-run-research');
  const researchResultsContainer = document.getElementById('research-results-container');

  // Initialize marked.js options
  if (window.marked) {
    marked.setOptions({
      gfm: true,
      breaks: true,
    });
  }

  // --- 1. Health Check ---
  async function checkHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        healthBadge.className = 'status-badge';
        healthText.textContent = `API v${data.version} Connected`;
      } else {
        throw new Error('Health endpoint returned error');
      }
    } catch (err) {
      healthBadge.className = 'status-badge disconnected';
      healthText.textContent = 'Disconnected';
    }
  }

  // --- 2. History Management ---
  async function fetchHistory() {
    try {
      const res = await fetch('/api/blogs');
      if (!res.ok) throw new Error('Failed to fetch history');
      const blogs = await res.json();
      renderHistory(blogs);
    } catch (err) {
      historyList.innerHTML = `<div style="color: var(--accent-rose); font-size: 0.75rem; padding: 8px;">Failed to load history.</div>`;
    }
  }

  function renderHistory(blogs) {
    if (!blogs || blogs.length === 0) {
      historyList.innerHTML = `<div style="color: var(--text-muted); font-size: 0.8rem; padding: 8px; text-align: center;">No saved blogs.</div>`;
      return;
    }

    historyList.innerHTML = '';
    blogs.forEach(blog => {
      const item = document.createElement('div');
      item.className = `history-item ${activeBlog && activeBlog.id === blog.id ? 'active' : ''}`;
      
      const dateStr = blog.created_at ? new Date(blog.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '';
      const promptSnippet = blog.prompt || 'Untitled Blog';

      item.innerHTML = `
        <div class="history-item-prompt">${escapeHtml(promptSnippet)}</div>
        <div class="history-item-meta">
          <span>${dateStr}</span>
          <button class="history-delete-btn" data-id="${blog.id}" title="Delete Blog">&times;</button>
        </div>
      `;

      item.addEventListener('click', (e) => {
        if (e.target.classList.contains('history-delete-btn')) return;
        loadBlog(blog.id);
      });

      const delBtn = item.querySelector('.history-delete-btn');
      delBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        await deleteBlog(blog.id);
      });

      historyList.appendChild(item);
    });
  }

  async function loadBlog(id) {
    try {
      const res = await fetch(`/api/blog/${id}`);
      if (!res.ok) throw new Error('Failed to fetch blog');
      const blog = await res.json();
      activeBlog = blog;
      renderBlog(blog);
      fetchHistory();
    } catch (err) {
      showToast('Error loading blog: ' + err.message, 'error');
    }
  }

  async function deleteBlog(id) {
    if (!confirm('Are you sure you want to delete this blog?')) return;
    try {
      const res = await fetch(`/api/blog/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete blog');
      showToast('Blog deleted', 'info');
      if (activeBlog && activeBlog.id === id) {
        activeBlog = null;
        blogWorkspace.classList.remove('active');
      }
      fetchHistory();
    } catch (err) {
      showToast('Delete error: ' + err.message, 'error');
    }
  }

  // --- 3. Blog Generation ---
  btnGenerate.addEventListener('click', async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      showToast('Please enter a prompt', 'warning');
      return;
    }

    btnGenerate.disabled = true;
    const isStream = streamToggle.checked;

    if (isStream) {
      await generateBlogStream(prompt);
    } else {
      await generateBlogSync(prompt);
    }

    btnGenerate.disabled = false;
  });

  async function generateBlogStream(prompt) {
    resetStreamTerminal();
    streamTerminal.classList.add('active');
    blogWorkspace.classList.remove('active');
    
    appendLog('[System] Initiating POST stream connection...');

    try {
      const res = await fetch('/api/blog/generate/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) throw new Error(`HTTP error ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6).trim();
            if (!jsonStr) continue;
            try {
              const data = JSON.parse(jsonStr);
              handleStreamEvent(data);
            } catch (e) {
              console.error('Failed to parse SSE JSON:', jsonStr);
            }
          }
        }
      }
    } catch (err) {
      terminalStatusText.textContent = 'Streaming Error';
      appendLog(`[Error] ${err.message}`);
      showToast('Generation failed: ' + err.message, 'error');
    }
  }

  function handleStreamEvent(data) {
    if (data.job_id) {
      jobIdDisplay.textContent = `Job: ${data.job_id.slice(0, 8)}...`;
    }

    if (data.event === 'node_complete') {
      const nodeName = data.node;
      appendLog(`[Node Complete] ${nodeName}`);
      updateNodeChipStatus(nodeName);
    } else if (data.event === 'done') {
      terminalStatusText.textContent = 'Complete!';
      appendLog('[Success] Blog assembly finished.');
      highlightAllNodesComplete();
      
      activeBlog = data;
      renderBlog(data);
      fetchHistory();
      showToast('Blog generated successfully!', 'success');
      
      setTimeout(() => {
        streamTerminal.classList.remove('active');
        blogWorkspace.classList.add('active');
      }, 1000);
    } else if (data.event === 'error') {
      terminalStatusText.textContent = 'Generation Failed';
      appendLog(`[Error] ${data.detail}`);
      showToast('Error: ' + data.detail, 'error');
    }
  }

  async function generateBlogSync(prompt) {
    resetStreamTerminal();
    streamTerminal.classList.add('active');
    terminalStatusText.textContent = 'Generating Article...';
    appendLog('[System] Sending synchronous request...');

    try {
      const res = await fetch('/api/blog/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        const errJson = await res.json();
        throw new Error(errJson.detail || 'Generation failed');
      }

      const data = await res.json();
      activeBlog = data;
      renderBlog(data);
      fetchHistory();
      
      streamTerminal.classList.remove('active');
      blogWorkspace.classList.add('active');
      showToast('Blog generated successfully!', 'success');
    } catch (err) {
      terminalStatusText.textContent = 'Generation Failed';
      appendLog(`[Error] ${err.message}`);
      showToast('Generation error: ' + err.message, 'error');
    }
  }

  function resetStreamTerminal() {
    terminalStatusText.textContent = 'Agent Working...';
    terminalLogs.innerHTML = '';
    jobIdDisplay.textContent = '';
    
    document.querySelectorAll('.node-chip').forEach(chip => {
      chip.className = 'node-chip';
    });
  }

  function updateNodeChipStatus(nodeName) {
    let chipId = `node-${nodeName}`;
    if (['content_generator', 'code_generator', 'image_handler'].includes(nodeName)) {
      chipId = 'node-generators';
    }
    
    const chip = document.getElementById(chipId);
    if (chip) {
      chip.classList.add('complete');
    }
  }

  function highlightAllNodesComplete() {
    document.querySelectorAll('.node-chip').forEach(chip => {
      chip.classList.remove('running');
      chip.classList.add('complete');
    });
  }

  function appendLog(msg) {
    const line = document.createElement('div');
    const timestamp = new Date().toLocaleTimeString();
    line.textContent = `[${timestamp}] ${msg}`;
    terminalLogs.appendChild(line);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
  }

  // --- 4. Render Blog & Smart Code/Typography Formatter ---
  function renderBlog(blog) {
    blogWorkspace.classList.add('active');
    
    // Header & Meta
    const planTitle = blog.plan && blog.plan.title ? blog.plan.title : (blog.prompt || 'Generated Blog');
    activeBlogTitle.textContent = planTitle;
    const dateStr = blog.created_at ? new Date(blog.created_at).toLocaleString() : '';
    activeBlogDate.textContent = `Created: ${dateStr}`;

    // Process & format raw markdown text to split squished code blocks into VS Code code fences
    const rawMarkdownText = blog.blog || '';
    const formattedMarkdownText = formatMarkdownForReading(rawMarkdownText);

    // Tab 1: Rendered Article with VS Code Code Blocks
    if (window.marked) {
      articleContainer.innerHTML = marked.parse(formattedMarkdownText);
    } else {
      articleContainer.textContent = formattedMarkdownText;
    }
    wrapCodeBlocksWithVSCodeTheme(articleContainer);

    // Tab 2: Analysis & Plan
    renderAnalysisTab(blog);

    // Tab 3: Images Gallery
    renderImagesTab(blog);

    // Tab 4: Code Snippets
    renderCodeTab(blog);

    // Tab 5: Raw Markdown in VS Code Window Frame
    renderRawMarkdownVSCode(formattedMarkdownText);
  }

  /**
   * Smart preprocessor to split squished code lines in markdown text
   * into clean multi-line VS Code code fences.
   */
  function formatMarkdownForReading(md) {
    if (!md) return '';

    // 1. Ensure blank line before and after existing ``` fence blocks
    md = md.replace(/([^\n])\n```/g, '$1\n\n```');
    md = md.replace(/```\n([^\n])/g, '```\n\n$1');

    const lines = md.split('\n');
    const resultLines = [];
    let inFence = false;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];

      if (line.trim().startsWith('```')) {
        inFence = !inFence;
        resultLines.push(line);
        continue;
      }

      if (inFence) {
        resultLines.push(line);
        continue;
      }

      // Check if line contains un-fenced Python code (e.g. "handles initialization: import os from ultralytics...")
      if (!inFence && (line.includes('import ') || line.includes('def ')) && line.includes('():') && !line.startsWith('#')) {
        const match = line.match(/^(.*?)(import\s+[a-zA-Z0-9_]+.*|def\s+[a-zA-Z0-9_]+\s*\(.*)/);
        if (match) {
          const introText = match[1].trim();
          let codeText = match[2].trim();

          if (introText) {
            resultLines.push(introText);
            resultLines.push('');
          }

          // Format squished code lines by placing statement breaks
          codeText = codeText
            .replace(/;\s*/g, '\n')
            .replace(/\s+(import\s+)/g, '\n$1')
            .replace(/\s+(from\s+[a-zA-Z0-9_.]+\s+import)/g, '\n$1')
            .replace(/\s+(def\s+[a-zA-Z0-9_]+\s*\()/g, '\n\n$1')
            .replace(/\s+(if\s+__name__\s*==)/g, '\n\n$1')
            .replace(/\s+(results\s*=)/g, '\n    $1')
            .replace(/\s+(metrics\s*=)/g, '\n    $1')
            .replace(/\s+(print\()/g, '\n    $1')
            .replace(/\s+(image_path\s*=)/g, '\n    $1')
            .replace(/\s+(if\s+os\.path)/g, '\n    $1')
            .replace(/\s+(inference_results\s*=)/g, '\n        $1')
            .replace(/\s+(else:)/g, '\n    $1');

          resultLines.push('```python');
          resultLines.push(codeText);
          resultLines.push('```');
          resultLines.push('');
          continue;
        }
      }

      resultLines.push(line);
    }

    return resultLines.join('\n');
  }

  function wrapCodeBlocksWithVSCodeTheme(container) {
    const pres = container.querySelectorAll('pre');
    pres.forEach((pre) => {
      if (pre.parentElement && pre.parentElement.classList.contains('vscode-body')) return;

      const codeEl = pre.querySelector('code');
      if (!codeEl) return;

      let lang = 'python';
      codeEl.classList.forEach(cls => {
        if (cls.startsWith('language-')) {
          lang = cls.replace('language-', '');
        }
      });

      // Apply Highlight.js syntax highlighting
      if (window.hljs) {
        try {
          hljs.highlightElement(codeEl);
        } catch (e) {
          console.warn('Highlight failed:', e);
        }
      }

      const rawCode = codeEl.textContent;

      // Wrap pre in VS Code Window DOM
      const windowBox = document.createElement('div');
      windowBox.className = 'vscode-window';

      const header = document.createElement('div');
      header.className = 'vscode-header';
      header.innerHTML = `
        <div class="vscode-dots">
          <span class="vscode-dot red"></span>
          <span class="vscode-dot yellow"></span>
          <span class="vscode-dot green"></span>
        </div>
        <div class="vscode-title">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#569cd6" stroke-width="2">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
          ${escapeHtml(lang)}
        </div>
        <button class="vscode-copy-btn">Copy</button>
      `;

      const body = document.createElement('div');
      body.className = 'vscode-body';

      pre.parentNode.insertBefore(windowBox, pre);
      body.appendChild(pre);
      windowBox.appendChild(header);
      windowBox.appendChild(body);

      const copyBtn = header.querySelector('.vscode-copy-btn');
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(rawCode);
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
      });
    });
  }

  function renderAnalysisTab(blog) {
    const analysis = blog.analysis || {};
    const plan = blog.plan || {};

    analysisMetricsGrid.innerHTML = `
      <div class="metric-card">
        <div class="metric-label">Topic</div>
        <div class="metric-value" style="font-size: 1rem; color: var(--text-main);">${escapeHtml(analysis.topic || 'N/A')}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Audience</div>
        <div class="metric-value" style="font-size: 1rem; color: var(--accent-primary);">${escapeHtml(analysis.audience || 'N/A')}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Tone</div>
        <div class="metric-value" style="font-size: 1rem; color: var(--accent-purple);">${escapeHtml(analysis.tone || 'N/A')}</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Target Words</div>
        <div class="metric-value">${analysis.word_count || 'N/A'}</div>
      </div>
    `;

    const sections = plan.sections || [];
    if (sections.length === 0) {
      planSectionsList.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem;">No section structure available.</div>`;
      return;
    }

    planSectionsList.innerHTML = sections.map((sec, idx) => `
      <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 12px 16px; margin-bottom: 8px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
          <strong style="color: var(--text-bright); font-size: 0.9rem;">${idx + 1}. ${escapeHtml(sec.title)}</strong>
          <div style="display: flex; gap: 6px;">
            ${sec.needs_code ? `<span style="font-size: 0.7rem; background: rgba(99,102,241,0.15); color: var(--accent-primary); padding: 2px 6px; border-radius: 4px;">Code</span>` : ''}
            ${sec.needs_image ? `<span style="font-size: 0.7rem; background: rgba(6,182,212,0.15); color: var(--accent-cyan); padding: 2px 6px; border-radius: 4px;">Image</span>` : ''}
          </div>
        </div>
        <p style="font-size: 0.82rem; color: var(--text-secondary);">${escapeHtml(sec.description || '')}</p>
      </div>
    `).join('');
  }

  async function renderImagesTab(blog) {
    imagesContainer.innerHTML = `<div style="color: var(--text-muted); padding: 12px; font-size: 0.85rem;">Loading image metadata...</div>`;
    
    try {
      let metadataList = [];
      if (blog.id) {
        const res = await fetch(`/api/blog/${blog.id}/images`);
        if (res.ok) metadataList = await res.json();
      }

      if (!metadataList || metadataList.length === 0) {
        imagesContainer.innerHTML = `<div style="color: var(--text-muted); padding: 12px; font-size: 0.85rem;">No image metadata available.</div>`;
        return;
      }

      imagesContainer.innerHTML = metadataList.map(img => `
        <div class="image-card">
          <div class="image-card-body">
            <div style="font-weight: 600; color: var(--text-bright);">${escapeHtml(img.filename)}</div>
            <div><strong>Creator:</strong> ${escapeHtml(img.creator || 'Unknown')}</div>
            <div><strong>Source:</strong> ${escapeHtml(img.source || 'Openverse')}</div>
            <div><strong>License:</strong> ${escapeHtml(img.license || 'N/A')}</div>
            ${img.source_url ? `<a href="${escapeHtml(img.source_url)}" target="_blank" style="color: var(--accent-cyan); text-decoration: none; margin-top: 4px; display: inline-block;">View Original Image &rarr;</a>` : ''}
          </div>
        </div>
      `).join('');
    } catch (err) {
      imagesContainer.innerHTML = `<div style="color: var(--accent-rose); padding: 12px;">Failed to load image metadata.</div>`;
    }
  }

  function renderCodeTab(blog) {
    const codeObj = blog.code || {};
    const keys = Object.keys(codeObj);

    if (keys.length === 0) {
      codeBlocksContainer.innerHTML = `<div style="color: var(--text-muted); padding: 12px; font-size: 0.85rem;">No code snippets generated for this post.</div>`;
      return;
    }

    codeBlocksContainer.innerHTML = '';
    keys.forEach(secTitle => {
      const codeItem = codeObj[secTitle];
      const lang = codeItem.language || 'python';
      const codeStr = codeItem.code || '';
      const explanation = codeItem.explanation || '';
      const deps = codeItem.dependencies || [];

      const card = document.createElement('div');
      card.className = 'glass-card';
      card.style.padding = '16px';
      
      card.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <h4 style="font-family: var(--font-heading); font-size: 1rem; color: var(--text-bright);">${escapeHtml(secTitle)}</h4>
          <span style="font-size: 0.75rem; background: var(--bg-tertiary); color: var(--accent-cyan); padding: 2px 8px; border-radius: 4px;">${escapeHtml(lang)}</span>
        </div>
        ${explanation ? `<p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px;">${escapeHtml(explanation)}</p>` : ''}
        ${deps.length > 0 ? `<div style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 8px;">Dependencies: <code>${deps.join(', ')}</code></div>` : ''}
        <pre><code class="language-${escapeHtml(lang)}">${escapeHtml(codeStr)}</code></pre>
      `;

      codeBlocksContainer.appendChild(card);
      wrapCodeBlocksWithVSCodeTheme(card);
    });
  }

  function renderRawMarkdownVSCode(markdownText) {
    rawMarkdownVscodeWrapper.innerHTML = `<pre><code class="language-markdown">${escapeHtml(markdownText)}</code></pre>`;
    wrapCodeBlocksWithVSCodeTheme(rawMarkdownVscodeWrapper);
  }

  // --- 5. Tabs Navigation Handler ---
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPaneId = btn.getAttribute('data-tab');
      const pane = document.getElementById(targetPaneId);
      if (pane) pane.classList.add('active');
    });
  });

  // Presets
  document.querySelectorAll('.preset-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      promptInput.value = pill.getAttribute('data-prompt');
      promptInput.focus();
    });
  });

  // Actions
  btnCopyMd.addEventListener('click', () => {
    if (!activeBlog || !activeBlog.blog) return;
    navigator.clipboard.writeText(activeBlog.blog);
    showToast('Markdown copied!', 'success');
  });

  btnDownloadMd.addEventListener('click', () => {
    if (!activeBlog || !activeBlog.blog) return;
    const blob = new Blob([activeBlog.blog], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `blog-${activeBlog.id || 'export'}.md`;
    a.click();
    URL.revokeObjectURL(url);
  });

  btnOpenHtmlWindow.addEventListener('click', () => {
    if (!activeBlog || !activeBlog.id) return;
    window.open(`/api/blog/${activeBlog.id}/html`, '_blank');
  });

  // --- 6. Research Modal ---
  btnOpenResearch.addEventListener('click', () => {
    researchModal.classList.add('active');
    researchQueryInput.focus();
  });

  btnCloseResearch.addEventListener('click', () => {
    researchModal.classList.remove('active');
  });

  researchModal.addEventListener('click', (e) => {
    if (e.target === researchModal) researchModal.classList.remove('active');
  });

  btnRunResearch.addEventListener('click', async () => {
    const query = researchQueryInput.value.trim();
    if (!query) return;

    btnRunResearch.disabled = true;
    researchResultsContainer.innerHTML = `<div style="color: var(--text-muted); text-align: center; padding: 16px; font-size: 0.85rem;">Searching web...</div>`;

    try {
      const res = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) throw new Error('Research request failed');
      const data = await res.json();
      renderResearchResults(data.results || []);
    } catch (err) {
      researchResultsContainer.innerHTML = `<div style="color: var(--accent-rose); text-align: center; padding: 16px;">Error: ${err.message}</div>`;
    } finally {
      btnRunResearch.disabled = false;
    }
  });

  function renderResearchResults(results) {
    if (results.length === 0) {
      researchResultsContainer.innerHTML = `<div style="color: var(--text-muted); text-align: center; padding: 16px; font-size: 0.85rem;">No results found.</div>`;
      return;
    }

    researchResultsContainer.innerHTML = results.map(item => `
      <div style="background: var(--bg-primary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 12px 14px;">
        <a href="${escapeHtml(item.url)}" target="_blank" style="font-family: var(--font-heading); font-size: 0.95rem; font-weight: 600; color: var(--accent-cyan); text-decoration: none;">${escapeHtml(item.title || item.url)}</a>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 4px; line-height: 1.45;">${escapeHtml(item.content || '')}</p>
        <div style="font-size: 0.72rem; color: var(--text-muted); margin-top: 6px;">Relevance Score: ${(item.score || 0).toFixed(2)}</div>
      </div>
    `).join('');
  }

  // Toast
  function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';
    if (type === 'warning') icon = '⚠️';

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(20px)';
      toast.style.transition = 'all 0.2s ease';
      setTimeout(() => toast.remove(), 200);
    }, 2500);
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, m => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    })[m]);
  }

  btnRefreshHistory.addEventListener('click', fetchHistory);

  // Initial Load
  checkHealth();
  fetchHistory();
});
