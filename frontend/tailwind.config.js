/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Hospital procurement teal palette
                brand: {
                    50: '#f0fdfa',
                    100: '#ccfbf1',
                    200: '#99f6e4',
                    500: '#14b8a6', // Teal 500
                    600: '#0d9488', // Teal 600
                    700: '#0f766e', // Teal 700
                    900: '#134e4a',
                },
                risk: {
                    low: '#22c55e',    // Green
                    medium: '#f59e0b', // Amber
                    high: '#ef4444',   // Red
                }
            }
        },
    },
    plugins: [],
}
