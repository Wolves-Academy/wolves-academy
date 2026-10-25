// Same theme as the in-browser Tailwind used before; build: see README "Styling"
const RGB = (v) => `rgb(var(--${v}) / <alpha-value>)`;
module.exports = {
  content: ['./templates/**/*.html', './static/sw.js'],
  theme: { extend: {
    colors: {
      bg: RGB('paper'), card: RGB('sheet'), card2: RGB('sheet-2'), card3: RGB('sheet-3'),
      edge: RGB('rule'), edge2: RGB('rule-soft'),
      accent: RGB('acc-text'), accent2: RGB('acc-text'), ink: RGB('ink'), ink2: RGB('ink-2'), dim: RGB('muted'), faint: RGB('faint'),
      ok: RGB('ok'), warn: RGB('warn'), bad: RGB('bad'), violet: RGB('acc-text'), wa: RGB('wa'),
    },
    fontFamily: { sans: ['Montserrat', 'Tajawal', 'system-ui', 'sans-serif'] },
    borderRadius: { none: '0', DEFAULT: '3px', sm: '2px', md: '3px', lg: '4px', xl: '5px', '2xl': '6px', '3xl': '8px', full: '999px' },
  } },
};
