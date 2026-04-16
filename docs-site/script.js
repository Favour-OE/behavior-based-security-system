const docsContent = {
  'introduction': {
    title: 'Introduction',
    content: `BBSS (Behavior-Based Security System) is a Python package that implements continuous authentication through behavioral biometrics. It goes beyond traditional password-based authentication by monitoring user behavior patterns and flagging sessions that deviate from established baselines.

The system captures behavioral signals (typing speed, login times, command patterns, IP addresses) and builds statistical profiles. When a session deviates from this baseline, BBSS computes a risk score and triggers appropriate security responses: allow, challenge with PIN verification, or block.`
  },
  'key-features': {
    title: 'Key Features',
    content: `Continuous authentication: Validates sessions in real-time, not just at login
Behavioral profiling: Learns user patterns—typing speed, session timing, command sequences
Statistical anomaly detection: Uses z-score and IQR-based analysis
Risk-based responses: Smart escalation—allow safe sessions, challenge suspicious ones, block threats
Machine learning ready: Isolation Forest models for advanced anomaly detection
Runtime configuration: All settings configurable at runtime via code or environment
Production-ready: 88+ tests with full coverage, modular design`
  },
  'installation': {
    title: 'Installation',
    content: `Requirements: Python 3.10+
Install from PyPI: pip install bbss
Install from Source: git clone and pip install -e .
Install with Dev Dependencies: pip install -e ".[dev]"`
  },
  'quickstart': {
    title: 'Quick Start',
    content: `Basic Usage: from bbss import BBSS; engine = BBSS(); result = engine.signup(username="john_doe", password="SecurePassword123!")
Authenticate: result = engine.login(username="john_doe", password="SecurePassword123!", typing_time=2.14, ip_address="192.168.1.10")
Handle Session: if result["success"]: session = result["session"]; engine.execute_command(session, "view_report"); engine.end_session(session)`
  },
  'architecture': {
    title: 'Architecture',
    content: `BBSS follows a modular architecture with clear separation of concerns:
auth: User registration, login, password hashing (Argon2), session management
behavior: Behavioral signal capture, profile building, anomaly detection
security: Risk scoring, risk classification, security response dispatcher
database: SQLite database management, models, query helpers
ml: Machine learning models (Isolation Forest), feature extraction
logs: Security logging, audit trail management
config: Runtime configuration management`
  },
  'risk-scoring': {
    title: 'Risk Scoring',
    content: `Every session receives a risk score from 0–100 based on detected anomalies:
0–30 SAFE: Grant full access immediately
31–60 WARNING: Secondary verification (PIN challenge)
61–100 HIGH_RISK: Block session immediately

Each anomaly signal contributes a weighted score. Default weights are configurable via RISK_WEIGHT_* settings.`
  },
  'behavioral-signals': {
    title: 'Behavioral Signals',
    content: `BBSS captures and analyzes the following behavioral signals:
typing_time_deviation: Z-score analysis (weight: 20)
unusual_login_hour: IQR analysis (weight: 25)
unusual_login_day: Pattern matching (weight: 10)
unknown_ip: IP whitelist check (weight: 20)
command_count_anomaly: Z-score analysis (weight: 15)
unknown_commands: Command whitelist (weight: 10)
session_duration_anomaly: Z-score analysis (weight: 10)
ml_isolation_forest: ML model prediction (weight: 30)`
  },
  'profile-lifecycle': {
    title: 'Profile Lifecycle',
    content: `BBSS handles new users gracefully with a three-stage profile maturity system:
Bootstrapping (Sessions 1–4): Sensitivity 0%, anomaly detection disabled
Warmup (Sessions 5–9): Sensitivity 50%, reduced sensitivity
Active (Sessions 10+): Sensitivity 100%, full detection

Use MIN_SESSIONS_BOOTSTRAPPING and MIN_SESSIONS_WARMUP to adjust thresholds.`
  },
  'bbss-class': {
    title: 'BBSS Class',
    content: `The main entry point for using BBSS. Supports runtime configuration.

Constructor: BBSS(**config_overrides)
Methods:
- signup(username, password, email?): Register a new user
- login(username, password, typing_time?, ip_address?, user_agent?): Authenticate user
- execute_command(session, command_name): Record a command during session
- end_session(session): End an active session
- get_user_report(user_id): Get security report for a user`
  },
  'session-class': {
    title: 'Session Class',
    content: `Represents an active authenticated session. Returned by engine.login() when session is allowed.

Properties:
- user_id: User identifier
- token: Session token
- session_id: Database session ID
- capture_ctx: Behavior capture context

Methods:
- add_command(command_name): Record a command executed during session
- end(): End the session and return behavior log ID`
  },
  'runtime-config': {
    title: 'Runtime Configuration',
    content: `BBSS supports three levels of configuration (in priority order):
1. Programmatic overrides (highest priority)
2. Environment variables
3. Default values (lowest priority)

Configure globally: from bbss import configure; configure(LOG_DIR="./custom_logs", CONSOLE_LOGGING=False, MAX_FAILED_ATTEMPTS=3)`
  },
  'config-reference': {
    title: 'Configuration Reference',
    content: `Database: DATABASE_PATH (default: ./bbss.db)
Authentication: SECRET_KEY, SESSION_EXPIRY_HOURS (24), MAX_FAILED_ATTEMPTS (5), LOCKOUT_DURATION_MINUTES (30)
Profile & Detection: MIN_SESSIONS_BOOTSTRAPPING (5), MIN_SESSIONS_WARMUP (10), ZSCORE_THRESHOLD (2.0), IQR_MULTIPLIER (1.5)
Risk Scoring: RISK_WEIGHT_* weights and RISK_THRESHOLD_WARNING (31), RISK_THRESHOLD_HIGH (61)
Logging: LOG_DIR (./logs), LOG_LEVEL (INFO), LOG_RETENTION_DAYS (30), CONSOLE_LOGGING (true)
ML: ML_ENABLED (true), ML_MIN_SESSIONS_FOR_TRAINING (20), ML_RETRAIN_EVERY_N_SESSIONS (10)`
  },
  'env-variables': {
    title: 'Environment Variables',
    content: `DATABASE_PATH: Path to SQLite database file (./bbss.db)
SECRET_KEY: Random 32-byte hex string for HMAC operations
SESSION_EXPIRY_HOURS: Session token lifetime (24)
MAX_FAILED_ATTEMPTS: Login failures before lockout (5)
LOCKOUT_DURATION_MINUTES: Account lockout duration (30)
MIN_SESSIONS_BOOTSTRAPPING: Sessions before any detection runs (5)
MIN_SESSIONS_WARMUP: Sessions before full sensitivity (10)
ZSCORE_THRESHOLD: Z-score above which signal is flagged (2.0)
IQR_MULTIPLIER: IQR multiplier for time-based anomalies (1.5)
RISK_WEIGHT_*: Individual weights for each anomaly signal
RISK_THRESHOLD_WARNING: Score threshold for WARNING (31)
RISK_THRESHOLD_HIGH: Score threshold for HIGH_RISK (61)
LOG_DIR: Log directory path (./logs)
LOG_LEVEL: DEBUG | INFO | WARNING | ERROR | CRITICAL
ML_ENABLED: Enable ML anomaly detection (true)`
  },
  'examples': {
    title: 'Examples',
    content: `High Security: BBSS with RISK_THRESHOLD_WARNING=20, RISK_THRESHOLD_HIGH=50, MAX_FAILED_ATTEMPTS=3
Development: configure with DATABASE_PATH=":memory:", LOG_LEVEL="DEBUG", ML_ENABLED=False
Session Management: signup, login, execute_command, end_session workflow`
  },
  'troubleshooting': {
    title: 'Troubleshooting',
    content: `ImportError: No module named 'bbss' - Run pip install -e . in the project root
Session blocked unexpectedly - Check MIN_SESSIONS_BOOTSTRAPPING settings for new users
ML model not training - Ensure ML_ENABLED=True and user has ML_MIN_SESSIONS_FOR_TRAINING sessions
Config changes not taking effect - Set config before creating the BBSS engine`
  },
  'contributing': {
    title: 'Contributing',
    content: `Fork the repository
Create a feature branch: git checkout -b feature/amazing-feature
Commit changes: git commit -m 'Add amazing feature'
Push to branch: git push origin feature/amazing-feature
Open a Pull Request
Run tests with: pytest tests/ -v`
  }
};

function initApp() {
  initTheme();
  wrapCodeBlocks();
  initScrollSpy();
  initSearch();
  initProgressBar();
  initBackToTop();
  initKeyboardShortcuts();
  initMobileMenu();
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const themeToggle = document.querySelector('.theme-toggle');
  const sunIcon = themeToggle?.querySelector('.sun-icon');
  const moonIcon = themeToggle?.querySelector('.moon-icon');
  
  if (saved === 'dark' || (saved === null && prefersDark)) {
    document.documentElement.classList.add('dark');
    if (sunIcon) sunIcon.style.display = 'block';
    if (moonIcon) moonIcon.style.display = 'none';
  } else {
    if (sunIcon) sunIcon.style.display = 'none';
    if (moonIcon) moonIcon.style.display = 'block';
  }
}

function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.classList.contains('dark');
  const themeToggle = document.querySelector('.theme-toggle');
  const sunIcon = themeToggle?.querySelector('.sun-icon');
  const moonIcon = themeToggle?.querySelector('.moon-icon');
  
  if (isDark) {
    html.classList.remove('dark');
    localStorage.setItem('theme', 'light');
    if (sunIcon) sunIcon.style.display = 'none';
    if (moonIcon) moonIcon.style.display = 'block';
  } else {
    html.classList.add('dark');
    localStorage.setItem('theme', 'dark');
    if (sunIcon) sunIcon.style.display = 'block';
    if (moonIcon) moonIcon.style.display = 'none';
  }
}

function detectLanguage(content) {
  const trimmed = content.trim();
  
  if (trimmed.startsWith('pip install') || trimmed.startsWith('pip3 install') ||
      trimmed.startsWith('python ') || trimmed.startsWith('python3 ') ||
      trimmed.match(/^from\s+\w+\s+import/m) || 
      trimmed.match(/^import\s+/m) ||
      trimmed.includes('def ') || trimmed.includes('class ') ||
      trimmed.includes('__init__') || trimmed.includes('self.')) {
    return 'python';
  }
  if (trimmed.startsWith('npm ') || trimmed.startsWith('yarn ') || 
      trimmed.includes('require(') || trimmed.includes('import {') ||
      trimmed.includes('const ') || trimmed.includes('let ') ||
      trimmed.includes('export default') || trimmed.includes('export const') ||
      trimmed.includes('export function')) {
    return 'javascript';
  }
  if (trimmed.startsWith('git ') || trimmed.startsWith('docker ') ||
      trimmed.startsWith('./') || trimmed.startsWith('bash ') ||
      trimmed.match(/^\$\s/) || trimmed.includes('#!/bin/bash') ||
      trimmed.startsWith('cd ') || trimmed.startsWith('mkdir ') ||
      trimmed.startsWith('source ') || trimmed.startsWith('pip ') ||
      trimmed.startsWith('pip3 ') || trimmed.startsWith('pytest ') ||
      trimmed.startsWith('cp ') || trimmed.startsWith('rm ') ||
      trimmed.startsWith('ls ') || trimmed.startsWith('touch ') ||
      trimmed.startsWith('cat ') || trimmed.startsWith('echo ') ||
      trimmed.startsWith('export ') || trimmed.startsWith('venv') ||
      trimmed.startsWith('python3 ') || trimmed.startsWith('virtualenv') ||
      trimmed.startsWith('fork') || trimmed.startsWith('clone') ||
      trimmed.match(/^git checkout/) || trimmed.match(/^git commit/) ||
      trimmed.match(/^git push/) || trimmed.match(/^git clone/)) {
    return 'bash';
  }
  if (trimmed.includes('SELECT ') || trimmed.includes('INSERT INTO') ||
      trimmed.includes('UPDATE ') || trimmed.includes('DELETE FROM') ||
      trimmed.includes('CREATE TABLE') || trimmed.includes('PRIMARY KEY') ||
      trimmed.includes('REFERENCES ') || trimmed.includes('ON DELETE')) {
    return 'sql';
  }
  if (trimmed.includes('<?php') || trimmed.includes('<?')) {
    return 'php';
  }
  if (trimmed.match(/^fn\s+\w+\s*\(/m) || trimmed.match(/^impl\s+\w+/m) ||
      trimmed.match(/^use\s+\w+::/m) || trimmed.includes('let mut') ||
      trimmed.includes('-> ') || trimmed.includes('&str') ||
      trimmed.includes('println!')) {
    return 'rust';
  }
  if (trimmed.match(/^func\s+\w+/m) || trimmed.match(/^package\s+\w+/m) ||
      trimmed.includes('fmt.Println') || trimmed.includes('fmt.Printf')) {
    return 'go';
  }
  if (trimmed.includes('env ') || trimmed.match(/^[A-Z_]+=/m)) {
    return 'bash';
  }
  return 'bash';
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function copyToClipboard(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
}

function wrapCodeBlocks() {
  const codeBlocks = document.querySelectorAll('.code-block');
  
  codeBlocks.forEach((block, index) => {
    if (block.querySelector('.code-block-header')) return;
    
    const content = block.textContent || block.innerText;
    const language = detectLanguage(content);
    
    const wrapper = document.createElement('div');
    wrapper.className = 'code-block';
    
    wrapper.innerHTML = `
      <div class="code-block-header">
        <div class="code-block-left">
          <div class="code-block-dots">
            <span class="code-block-dot red"></span>
            <span class="code-block-dot yellow"></span>
            <span class="code-block-dot green"></span>
          </div>
          <span class="code-block-title">${language.toUpperCase()}</span>
        </div>
        <div class="code-block-right">
          <button class="code-block-copy-btn" data-code="${content.replace(/"/g, '&quot;').replace(/\n/g, '&#10;')}" data-copied="false" title="Copy code">
            <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span class="copy-text">Copy</span>
          </button>
        </div>
      </div>
      <div class="code-block-content"><code class="language-${language}">${escapeHtml(content)}</code></div>
    `;
    
    block.parentNode.replaceChild(wrapper, block);
  });
  
  document.querySelectorAll('.code-block-copy-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      if (this.disabled) return;
      
      const code = this.getAttribute('data-code').replace(/&#10;/g, '\n');
      copyToClipboard(code);
      
      this.disabled = true;
      this.classList.add('copied');
      this.querySelector('.copy-icon').style.display = 'none';
      this.querySelector('.copy-text').textContent = 'copied';
      this.title = 'Copied!';
      
      setTimeout(() => {
        this.disabled = false;
        this.classList.remove('copied');
        this.querySelector('.copy-icon').style.display = '';
        this.querySelector('.copy-text').textContent = 'Copy';
        this.title = 'Copy code';
      }, 60000);
    });
  });
  
  if (typeof hljs !== 'undefined') {
    document.querySelectorAll('pre code').forEach((block) => {
      hljs.highlightElement(block);
    });
  }
}

function initScrollSpy() {
  const sections = document.querySelectorAll('.section[id]');
  const navLinks = document.querySelectorAll('.nav-link');
  
  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -80% 0px',
    threshold: 0
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          }
        });
        
        document.querySelectorAll('.breadcrumb span').forEach(breadcrumb => {
          breadcrumb.textContent = id.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        });
      }
    });
  }, observerOptions);
  
  sections.forEach(section => observer.observe(section));
  
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href').substring(1);
      const target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
        if (window.innerWidth <= 768) {
          closeMobileMenu();
        }
      }
    });
  });
}

function highlightText(text, query) {
  if (!query) return escapeHtml(text);
  
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return escapeHtml(text).replace(regex, '<mark class="search-highlight">$1</mark>');
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function initSearch() {
  const searchInput = document.querySelector('.search-box input');
  const searchContainer = document.querySelector('.search-box');
  
  let searchResultsContainer = document.querySelector('.search-results');
  if (!searchResultsContainer) {
    searchResultsContainer = document.createElement('div');
    searchResultsContainer.className = 'search-results';
    searchContainer.appendChild(searchResultsContainer);
  }
  
  const performSearch = debounce((query) => {
    if (query.length < 2) {
      searchResultsContainer.innerHTML = '';
      return;
    }
    
    const results = [];
    
    Object.entries(docsContent).forEach(([id, data]) => {
      const titleMatch = data.title.toLowerCase().includes(query);
      const contentMatch = data.content.toLowerCase().includes(query);
      
      if (titleMatch || contentMatch) {
        const section = document.getElementById(id);
        if (!section) return;
        
        let snippet = data.content;
        if (contentMatch) {
          const index = data.content.toLowerCase().indexOf(query);
          const start = Math.max(0, index - 40);
          const end = Math.min(data.content.length, index + query.length + 60);
          snippet = (start > 0 ? '...' : '') + data.content.substring(start, end) + (end < data.content.length ? '...' : '');
        }
        
        results.push({
          id,
          title: data.title,
          snippet,
          titleMatch
        });
      }
    });
    
    if (results.length === 0) {
      searchResultsContainer.innerHTML = '<div class="search-no-results">No results found</div>';
      return;
    }
    
    results.sort((a, b) => b.titleMatch - a.titleMatch);
    
    searchResultsContainer.innerHTML = results.slice(0, 5).map((result, index) => `
      <div class="search-result-item" data-target="${result.id}" data-index="${index}" tabindex="0">
        <strong>${highlightText(result.title, query)}</strong>
        <div style="font-size: 12px; color: var(--text-tertiary); margin-top: 4px;">
          ${highlightText(result.snippet.substring(0, 100), query)}
        </div>
      </div>
    `).join('');
    
    selectedResultIndex = -1;
    
    document.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', () => {
        const targetId = item.getAttribute('data-target');
        const target = document.getElementById(targetId);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth' });
          searchInput.value = '';
          searchResultsContainer.innerHTML = '';
          closeMobileMenu();
        }
      });
    });
  }, 200);
  
  let selectedResultIndex = -1;
  
  searchInput.addEventListener('input', (e) => {
    selectedResultIndex = -1;
    performSearch(e.target.value.trim().toLowerCase());
  });
  
  searchInput.addEventListener('keydown', (e) => {
    const items = searchResultsContainer.querySelectorAll('.search-result-item');
    if (items.length === 0) return;
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedResultIndex = Math.min(selectedResultIndex + 1, items.length - 1);
      updateResultSelection(items, selectedResultIndex);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedResultIndex = Math.max(selectedResultIndex - 1, -1);
      updateResultSelection(items, selectedResultIndex);
    } else if (e.key === 'Enter' && selectedResultIndex >= 0) {
      e.preventDefault();
      items[selectedResultIndex].click();
    } else if (e.key === 'Escape') {
      searchResultsContainer.innerHTML = '';
      searchInput.blur();
    }
  });
  
  function updateResultSelection(items, index) {
    items.forEach((item, i) => {
      item.classList.toggle('selected', i === index);
      if (i === index) {
        item.scrollIntoView({ block: 'nearest' });
      }
    });
  }
  
  searchInput.addEventListener('focus', () => {
    if (searchInput.value.trim().length >= 2) {
      searchInput.dispatchEvent(new Event('input'));
    }
  });
  
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResultsContainer.contains(e.target)) {
      searchResultsContainer.innerHTML = '';
    }
  });
}

function initProgressBar() {
  const progressBar = document.getElementById('progressBar');
  if (!progressBar) return;
  
  window.addEventListener('scroll', () => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (scrollTop / docHeight) * 100;
    progressBar.style.width = `${progress}%`;
  });
}

function initBackToTop() {
  const backToTopBtn = document.getElementById('backToTop');
  if (!backToTopBtn) return;
  
  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      backToTopBtn.classList.add('visible');
    } else {
      backToTopBtn.classList.remove('visible');
    }
  });
  
  backToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    const sections = Array.from(document.querySelectorAll('.section[id]'));
    
    if (e.key === '/') {
      e.preventDefault();
      document.querySelector('.search-box input').focus();
    } else if (e.key === 'j' || e.key === 'J') {
      e.preventDefault();
      navigateSection(sections, 1);
    } else if (e.key === 'k' || e.key === 'K') {
      e.preventDefault();
      navigateSection(sections, -1);
    } else if (e.key === 't' || e.key === 'T') {
      e.preventDefault();
      toggleTheme();
    } else if (e.key === 'Escape') {
      closeMobileMenu();
    }
  });
  
  function navigateSection(sections, direction) {
    const scrollTop = window.scrollY;
    let currentIndex = -1;
    
    sections.forEach((section, index) => {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 150) {
        currentIndex = index;
      }
    });
    
    let nextIndex = currentIndex + direction;
    if (nextIndex < 0) nextIndex = 0;
    if (nextIndex >= sections.length) nextIndex = sections.length - 1;
    
    sections[nextIndex].scrollIntoView({ behavior: 'smooth' });
  }
}

function initMobileMenu() {
  let menuToggle = document.querySelector('.mobile-menu-toggle');
  
  if (!menuToggle) {
    const sidebar = document.querySelector('.sidebar');
    menuToggle = document.createElement('button');
    menuToggle.className = 'mobile-menu-toggle';
    menuToggle.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
    menuToggle.setAttribute('aria-label', 'Toggle menu');
    sidebar.insertBefore(menuToggle, sidebar.firstChild);
  }
  
  menuToggle.addEventListener('click', () => {
    document.body.classList.toggle('mobile-menu-open');
  });
}

function closeMobileMenu() {
  document.body.classList.remove('mobile-menu-open');
}

document.addEventListener('DOMContentLoaded', initApp);
