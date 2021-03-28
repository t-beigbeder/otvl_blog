const colors = require('tailwindcss/colors')

module.exports = {
  purge: {
    // enabled: true,
    content: [
      './public/**/*.html',
      './src/**/*.vue',
  ]},
  theme: {
    colors: {
      // Build your palette here
      transparent: 'transparent',
      current: 'currentColor',
      gray: colors.coolGray,
      red: colors.red,
      blue: colors.lightBlue,
      yellow: colors.amber,
    },
    boxShadow: {
      md: '0 1px 5px rgba(0,0,0,0.2),0 2px 2px rgba(0,0,0,0.24),0 3px 1px -2px rgba(0,0,0,0.36)',
      lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    }
  },
  variants: {},
  plugins: [
  ],
};