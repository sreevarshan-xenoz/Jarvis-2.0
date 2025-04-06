# Jarvis Themes Directory

This directory contains theme files for the Jarvis Voice Assistant UI.

Themes are stored as JSON files with the following structure:

```json
{
  "name": "Theme Name",
  "description": "Theme description",
  "colors": {
    "bg_dark": "#hex_color",
    "bg_medium": "#hex_color",
    "bg_gradient_top": "#hex_color",
    "bg_gradient_bottom": "#hex_color",
    "accent": "#hex_color",
    "accent_glow": "#hex_color",
    "accent_secondary": "#hex_color",
    "text": "#hex_color",
    "text_dim": "#hex_color",
    "success": "#hex_color",
    "warning": "#hex_color",
    "error": "#hex_color"
  },
  "animation": {
    "intensity": 1.0,
    "complexity": 1.0,
    "particle_count": 50,
    "wave_complexity": 1.0
  },
  "fonts": {
    "title": {"family": "Font Family", "size": 28, "weight": "bold"},
    "subtitle": {"family": "Font Family", "size": 11, "weight": "normal"},
    "text": {"family": "Font Family", "size": 12, "weight": "normal"},
    "status": {"family": "Font Family", "size": 11, "weight": "bold"},
    "footer": {"family": "Font Family", "size": 10, "weight": "normal"}
  }
}
```

## Built-in Themes

- **Dark**: Default dark theme with blue accents
- **Light**: Light theme with blue accents
- **High Contrast**: High contrast theme for accessibility
- **Cyberpunk**: Futuristic cyberpunk theme with neon colors
- **Minimal**: Clean, minimalist theme with reduced animations

## Custom Themes

You can create custom themes by adding new JSON files to this directory. The theme manager will automatically load them on startup.