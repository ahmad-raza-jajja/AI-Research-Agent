/**
 * AI Research Agent Dashboard JavaScript
 * Handles theme switching, sidebar toggle, preferences persistence, and UI enhancements
 */

// ===== CONFIGURATION =====
const CONFIG = {
  themes: ['Light', 'Dark', 'Cyberpunk'],
  defaultTheme: 'Light',
  storageKeys: {
    theme: 'aiResearchAgent_theme',
    sidebarCollapsed: 'aiResearchAgent_sidebarCollapsed'
  },
  selectors: {
    app: '.stApp',
    sidebar: '.stSidebar',
    summaryBox: '.summary-box',
    themeToggle: '.theme-toggle-btn',
    sidebarToggle: '.sidebar-toggle-btn'
  }
};

// ===== UTILITY FUNCTIONS =====
// Simple debounce function to limit function calls
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

// Check if user prefers reduced motion
function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// Safe localStorage operations with fallback
function safeLocalStorage() {
  try {
    return window.localStorage;
  } catch (e) {
    console.warn('localStorage not available, using session storage');
    return {
      getItem: (key) => sessionStorage.getItem(key),
      setItem: (key, value) => sessionStorage.setItem(key, value),
      removeItem: (key) => sessionStorage.removeItem(key)
    };
  }
}

const storage = safeLocalStorage();

// ===== THEME MANAGEMENT =====
function setTheme(theme) {
  if (!CONFIG.themes.includes(theme)) {
    console.warn(`Invalid theme: ${theme}. Using default.`);
    theme = CONFIG.defaultTheme;
  }
  
  const appElement = document.querySelector(CONFIG.selectors.app);
  if (appElement) {
    appElement.setAttribute('data-theme', theme);
    storage.setItem(CONFIG.storageKeys.theme, theme);
    
    // Dispatch custom event for other components
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
  }
}

function getTheme() {
  return storage.getItem(CONFIG.storageKeys.theme) || CONFIG.defaultTheme;
}

function toggleTheme() {
  const currentTheme = getTheme();
  const currentIndex = CONFIG.themes.indexOf(currentTheme);
  const nextIndex = (currentIndex + 1) % CONFIG.themes.length;
  setTheme(CONFIG.themes[nextIndex]);
}

function resetTheme() {
  setTheme(CONFIG.defaultTheme);
}

function randomTheme() {
  const randomIndex = Math.floor(Math.random() * CONFIG.themes.length);
  setTheme(CONFIG.themes[randomIndex]);
}

// ===== SIDEBAR MANAGEMENT =====
function toggleSidebar() {
  const sidebar = document.querySelector(CONFIG.selectors.sidebar);
  const appElement = document.querySelector(CONFIG.selectors.app);
  
  if (sidebar && appElement) {
    const isCollapsed = sidebar.classList.contains('collapsed');
    
    if (isCollapsed) {
      sidebar.classList.remove('collapsed');
      appElement.setAttribute('data-sidebar-collapsed', 'false');
      storage.setItem(CONFIG.storageKeys.sidebarCollapsed, 'false');
    } else {
      sidebar.classList.add('collapsed');
      appElement.setAttribute('data-sidebar-collapsed', 'true');
      storage.setItem(CONFIG.storageKeys.sidebarCollapsed, 'true');
    }
    
    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('sidebarToggled', { 
      detail: { collapsed: !isCollapsed } 
    }));
  }
}

function applySavedSidebarState() {
  const isCollapsed = storage.getItem(CONFIG.storageKeys.sidebarCollapsed) === 'true';
  const sidebar = document.querySelector(CONFIG.selectors.sidebar);
  const appElement = document.querySelector(CONFIG.selectors.app);
  
  if (sidebar && appElement && isCollapsed) {
    sidebar.classList.add('collapsed');
    appElement.setAttribute('data-sidebar-collapsed', 'true');
  }
}

// ===== UI ENHANCEMENTS =====
function decorateSummaryBox(summaryBox) {
  // Only decorate once per element
  if (summaryBox.querySelector('.summary-icon')) return;
  
  // Add icon
  const icon = document.createElement('div');
  icon.className = 'summary-icon';
  icon.innerHTML = '📊'; // Simple emoji icon
  icon.style.cssText = `
    position: absolute;
    top: 12px;
    right: 12px;
    font-size: 16px;
    opacity: 0.7;
  `;
  summaryBox.style.position = 'relative';
  summaryBox.appendChild(icon);
  
  // Add subtle progress bar (cosmetic)
  const progressBar = document.createElement('div');
  progressBar.className = 'summary-progress';
  progressBar.style.cssText = `
    position: absolute;
    bottom: 0;
    left: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
    width: 0%;
    transition: width 0.3s ease;
    border-radius: 0 0 8px 8px;
  `;
  summaryBox.appendChild(progressBar);
  
  // Animate progress bar on first appearance
  if (!prefersReducedMotion()) {
    setTimeout(() => {
      progressBar.style.width = '100%';
      setTimeout(() => {
        progressBar.style.opacity = '0.3';
      }, 300);
    }, 100);
  } else {
    progressBar.style.width = '100%';
    progressBar.style.opacity = '0.3';
  }
}

function enhanceNewElements() {
  // Decorate summary boxes
  const summaryBoxes = document.querySelectorAll(CONFIG.selectors.summaryBox);
  summaryBoxes.forEach(decorateSummaryBox);
  
  // Add any other dynamic enhancements here
}

// ===== STREAMLIT INTEGRATION =====
// Helper to trigger Streamlit input event - Usage: triggerStreamlitInput(inputElement, 'new value')
function triggerStreamlitInput(inputElement, value) {
  if (!inputElement) return;
  
  inputElement.value = value;
  inputElement.dispatchEvent(new Event('input', { bubbles: true }));
  inputElement.dispatchEvent(new Event('change', { bubbles: true }));
}

// ===== DOM MUTATION OBSERVER =====
let mutationObserver;

function setupMutationObserver() {
  if (mutationObserver) {
    mutationObserver.disconnect();
  }
  
  const debouncedEnhance = debounce(enhanceNewElements, 250);
  
  mutationObserver = new MutationObserver((mutations) => {
    let shouldEnhance = false;
    
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        // Check if any added nodes contain elements we care about
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.matches && (
              node.matches(CONFIG.selectors.summaryBox) ||
              node.querySelector(CONFIG.selectors.summaryBox)
            )) {
              shouldEnhance = true;
            }
          }
        });
      }
    });
    
    if (shouldEnhance) {
      debouncedEnhance();
    }
  });
  
  // Start observing
  const appElement = document.querySelector(CONFIG.selectors.app) || document.body;
  mutationObserver.observe(appElement, {
    childList: true,
    subtree: true
  });
}

// ===== EVENT HANDLERS =====
function attachEventHandlers() {
  // Theme toggle buttons
  document.addEventListener('click', (e) => {
    if (e.target.matches(CONFIG.selectors.themeToggle)) {
      e.preventDefault();
      toggleTheme();
    }
    
    if (e.target.matches(CONFIG.selectors.sidebarToggle)) {
      e.preventDefault();
      toggleSidebar();
    }
  });
  
  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Shift + T for theme toggle
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
      e.preventDefault();
      toggleTheme();
    }
    
    // Ctrl/Cmd + Shift + S for sidebar toggle
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
      e.preventDefault();
      toggleSidebar();
    }
  });
  
  // Listen for theme changes from other sources
  window.addEventListener('themeChanged', (e) => {
    console.log('Theme changed to:', e.detail.theme);
  });
  
  // Listen for sidebar changes
  window.addEventListener('sidebarToggled', (e) => {
    console.log('Sidebar collapsed:', e.detail.collapsed);
  });
}

// ===== INITIALIZATION =====
function initUI() {
  try {
    // Apply saved theme
    const savedTheme = getTheme();
    setTheme(savedTheme);
    
    // Apply saved sidebar state
    applySavedSidebarState();
    
    // Enhance existing elements
    enhanceNewElements();
    
    // Setup mutation observer for dynamic content
    setupMutationObserver();
    
    // Attach event handlers
    attachEventHandlers();
    
    // Set up responsive sidebar for mobile
    const handleResize = debounce(() => {
      const sidebar = document.querySelector(CONFIG.selectors.sidebar);
      if (sidebar && window.innerWidth <= 768) {
        sidebar.classList.add('mobile');
      } else if (sidebar) {
        sidebar.classList.remove('mobile');
      }
    }, 250);
    
    window.addEventListener('resize', handleResize);
    handleResize(); // Call once on init
    
    console.log('AI Research Agent Dashboard initialized');
    
  } catch (error) {
    console.error('Error initializing UI:', error);
  }
}

// ===== CLEANUP =====
function cleanup() {
  if (mutationObserver) {
    mutationObserver.disconnect();
  }
}

// Handle page unload
window.addEventListener('beforeunload', cleanup);

// ===== AUTO-INITIALIZATION =====
// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initUI);
} else {
  // DOM is already loaded
  initUI();
}

// Also handle Streamlit's dynamic loading
const streamlitReady = setInterval(() => {
  const appElement = document.querySelector(CONFIG.selectors.app);
  if (appElement && !appElement.hasAttribute('data-ai-agent-initialized')) {
    appElement.setAttribute('data-ai-agent-initialized', 'true');
    initUI();
    clearInterval(streamlitReady);
  }
}, 500);

// Clear the interval after 10 seconds to avoid infinite checking
setTimeout(() => {
  clearInterval(streamlitReady);
}, 10000);

// ===== GLOBAL API =====
// Expose functions to global scope for external access
window.AIResearchAgent = {
  setTheme,
  getTheme,
  toggleTheme,
  resetTheme,
  randomTheme,
  toggleSidebar,
  initUI,
  triggerStreamlitInput,
  cleanup
};