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
      threshold: 0.1,
      rootMargin: '0px 0px -100px 0px'
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