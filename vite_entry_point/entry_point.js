import 'vite/modulepreload-polyfill';
import '../static/css/main.css';
import htmx from 'htmx.org';
import Alpine from 'alpinejs'

// make Alpine globally accessible
window.Alpine = Alpine
 
Alpine.start()


// make htmx globally accessible
window.htmx = htmx
