// Nova Trader - Interactive Landing Page JavaScript

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive features
    initSmoothScrolling();
    initScrollAnimations();
    initLiveMetrics();
    initPortfolioAnimations();
    initPortfolioInteractions();
    initTechnologyHovers();
    initPerformanceCounters();
    initMobileMenu();
});

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetSection.offsetTop - navbarHeight - 20;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll animations
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    const animatedElements = document.querySelectorAll([
        '.overview-card',
        '.portfolio-card',
        '.performance-card',
        '.arch-layer',
        '.tech-category'
    ].join(','));

    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

// Live metrics simulation
function initLiveMetrics() {
    const metrics = {
        pnl: { element: document.querySelector('.metric-value.positive'), base: 1247, variance: 50 },
        positions: { element: document.querySelector('.metric-value:nth-child(2)'), base: 23, variance: 2 },
        successRate: { element: document.querySelector('.metric-value:nth-child(3)'), base: 78.4, variance: 1.5 }
    };

    function updateMetrics() {
        // Update P&L
        if (metrics.pnl.element) {
            const variation = (Math.random() - 0.5) * metrics.pnl.variance;
            const newValue = Math.round(metrics.pnl.base + variation);
            metrics.pnl.element.textContent = `+£${newValue.toLocaleString()}`;
        }

        // Update positions count
        if (metrics.positions.element) {
            const variation = Math.floor((Math.random() - 0.5) * metrics.positions.variance);
            const newValue = metrics.positions.base + variation;
            metrics.positions.element.textContent = newValue;
        }

        // Update success rate
        const successElements = document.querySelectorAll('.metric-value');
        if (successElements[2]) {
            const variation = (Math.random() - 0.5) * metrics.successRate.variance;
            const newValue = (metrics.successRate.base + variation).toFixed(1);
            successElements[2].textContent = `${newValue}%`;
        }
    }

    // Update metrics every 3 seconds
    setInterval(updateMetrics, 3000);

    // Animate chart bars
    function animateChartBars() {
        const bars = document.querySelectorAll('.bar');
        bars.forEach(bar => {
            const currentHeight = parseInt(bar.style.height);
            const variation = Math.random() * 20 - 10; // ±10% variation
            const newHeight = Math.max(20, Math.min(90, currentHeight + variation));
            bar.style.height = `${newHeight}%`;
        });
    }

    setInterval(animateChartBars, 2000);
}

// Portfolio expand/collapse interactions
function initPortfolioInteractions() {
    const portfolioCards = document.querySelectorAll('.portfolio-card');

    portfolioCards.forEach(card => {
        const expandBtn = card.querySelector('.portfolio-expand-btn');

        if (expandBtn) {
            expandBtn.addEventListener('click', function(e) {
                e.stopPropagation();

                // Close other expanded cards
                portfolioCards.forEach(otherCard => {
                    if (otherCard !== card && otherCard.classList.contains('expanded')) {
                        otherCard.classList.remove('expanded');
                    }
                });

                // Toggle current card
                card.classList.toggle('expanded');

                // Add ripple effect to button
                const ripple = document.createElement('div');
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);

                ripple.style.cssText = `
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: ${size}px;
                    height: ${size}px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.3);
                    transform: translate(-50%, -50%) scale(0);
                    animation: ripple 0.6s ease-out;
                    pointer-events: none;
                    z-index: 1;
                `;

                this.style.position = 'relative';
                this.appendChild(ripple);

                setTimeout(() => {
                    if (ripple.parentNode) {
                        ripple.parentNode.removeChild(ripple);
                    }
                }, 600);
            });
        }
    });
}

// Portfolio allocation animations
function initPortfolioAnimations() {
    const portfolioCards = document.querySelectorAll('.portfolio-card');

    portfolioCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            const allocationBar = this.querySelector('.allocation-fill');
            if (allocationBar) {
                const currentWidth = allocationBar.style.width;
                const numericWidth = parseInt(currentWidth);

                // Subtle animation on hover
                allocationBar.style.transform = 'scaleX(1.02)';
                allocationBar.style.transition = 'transform 0.3s ease';
            }
        });

        card.addEventListener('mouseleave', function() {
            const allocationBar = this.querySelector('.allocation-fill');
            if (allocationBar) {
                allocationBar.style.transform = 'scaleX(1)';
            }
        });
    });

    // Animate allocation bars on scroll
    const portfolioObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const allocationBar = entry.target.querySelector('.allocation-fill');
                if (allocationBar) {
                    const targetWidth = allocationBar.style.width;
                    allocationBar.style.width = '0%';

                    setTimeout(() => {
                        allocationBar.style.width = targetWidth;
                    }, 200);
                }
            }
        });
    }, { threshold: 0.3 });

    portfolioCards.forEach(card => {
        portfolioObserver.observe(card);
    });
}

// Technology section interactions
function initTechnologyHovers() {
    const techItems = document.querySelectorAll('.tech-item');
    const archComponents = document.querySelectorAll('.arch-component');

    // Add hover effects with random delays for organic feel
    [...techItems, ...archComponents].forEach((item, index) => {
        item.addEventListener('mouseenter', function() {
            // Add ripple effect
            const ripple = document.createElement('div');
            ripple.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
                transform: translate(-50%, -50%);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;

            this.style.position = 'relative';
            this.appendChild(ripple);

            setTimeout(() => {
                if (ripple.parentNode) {
                    ripple.parentNode.removeChild(ripple);
                }
            }, 600);
        });
    });

    // Add ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                width: 100px;
                height: 100px;
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Performance counter animations
function initPerformanceCounters() {
    const performanceTargets = document.querySelectorAll('.performance-target');

    const performanceObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const text = target.textContent;
                const isPercentage = text.includes('%');
                const isRatio = text.includes(':');
                const originalValue = text;

                // Animate counting up to the target value
                target.textContent = '0';

                if (isPercentage) {
                    const endValue = parseInt(originalValue);
                    animateCounter(target, 0, endValue, 1000, (val) => `${val}%`);
                } else if (isRatio) {
                    const parts = originalValue.split(':');
                    const endValue = parseFloat(parts[0]);
                    animateCounter(target, 0, endValue, 1000, (val) => `${val.toFixed(1)}:1`);
                } else if (text.includes('-')) {
                    const parts = originalValue.split('-');
                    const startValue = parseInt(parts[0]);
                    const endValue = parseInt(parts[1]);
                    animateCounter(target, 0, endValue, 1500, (val) => `${startValue}-${val}%`);
                } else {
                    target.textContent = originalValue;
                }
            }
        });
    }, { threshold: 0.5 });

    performanceTargets.forEach(target => {
        performanceObserver.observe(target);
    });
}

// Counter animation helper
function animateCounter(element, start, end, duration, formatter) {
    const startTime = performance.now();

    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const currentValue = start + (end - start) * easeOutQuart;

        element.textContent = formatter(Math.floor(currentValue));

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            // Ensure final value is exact
            element.textContent = formatter(end);
        }
    }

    requestAnimationFrame(updateCounter);
}

// Mobile menu functionality
function initMobileMenu() {
    // This would be expanded for a full mobile menu implementation
    const navLinks = document.querySelectorAll('.nav-link');

    // Add mobile touch effects
    navLinks.forEach(link => {
        link.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });

        link.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Dynamic background effects
function initBackgroundEffects() {
    const hero = document.querySelector('.hero');

    // Add floating particles
    function createParticle() {
        const particle = document.createElement('div');
        particle.style.cssText = `
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(0, 102, 255, 0.1);
            border-radius: 50%;
            pointer-events: none;
            animation: float 10s infinite linear;
            left: ${Math.random() * 100}%;
            top: 100%;
        `;

        hero.appendChild(particle);

        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
        }, 10000);
    }

    // Create particles periodically
    setInterval(createParticle, 2000);

    // Add floating animation
    const floatStyle = document.createElement('style');
    floatStyle.textContent = `
        @keyframes float {
            from {
                transform: translateY(0) translateX(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            to {
                transform: translateY(-100vh) translateX(${Math.random() * 200 - 100}px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(floatStyle);
}

// Initialize background effects
initBackgroundEffects();

// Enhanced navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    const scrolled = window.scrollY > 50;

    if (scrolled) {
        navbar.style.background = `
            radial-gradient(ellipse at center, rgba(15, 15, 15, 0.99) 0%, rgba(10, 10, 10, 0.98) 100%),
            linear-gradient(45deg, transparent 25%, rgba(255, 255, 255, 0.02) 25%, rgba(255, 255, 255, 0.02) 50%, transparent 50%, transparent 75%, rgba(255, 255, 255, 0.02) 75%)
        `;
        navbar.style.backgroundSize = 'auto, 4px 4px';
        navbar.style.backdropFilter = 'blur(30px) saturate(1.3)';
        navbar.style.borderBottom = '1px solid rgba(255, 107, 53, 0.4)';
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.6)';
    } else {
        navbar.style.background = `
            radial-gradient(ellipse at center, rgba(20, 20, 20, 0.98) 0%, rgba(15, 15, 15, 0.96) 100%),
            linear-gradient(45deg, transparent 25%, rgba(255, 255, 255, 0.015) 25%, rgba(255, 255, 255, 0.015) 50%, transparent 50%, transparent 75%, rgba(255, 255, 255, 0.015) 75%)
        `;
        navbar.style.backgroundSize = 'auto, 4px 4px';
        navbar.style.backdropFilter = 'blur(25px) saturate(1.2)';
        navbar.style.borderBottom = '1px solid rgba(51, 51, 51, 0.8)';
        navbar.style.boxShadow = '0 1px 8px rgba(0, 0, 0, 0.4)';
    }
});

// Button interactions
document.querySelectorAll('.btn-primary, .btn-secondary, .nav-cta').forEach(button => {
    button.addEventListener('click', function(e) {
        // Add click ripple effect
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            top: ${y}px;
            left: ${x}px;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            animation: buttonRipple 0.6s ease-out;
            pointer-events: none;
        `;

        this.style.position = 'relative';
        this.appendChild(ripple);

        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.parentNode.removeChild(ripple);
            }
        }, 600);
    });
});

// Add button ripple animation
const buttonRippleStyle = document.createElement('style');
buttonRippleStyle.textContent = `
    @keyframes buttonRipple {
        to {
            width: 200px;
            height: 200px;
            opacity: 0;
        }
    }
`;
document.head.appendChild(buttonRippleStyle);

// Console easter egg
console.log(`
%c🚀 Nova Trader Platform v1.0
%cInstitutional-Grade Trading System
%c
Portfolio Value: £76,872
Active Strategies: 10+
Sophistication: 9/10
%c
Ready for algorithmic trading excellence.
`,
'color: #0066ff; font-size: 18px; font-weight: bold;',
'color: #ffd700; font-size: 14px;',
'color: #00c851; font-family: monospace; font-size: 12px;',
'color: #ff6b35; font-size: 12px;'
);