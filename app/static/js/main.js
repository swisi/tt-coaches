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
    
    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
        
        // Schließe Menu beim Klick außerhalb
        document.addEventListener('click', function(event) {
            if (!sidebar.contains(event.target) && !mobileMenuBtn.contains(event.target)) {
                sidebar.classList.remove('open');
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

