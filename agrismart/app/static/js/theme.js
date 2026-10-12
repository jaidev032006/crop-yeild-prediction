// Theme Management (Universal Dark / Light Mode)
const htmlElement = document.documentElement;

// Get saved theme or default to system/light
const savedTheme = localStorage.getItem('theme') || 'light';
htmlElement.setAttribute('data-theme', savedTheme);
document.addEventListener('DOMContentLoaded', () => {
    updateAllThemeIcons(savedTheme);
    setupThemeToggleListeners();
});

function setupThemeToggleListeners() {
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn, #theme-toggle');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const currentTheme = htmlElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateAllThemeIcons(newTheme);
        });
    });
}

function updateAllThemeIcons(theme) {
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn, #theme-toggle');
    toggleBtns.forEach(btn => {
        const icon = btn.querySelector('i, svg');
        if (icon) {
            if (theme === 'dark') {
                icon.setAttribute('data-lucide', 'sun');
                btn.setAttribute('title', 'Switch to Light Mode');
            } else {
                icon.setAttribute('data-lucide', 'moon');
                btn.setAttribute('title', 'Switch to Dark Mode');
            }
        }
    });
    if (window.lucide) {
        window.lucide.createIcons();
    }
}


// Close dropdowns when clicking outside
document.addEventListener('click', (e) => {
    const userMenu = document.querySelector('.user-menu');
    const userBtn = document.querySelector('.user-btn');
    
    if (userMenu && !userMenu.contains(e.target)) {
        userMenu.classList.remove('active');
    }
});

// User menu toggle
document.querySelector('.user-btn')?.addEventListener('click', (e) => {
    e.stopPropagation();
    const dropdown = e.target.closest('.user-menu');
    dropdown?.classList.toggle('active');
});
