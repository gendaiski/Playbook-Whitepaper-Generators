# Accord native WhitePaperBuilder adapter

Build from unchanged WhitePaperBuilder source using Python3, Node and build-time PostCSS 8.5.28. Runtime requires no npm dependencies/CDN/backend.

`WHITEPAPER_UPSTREAM=/path/to/WhitePaperBuilder WHITEPAPER_OUTPUT=/path/to/app/modules/whitepaper-generator POSTCSS_MODULE=/path/to/node_modules/postcss python build-native.py`

Exports async mount(host,{theme}) => {dispose,setTheme,save,api}. Original seven-tab editing, visual editors, OSINT/manual citations, project JSON, live Paged.js pagination and print retained. Native scoped DOM, never an iframe. Original fonts, pagination and citation code embedded locally; MIT and third-party notices preserved.

Storage: accord-whitepaper-paper-v1, accord-whitepaper-theme-v1 and accord-whitepaper-tab-v1. Export project JSON for backups; this is separate from Accord workspace backup. Starter research placeholders remain labelled. No AI/model service is implied. Native print CSS prints only the whitepaper; Chromium PDF acceptance is separate from OS print dialog behavior.
