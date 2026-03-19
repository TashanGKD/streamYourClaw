# Contributing Themes

This guide explains how to create and contribute visual themes for streamYourClaw.

## Overview

Themes allow customization of the frontend appearance. Each theme is a CSS file that overrides the default color variables.

## Theme Structure

### Default Theme Variables

```css
:root {
    /* Background colors */
    --bg-primary: #0d1117;      /* Main background */
    --bg-secondary: #161b22;    /* Secondary background */
    --bg-tertiary: #21262d;     /* Tertiary background */

    /* Text colors */
    --text-primary: #c9d1d9;    /* Main text */
    --text-secondary: #8b949e;  /* Secondary text */

    /* Accent colors */
    --accent-blue: #58a6ff;     /* Primary accent */
    --accent-green: #3fb950;    /* Success */
    --accent-yellow: #d29922;   /* Warning */
    --accent-red: #f85149;      /* Error */
    --accent-purple: #a371f7;   /* Special states */

    /* UI colors */
    --border-color: #30363d;    /* Borders */
    --shadow-color: rgba(0, 0, 0, 0.3);  /* Shadows */

    /* Animation */
    --transition-speed: 0.3s;
}
```

## Creating a Theme

### Step 1: Create Theme File

Create a new CSS file in `frontend/css/themes/`:

```
frontend/css/themes/
├── default.css
├── dark-purple.css    # Your new theme
└── ocean-blue.css
```

### Step 2: Define Variables

```css
/* frontend/css/themes/dark-purple.css */

/* Dark Purple Theme */
:root {
    /* Background - Deep purple tones */
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-tertiary: #0f3460;

    /* Text */
    --text-primary: #eaeaea;
    --text-secondary: #a0a0a0;

    /* Accents - Vibrant purple/blue */
    --accent-blue: #7b2cbf;
    --accent-green: #00ff88;
    --accent-yellow: #ffd60a;
    --accent-red: #ff4757;
    --accent-purple: #9d4edd;

    /* UI */
    --border-color: #2d2d44;
    --shadow-color: rgba(0, 0, 0, 0.5);
}

/* Optional: Additional theme-specific styles */
.theme-dark-purple .mindmap-node {
    box-shadow: 0 0 10px var(--accent-purple);
}

.theme-dark-purple .status-indicator {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
}
```

### Step 3: Register Theme

Update `frontend/index.html` to include theme selection:

```html
<!-- Add theme stylesheet -->
<link rel="stylesheet" href="css/themes/dark-purple.css" id="theme-stylesheet" disabled>

<!-- Theme selector (optional) -->
<select id="theme-selector">
    <option value="default">Default</option>
    <option value="dark-purple">Dark Purple</option>
</select>
```

Add JavaScript for theme switching:

```javascript
// Theme switching logic
function setTheme(themeName) {
    // Disable all theme stylesheets
    document.querySelectorAll('[id^="theme-"]').forEach(el => {
        el.disabled = true;
    });

    // Enable selected theme
    if (themeName !== 'default') {
        const themeEl = document.getElementById(`theme-${themeName}`);
        if (themeEl) themeEl.disabled = false;
    }

    // Save preference
    localStorage.setItem('theme', themeName);
}

// Load saved theme
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'default';
    setTheme(savedTheme);
});
```

## Theme Categories

### Dark Themes

Suitable for long streaming sessions, easy on the eyes.

```css
/* Example: Midnight */
:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --accent-blue: #4fc3f7;
}
```

### Light Themes

Bright and clean appearance.

```css
/* Example: Light Mode */
:root {
    --bg-primary: #ffffff;
    --bg-secondary: #f5f5f5;
    --text-primary: #1a1a1a;
    --accent-blue: #1976d2;
}
```

### Vibrant Themes

Colorful and energetic.

```css
/* Example: Neon */
:root {
    --bg-primary: #0d0d0d;
    --accent-blue: #00ffff;
    --accent-green: #00ff00;
    --accent-purple: #ff00ff;
}
```

## Design Guidelines

1. **Contrast**: Ensure text is readable against backgrounds
2. **Consistency**: All colors should work together harmoniously
3. **Accessibility**: Check color contrast ratios (WCAG AA minimum)
4. **State Colors**: Keep success/warning/error colors distinguishable

## Testing Your Theme

1. Apply your theme locally
2. Check all UI elements:
   - Mindmap nodes
   - Status indicators
   - Log entries
   - Video container
3. Test with different content lengths
4. Verify in browser dev tools

## Submitting a Theme

1. Create theme CSS file in `frontend/css/themes/`
2. Update `index.html` with theme registration
3. Add theme screenshot (optional) in `docs/assets/themes/`
4. Submit PR with title: `[Theme] Add YourThemeName theme`

### PR Template

```markdown
## Theme Contribution

**Theme Name**: dark-purple
**Category**: Dark

### Description
A deep purple theme with vibrant accents.

### Color Palette
- Primary Background: #1a1a2e
- Secondary Background: #16213e
- Primary Accent: #7b2cbf
- Success Color: #00ff88

### Checklist
- [ ] All CSS variables defined
- [ ] Tested with all UI components
- [ ] Accessible contrast ratios
- [ ] Theme registered in index.html
```

## Theme Gallery

Contributed themes will be showcased in the project documentation.