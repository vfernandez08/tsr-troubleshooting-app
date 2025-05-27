// Dark Mode Toggle Functionality
class DarkModeManager {
    constructor() {
        this.toggle = document.getElementById('darkModeToggle');
        this.icon = this.toggle.querySelector('i');
        this.init();
    }

    init() {
        // Check for saved theme preference or default to light mode
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);

        // Add click event listener
        this.toggle.addEventListener('click', () => {
            this.toggleTheme();
        });
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update button icon and style
        if (theme === 'dark') {
            this.icon.className = 'fas fa-sun';
            this.toggle.title = 'Switch to Light Mode';
        } else {
            this.icon.className = 'fas fa-moon';
            this.toggle.title = 'Switch to Dark Mode';
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme');
    }
}

// Initialize dark mode when page loads
document.addEventListener('DOMContentLoaded', function() {
    new DarkModeManager();
});