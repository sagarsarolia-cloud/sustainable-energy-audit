/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    dark: '#0B1120', // Deep Slate/Green
                    card: '#151F32', // Lighter Slate
                    green: '#059669', // Emerald 600
                    light: '#34D399', // Emerald 400
                    accent: '#F59E0B', // Amber 500
                }
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(10px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                }
            }
        },
    },
    plugins: [],
}
