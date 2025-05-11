import 'vite/modulepreload-polyfill';
import './css/main.css';
import htmx from 'htmx.org';
import Alpine from 'alpinejs';
import focus from '@alpinejs/focus';

// add the focus plugin
Alpine.plugin(focus)

// make Alpine globally accessible
window.Alpine = Alpine
 
Alpine.start()


// make htmx globally accessible
window.htmx = htmx

// the toggleDarkModeDesktop and toggleDarkModeMobile darkmode feature
document.addEventListener('DOMContentLoaded', () => {
    const toggleDarkModeDesktop = document.getElementById('toggleDarkModeDesktop');
    const toggleDarkModeMobile = document.getElementById('toggleDarkModeMobile');
    const root = document.documentElement;
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        root.classList.add('dark');
        toggleDarkModeDesktop.checked = true;
        toggleDarkModeMobile.checked = true;
    } else {
        root.classList.remove('dark');
        toggleDarkModeDesktop.checked = false;
        toggleDarkModeMobile.checked = false;
    }
    toggleDarkModeDesktop.addEventListener('change', () => {
        if (toggleDarkModeDesktop.checked) {
            root.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            toggleDarkModeMobile.checked = true;
        } else {
            root.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            toggleDarkModeMobile.checked = false;
        }
    });
    toggleDarkModeMobile.addEventListener('change', () => {
        if (toggleDarkModeMobile.checked) {
            root.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            toggleDarkModeDesktop.checked = true;
        } else {
            root.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            toggleDarkModeDesktop.checked = false;
        }
    });
});

// This updates the avatar
const fileInput = document.querySelector('input[type="file"]');
if (fileInput) {
    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        const image = document.querySelector('#avatar');
    
        if (file && file.type.includes('image')) {
            const url = URL.createObjectURL(file);
            image.src = url;
        }
    });
}

// This updates the name
const display_nameInput = document.getElementById('id_displayname');
const display_nameOutput = document.getElementById('displayname');

if (display_nameInput) {
    display_nameInput.addEventListener('input', (event) => {
        display_nameOutput.innerText = event.target.value;
    });
}