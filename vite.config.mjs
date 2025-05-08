import {defineConfig} from 'vite';
import {resolve} from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    base: "/static/",
    build: {
        manifest: "manifest.json",
        outDir: resolve("./static"),
        rollupOptions: {
            input: {
                asset: resolve('./vite_entry_point/entry_point.js')
            },
            output: {
                entryFileNames: 'js/main.js',
                assetFileNames: assetInfo => {
                    if (assetInfo.names && assetInfo.names.endsWith('.css')) {
                        return 'css/style.css';
                    }
                    return 'assets/[name][extname]';
                }
            },
        },
        cssCodeSplit: false
    },
    plugins: [
        tailwindcss(),
    ],
})