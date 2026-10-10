# OOPSIE Browser Extension Specification & Guide

This document outlines the architecture and integration roadmap for the **OOPSIE Browser Extension** (Chrome Manifest V3 / Firefox WebExtensions).

## Extension Features
1. **One-Click Error Capture**: Highlight error text on Vercel build logs, Netlify deploy pages, GitHub Actions, or local web apps -> Right-click -> "Analyze with OOPSIE".
2. **DevTools Panel**: Adds an "OOPSIE Recovery" tab to Chrome Developer Tools console, capturing unhandled runtime exceptions automatically.
3. **Floating Copilot Widget**: Slide-out panel providing immediate plain-English explanations and copyable repair prompts directly inside browser-based IDEs (Replit, Bolt.new, Lovable, Cursor web).

## Folder Structure (`/extension/`)
```
/extension
  ├── manifest.json       # Chrome Extension Manifest V3 configuration
  ├── background.js      # Service worker for context menu & API calls
  ├── content.js         # Page inspector & error selector script
  ├── popup.html         # Extension popup interface
  ├── popup.js           # Extension popup application logic
  └── styles.css         # Modern glassmorphism UI styles
```

## How to Test the Scaffolding
1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable "Developer mode" in the top right.
3. Click "Load unpacked" and select the `c:\Users\onyxe\Desktop\OOPSIE\extension` directory.
4. Click the OOPSIE extension icon or right-click any selected text to open the error analyzer.
