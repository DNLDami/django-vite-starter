import 'vite/modulepreload-polyfill';
import './css/main.css';
import htmx from 'htmx.org';
import Alpine from 'alpinejs'

// make Alpine globally accessible
window.Alpine = Alpine
 
Alpine.start()


// make htmx globally accessible
window.htmx = htmx

document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('toggleDarkMode');
    const root = document.documentElement;
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        root.classList.add('dark');
        toggle.checked = true;
    } else {
        root.classList.remove('dark');
        toggle.checked = false;
    }
    toggle.addEventListener('change', () => {
        if (toggle.checked) {
            root.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            root.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    });
});