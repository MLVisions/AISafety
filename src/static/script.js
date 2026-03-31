// Note: navigation across pages is handled by simple anchor links in the HTML.
// This script focuses on tab switching within a page and gamification enhancements.

// Smooth scrolling for any anchor links
document.addEventListener('DOMContentLoaded', () => {
  // Smooth scrolling behavior
  document.documentElement.style.scrollBehavior = 'smooth';
  
  // Add loading animation for images
  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach(img => {
    img.addEventListener('load', () => {
      img.style.opacity = '1';
      img.style.transform = 'scale(1)';
    });
    
    // Set initial state for fade-in effect
    img.style.opacity = '0';
    img.style.transform = 'scale(0.95)';
    img.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  });

  // Initialize tabs functionality
  initializeTabs();

  // Add button feedback
  addButtonFeedback();

  // Add intersection observer for scroll animations
  addScrollAnimations();

  // Add gamification elements
  addGamificationElements();

  // Initialize ticker dropdown functionality (isolated so errors don't hide page content)
  try { initializeTickerDropdowns(); } catch (e) { console.error('Ticker init error:', e); }
});

function initializeTabs() {
  // Get all tab buttons
  const tabButtons = document.querySelectorAll('.tab-button');
  
  tabButtons.forEach(button => {
    button.addEventListener('click', function() {
      // Remove active class from all buttons
      tabButtons.forEach(btn => btn.classList.remove('active'));
      
      // Add active class to clicked button
      this.classList.add('active');
      
      // Hide all tab content
      document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'none';
      });
      
      // Show the selected tab content
      const targetTab = document.getElementById(this.getAttribute('data-tab'));
      if (targetTab) {
        targetTab.style.display = 'block';
      }
    });
  });
  
  // Initialize - show first tab if no tab is visible
  const visibleTab = document.querySelector('.tab-content[style*="block"]');
  if (!visibleTab && tabButtons.length > 0) {
    // Click the first tab to initialize
    tabButtons[0].click();
  }
}

function addButtonFeedback() {
  // Add subtle click animation to all buttons
  document.querySelectorAll('button').forEach(button => {
    button.addEventListener('click', function(e) {
      // Create ripple effect
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      
      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple 0.5s linear;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        pointer-events: none;
        z-index: 10;
      `;
      
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 500);
    });
  });
  
  // Add ripple animation CSS
  if (!document.getElementById('ripple-styles')) {
    const style = document.createElement('style');
    style.id = 'ripple-styles';
    style.textContent = `
      @keyframes ripple {
        to {
          transform: scale(3);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

function addScrollAnimations() {
  // Check if IntersectionObserver is supported (iOS Safari compatibility)
  if ('IntersectionObserver' in window) {
    const observerOptions = {
      threshold: 0,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, observerOptions);

    // Observe content sections for scroll animations
    document.querySelectorAll('.content-section').forEach(section => {
      section.style.opacity = '0';
      section.style.transform = 'translateY(30px)';
      section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(section);
    });
  } else {
    // Fallback for older iOS versions - show all content immediately
    document.querySelectorAll('.content-section').forEach(section => {
      section.style.opacity = '1';
      section.style.transform = 'translateY(0)';
    });
  }
}

function addGamificationElements() {
  // Detect if device is iOS/touch device
  const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  
  // Add particle effects on hover for nav buttons (desktop) or touch for mobile
  document.querySelectorAll('.nav-button, .cta-button').forEach(button => {
    if (isTouch) {
      // For touch devices, use touch events instead of hover
      button.addEventListener('touchstart', function() {
        createParticles(this);
      }, { passive: true });
    } else {
      button.addEventListener('mouseenter', function() {
        createParticles(this);
      });
    }
  });

  // Add achievement-style feedback for action cards
  document.querySelectorAll('.action-card').forEach(card => {
    const eventType = isTouch ? 'touchstart' : 'click';
    card.addEventListener(eventType, function() {
      showAchievementToast('Progress tracked!');
    }, { passive: true });
  });

  // Add floating elements animation
  addFloatingElements();
}

function createParticles(element) {
  const particles = 6;
  for (let i = 0; i < particles; i++) {
    const particle = document.createElement('div');
    const rect = element.getBoundingClientRect();
    
    particle.style.cssText = `
      position: fixed;
      width: 4px;
      height: 4px;
      background: linear-gradient(45deg, #4da3d8, #295da0);
      border-radius: 50%;
      pointer-events: none;
      z-index: 1000;
      left: ${rect.left + rect.width/2}px;
      top: ${rect.top + rect.height/2}px;
      animation: particleFloat 1s ease-out forwards;
    `;
    
    // Random direction
    const angle = (Math.PI * 2 * i) / particles;
    const distance = 40 + Math.random() * 20;
    const endX = Math.cos(angle) * distance;
    const endY = Math.sin(angle) * distance;
    
    particle.style.setProperty('--end-x', endX + 'px');
    particle.style.setProperty('--end-y', endY + 'px');
    
    document.body.appendChild(particle);
    
    setTimeout(() => particle.remove(), 1000);
  }
  
  // Add particle animation CSS if not exists
  if (!document.getElementById('particle-styles')) {
    const style = document.createElement('style');
    style.id = 'particle-styles';
    style.textContent = `
      @keyframes particleFloat {
        0% {
          transform: translate(0, 0) scale(1);
          opacity: 1;
        }
        100% {
          transform: translate(var(--end-x), var(--end-y)) scale(0);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

function showAchievementToast(message) {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #4da3d8 0%, #295da0 100%);
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    z-index: 10000;
    animation: toastSlideIn 0.3s ease-out;
  `;
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'toastSlideOut 0.3s ease-in forwards';
    setTimeout(() => toast.remove(), 300);
  }, 2000);
  
  // Add toast animation CSS if not exists
  if (!document.getElementById('toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
      @keyframes toastSlideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
      @keyframes toastSlideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
}

function addFloatingElements() {
  // Add subtle floating background elements
  const header = document.querySelector('header');
  if (header) {
    for (let i = 0; i < 5; i++) {
      const floater = document.createElement('div');
      floater.style.cssText = `
        position: absolute;
        width: ${20 + Math.random() * 30}px;
        height: ${20 + Math.random() * 30}px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
        left: ${Math.random() * 100}%;
        top: ${Math.random() * 100}%;
        animation: float${i} ${8 + Math.random() * 4}s ease-in-out infinite;
        pointer-events: none;
      `;
      header.appendChild(floater);
    }
    
    // Add floating animation CSS
    if (!document.getElementById('float-styles')) {
      const style = document.createElement('style');
      style.id = 'float-styles';
      style.textContent = `
        @keyframes float0 { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-20px) rotate(180deg); } }
        @keyframes float1 { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-30px) rotate(-180deg); } }
        @keyframes float2 { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-25px) rotate(270deg); } }
        @keyframes float3 { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-15px) rotate(-270deg); } }
        @keyframes float4 { 0%, 100% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-35px) rotate(90deg); } }
      `;
      document.head.appendChild(style);
    }
  }
}

// Ticker dropdown functionality — multi-select with Plotly rendering
function initializeTickerDropdowns() {
  const containers = document.querySelectorAll('.ticker-dropdown-container');
  if (containers.length === 0) return;

  // Lazy-load Plotly.js from CDN only when needed
  let plotlyReady = false;
  const plotlyQueue = [];

  function loadPlotly() {
    if (plotlyReady || document.getElementById('plotly-cdn')) return;
    const s = document.createElement('script');
    s.id = 'plotly-cdn';
    s.src = 'https://cdn.plot.ly/plotly-2.35.2.min.js';
    s.defer = true;
    s.onload = () => {
      plotlyReady = true;
      plotlyQueue.forEach(fn => fn());
      plotlyQueue.length = 0;
    };
    document.head.appendChild(s);
  }

  function whenPlotlyReady(fn) {
    if (plotlyReady) fn();
    else { loadPlotly(); plotlyQueue.push(fn); }
  }

  fetch('data/ticker_dropdown.json')
    .then(r => r.json())
    .then(data => containers.forEach(c => createTickerPicker(c, data, whenPlotlyReady)))
    .catch(() => {});
}

function createTickerPicker(container, tickerData, whenPlotlyReady) {
  const TRACE_COLORS = ['#295da0', '#d4952a', '#4da3d8', '#c45c5c', '#5cb88a', '#8e6cc2', '#e07b53', '#4aa396'];
  let nextColor = 0;
  const selected = new Map(); // ticker -> { info, data, color }
  let currentView = 'normalized';

  container.innerHTML = `
    <div class="ticker-picker">
      <div class="ticker-selected-chips"></div>
      <div class="ticker-picker-control">
        <button class="ticker-picker-toggle" type="button">
          <span class="ticker-picker-label">📊 Select assets to compare</span>
          <span class="ticker-picker-arrow">▾</span>
        </button>
      </div>
      <div class="ticker-picker-dropdown" style="display:none;">
        <div class="ticker-picker-search">
          <input type="text" placeholder="Search tickers..." class="ticker-search-input" />
        </div>
        <div class="ticker-picker-options"></div>
        <div class="ticker-picker-footer">
          <small>${tickerData.metadata.total_tickers} assets · click to add/remove</small>
        </div>
      </div>
    </div>
    <div class="ticker-chart-area" style="display:none;">
      <div class="ticker-chart-header">
        <h4 class="ticker-chart-title">Asset Comparison</h4>
        <div class="ticker-chart-controls">
          <button class="ticker-view-toggle active" data-view="normalized">% Change</button>
          <button class="ticker-view-toggle" data-view="raw">Raw Price</button>
        </div>
      </div>
      <div class="ticker-plotly-chart"></div>
    </div>
  `;

  const toggle = container.querySelector('.ticker-picker-toggle');
  const dropdown = container.querySelector('.ticker-picker-dropdown');
  const optionsEl = container.querySelector('.ticker-picker-options');
  const searchInput = container.querySelector('.ticker-search-input');
  const chipsArea = container.querySelector('.ticker-selected-chips');
  const chartArea = container.querySelector('.ticker-chart-area');
  const chartDiv = container.querySelector('.ticker-plotly-chart');
  const viewToggles = container.querySelectorAll('.ticker-view-toggle');

  // View toggle
  viewToggles.forEach(btn => {
    btn.addEventListener('click', () => {
      viewToggles.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentView = btn.dataset.view;
      renderChart();
    });
  });

  function renderOptions(filter = '') {
    const lf = filter.toLowerCase();
    let html = '';
    for (const [, cat] of Object.entries(tickerData.categories)) {
      const matching = cat.tickers.filter(t =>
        !lf || t.display_name.toLowerCase().includes(lf) ||
        t.ticker.toLowerCase().includes(lf) ||
        t.description.toLowerCase().includes(lf)
      );
      if (matching.length === 0) continue;
      html += `<div class="picker-optgroup-label">${cat.display_name}</div>`;
      for (const t of matching) {
        const sel = selected.has(t.ticker) ? ' selected' : '';
        html += `<div class="picker-option${sel}" data-ticker="${t.ticker}">`
          + `<span class="picker-option-check">${sel ? '✓' : ''}</span>`
          + `${t.display_name}<span class="picker-option-ticker">${t.ticker}</span></div>`;
      }
    }
    optionsEl.innerHTML = html || '<div class="picker-no-results">No matching assets</div>';
    optionsEl.querySelectorAll('.picker-option').forEach(opt => {
      opt.addEventListener('click', () => toggleTicker(opt.dataset.ticker));
    });
  }

  function findTickerInfo(ticker) {
    for (const cat of Object.values(tickerData.categories)) {
      const found = cat.tickers.find(t => t.ticker === ticker);
      if (found) return found;
    }
    return null;
  }

  function toggleTicker(ticker) {
    if (selected.has(ticker)) {
      selected.delete(ticker);
      renderChips();
      renderOptions(searchInput.value);
      renderChart();
    } else {
      const info = findTickerInfo(ticker);
      if (!info || !info.data_path) return;
      const color = TRACE_COLORS[nextColor++ % TRACE_COLORS.length];
      fetch(info.data_path)
        .then(r => r.json())
        .then(data => {
          selected.set(ticker, { info, data, color });
          renderChips();
          renderOptions(searchInput.value);
          renderChart();
        })
        .catch(() => {});
    }
  }

  function renderChips() {
    chipsArea.innerHTML = [...selected].map(([key, { info, color }]) =>
      `<span class="ticker-chip" style="border-color:${color};color:${color}">` +
      `${info.display_name} <button data-ticker="${key}" type="button">✕</button></span>`
    ).join('');
    chipsArea.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        selected.delete(btn.dataset.ticker);
        renderChips();
        renderOptions(searchInput.value);
        renderChart();
      });
    });
  }

  function renderChart() {
    if (selected.size === 0) {
      chartArea.style.display = 'none';
      return;
    }
    chartArea.style.display = 'block';

    whenPlotlyReady(() => {
      const traces = [];
      for (const [, { info, data, color }] of selected) {
        let yVals, hoverTpl, yTitle;
        if (currentView === 'normalized') {
          const first = data.close[0];
          yVals = data.close.map(v => ((v / first) - 1) * 100);
          hoverTpl = '%{x|%Y-%m-%d}<br>%{y:+.1f}%<extra>' + info.display_name + '</extra>';
          yTitle = 'Change from Start (%)';
        } else {
          yVals = data.close;
          hoverTpl = '%{x|%Y-%m-%d}<br>$%{y:,.2f}<extra>' + info.display_name + '</extra>';
          yTitle = 'Price (USD)';
        }
        traces.push({
          x: data.dates, y: yVals, type: 'scatter', mode: 'lines',
          name: info.display_name, line: { color, width: 2 },
          hovertemplate: hoverTpl,
        });
      }

      const layout = {
        font: { family: 'Arial, Helvetica, sans-serif', color: '#0a1f44', size: 12 },
        paper_bgcolor: 'white', plot_bgcolor: 'white',
        margin: { l: 55, r: 20, t: 10, b: 45 },
        xaxis: {
          gridcolor: '#e8f2fe', showline: true, linecolor: '#6a7aa2',
          rangeselector: { buttons: [
            { count: 6, label: '6M', step: 'month', stepmode: 'backward' },
            { count: 1, label: '1Y', step: 'year', stepmode: 'backward' },
            { count: 5, label: '5Y', step: 'year', stepmode: 'backward' },
            { step: 'all', label: 'All' },
          ]},
        },
        yaxis: { gridcolor: '#e8f2fe', showline: true, linecolor: '#6a7aa2', title: traces.length ? (currentView === 'normalized' ? 'Change from Start (%)' : 'Price (USD)') : '' },
        hovermode: 'x unified',
        legend: { orientation: 'h', y: -0.18, x: 0.5, xanchor: 'center' },
        height: 480,
      };

      Plotly.react(chartDiv, traces, layout, { responsive: true, displayModeBar: true, displaylogo: false });
    });
  }

  // Toggle dropdown
  toggle.addEventListener('click', () => {
    const open = dropdown.style.display !== 'none';
    dropdown.style.display = open ? 'none' : 'block';
    if (!open) { searchInput.focus(); renderOptions(); }
  });

  searchInput.addEventListener('input', () => renderOptions(searchInput.value));

  // Close dropdown on outside click
  document.addEventListener('click', e => {
    if (!container.querySelector('.ticker-picker').contains(e.target)) {
      dropdown.style.display = 'none';
    }
  });

  renderOptions();

  // Auto-load defaults (S&P 500 + Bitcoin)
  const defaults = tickerData.metadata.defaults || [];
  if (defaults.length > 0) {
    const loadPromises = defaults.map(ticker => {
      const info = findTickerInfo(ticker);
      if (!info || !info.data_path) return Promise.resolve();
      const color = TRACE_COLORS[nextColor++ % TRACE_COLORS.length];
      return fetch(info.data_path)
        .then(r => r.json())
        .then(data => { selected.set(ticker, { info, data, color }); })
        .catch(() => {});
    });
    Promise.all(loadPromises).then(() => {
      renderChips();
      renderOptions();
      renderChart();
    });
  }
}