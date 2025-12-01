// Theme Toggle
document.addEventListener('DOMContentLoaded', function() {
    // Theme aus localStorage laden oder System-Präferenz verwenden
    const theme = localStorage.getItem('theme') || 
                  (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    document.documentElement.classList.toggle('dark', theme === 'dark');
    
    // Theme Toggle Button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDark = document.documentElement.classList.toggle('dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });
    }
    
    // Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
    
    function toggleMobileMenu() {
        const isOpen = sidebar.classList.contains('open');
        if (isOpen) {
            sidebar.classList.remove('open');
            if (mobileMenuOverlay) {
                mobileMenuOverlay.classList.add('hidden');
            }
        } else {
            sidebar.classList.add('open');
            if (mobileMenuOverlay) {
                mobileMenuOverlay.classList.remove('hidden');
            }
        }
    }
    
    function closeMobileMenu() {
        sidebar.classList.remove('open');
        if (mobileMenuOverlay) {
            mobileMenuOverlay.classList.add('hidden');
        }
    }
    
    if (mobileMenuBtn && sidebar) {
        // Toggle Menu beim Klick auf Button
        mobileMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleMobileMenu();
        });
        
        // Schließe Menu beim Klick auf Overlay
        if (mobileMenuOverlay) {
            mobileMenuOverlay.addEventListener('click', function() {
                closeMobileMenu();
            });
        }
        
        // Schließe Menu beim Klick außerhalb
        document.addEventListener('click', function(event) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnMenuBtn = mobileMenuBtn.contains(event.target);
            const isClickOnOverlay = mobileMenuOverlay && mobileMenuOverlay.contains(event.target);
            
            if (!isClickInsideSidebar && !isClickOnMenuBtn && !isClickOnOverlay && sidebar.classList.contains('open')) {
                closeMobileMenu();
            }
        });
        
        // Verhindere Event-Bubbling beim Klick innerhalb der Sidebar
        sidebar.addEventListener('click', function(e) {
            e.stopPropagation();
        });
        
        // Schließe Menu beim Klick auf einen Link (für bessere UX)
        const sidebarLinks = sidebar.querySelectorAll('a');
        sidebarLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                // Prüfe ob Mobile Menu aktiv sein sollte (Portrait oder sehr schmal)
                const isMobile = window.innerWidth <= 1024 && 
                                 (window.innerHeight > window.innerWidth || window.innerWidth <= 768);
                if (isMobile) {
                    closeMobileMenu();
                }
            });
        });
        
        // Schließe Menu automatisch bei Orientierungswechsel zu Landscape
        window.addEventListener('orientationchange', function() {
            setTimeout(function() {
                // Wenn im Landscape-Modus (Breite > Höhe), schließe Menu
                if (window.innerWidth > window.innerHeight && window.innerWidth >= 769) {
                    closeMobileMenu();
                }
            }, 100);
        });
        
        // Schließe Menu auch bei Resize, wenn zu Landscape gewechselt wird
        window.addEventListener('resize', function() {
            // Wenn im Landscape-Modus (Breite > Höhe) und breit genug, schließe Menu
            if (window.innerWidth > window.innerHeight && window.innerWidth >= 769) {
                closeMobileMenu();
            }
        });
    }
    
    // Auto-hide Flash Messages (nur Nachrichten, keine Buttons)
    const flashMessages = document.querySelectorAll('.bg-red-100, .bg-green-100, .bg-yellow-100, .bg-blue-100, .bg-red-900, .bg-green-900, .bg-yellow-900, .bg-blue-900');
    flashMessages.forEach(function(msg) {
        if (msg.textContent.trim() && !msg.querySelector('button') && !msg.querySelector('a[class*="bg-"]')) {
            setTimeout(function() {
                msg.style.transition = 'opacity 0.5s';
                msg.style.opacity = '0';
                setTimeout(function() {
                    msg.remove();
                }, 500);
            }, 5000);
        }
    });
    
    // Form Validation Enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500');
                } else {
                    field.classList.remove('border-red-500');
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                alert('Bitte fülle alle Pflichtfelder aus.');
            }
        });
    });
    
    // Search Input Debounce (für zukünftige Live-Search)
    const searchInputs = document.querySelectorAll('input[type="text"][name="search"]');
    searchInputs.forEach(function(input) {
        let timeout;
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                // Optional: Live-Search hier implementieren
            }, 300);
        });
    });
});

// Drag & Drop für Aktivitäten (wird später erweitert)
function initDragAndDrop() {
    // Wird in zukünftiger Version implementiert
    console.log('Drag & Drop initialisiert');
}

// Live-Tracking Helper
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    return `${hours}:${minutes}`;
}

function getCurrentTime() {
    const now = new Date();
    return {
        hours: now.getHours(),
        minutes: now.getMinutes(),
        seconds: now.getSeconds(),
        weekday: now.getDay() === 0 ? 6 : now.getDay() - 1 // 0=Montag, 6=Sonntag
    };
}

// Export für andere Scripts
window.CoachManager = {
    formatTime: formatTime,
    getCurrentTime: getCurrentTime,
    initDragAndDrop: initDragAndDrop
};


