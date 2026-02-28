"""Cyberpunk terminal theme for the Streamlit app."""

DESIGN_SYSTEM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Oxanium:wght@500;600;700;800&display=swap');

:root {
    --bg-0: #010203;
    --bg-1: #04070d;
    --bg-2: #080d16;
    --panel: rgba(4, 8, 14, 0.94);
    --panel-strong: rgba(2, 5, 10, 0.97);
    --line: rgba(0, 246, 255, 0.16);
    --line-strong: rgba(0, 246, 255, 0.38);
    --hot: #ff2bd6;
    --cyan: #00f6ff;
    --cyan-dim: #7de9ff;
    --lime: #8dff5f;
    --warn: #ffb000;
    --error: #ff4d6d;
    --text: #eaf7ff;
    --muted: #86a7be;
    --shadow: 0 0 0 1px rgba(0, 246, 255, 0.03), 0 22px 70px rgba(0, 0, 0, 0.78);
    --radius: 0px;
    --mono: 'IBM Plex Mono', SFMono-Regular, Menlo, monospace;
    --display: 'Oxanium', 'IBM Plex Mono', monospace;
}

* {
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: var(--mono);
}

#MainMenu, header, footer:not(.app-footer) {
    visibility: hidden;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(circle at 15% 15%, rgba(255, 43, 214, 0.05), transparent 24%),
        radial-gradient(circle at 85% 8%, rgba(0, 246, 255, 0.04), transparent 26%),
        linear-gradient(rgba(0, 246, 255, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 246, 255, 0.035) 1px, transparent 1px),
        linear-gradient(180deg, #000000, var(--bg-0) 18%, var(--bg-1) 52%, #02040a 100%);
    background-size: auto, auto, 26px 26px, 26px 26px, auto;
}

.block-container {
    max-width: 1140px !important;
    padding: 44px 24px 36px !important;
}

.main .block-container {
    padding-top: 28px !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 18px;
    align-items: stretch;
}

.search-form-marker,
.panel-marker {
    display: none;
}

@keyframes boot {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero-shell {
    max-width: 860px;
    margin: 0 auto 18px;
    padding: 22px 24px 18px;
    text-align: center;
    border: 1px solid var(--line);
    background:
        linear-gradient(90deg, rgba(255, 43, 214, 0.03), transparent 18%, transparent 82%, rgba(0, 246, 255, 0.03)),
        var(--panel);
    box-shadow: var(--shadow);
    position: relative;
    animation: boot 160ms ease-out;
}

.hero-shell::before,
.hero-shell::after,
div[data-testid="stForm"]::before,
div[data-testid="stForm"]::after,
.result-shell::before,
.result-shell::after,
.status-card::before,
.status-card::after,
.empty-guidance::before,
.empty-guidance::after,
div[data-testid="column"]:has(.panel-marker--map)::before,
div[data-testid="column"]:has(.panel-marker--map)::after,
div[data-testid="column"]:has(.panel-marker--actions)::before,
div[data-testid="column"]:has(.panel-marker--actions)::after {
    content: "";
    position: absolute;
    width: 14px;
    height: 14px;
    border-color: var(--line-strong);
    border-style: solid;
    pointer-events: none;
}

.hero-shell::before,
div[data-testid="stForm"]::before,
.result-shell::before,
.status-card::before,
.empty-guidance::before,
div[data-testid="column"]:has(.panel-marker--map)::before,
div[data-testid="column"]:has(.panel-marker--actions)::before {
    top: -1px;
    left: -1px;
    border-width: 2px 0 0 2px;
}

.hero-shell::after,
div[data-testid="stForm"]::after,
.result-shell::after,
.status-card::after,
.empty-guidance::after,
div[data-testid="column"]:has(.panel-marker--map)::after,
div[data-testid="column"]:has(.panel-marker--actions)::after {
    right: -1px;
    bottom: -1px;
    border-width: 0 2px 2px 0;
}

.hero-badge,
.result-badge,
.empty-kicker,
.status-meta,
.result-section-label,
.metric-label,
.detail-key,
.panel-kicker,
.terminal-label {
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: var(--cyan);
    text-shadow: 0 0 10px rgba(0, 246, 255, 0.35);
}

.hero-title {
    margin: 12px 0 0;
    font-family: var(--display);
    font-size: clamp(2.3rem, 5vw, 4.6rem);
    font-weight: 800;
    line-height: 1;
    letter-spacing: 0.02em;
    color: var(--text);
    text-shadow:
        0 0 12px rgba(0, 246, 255, 0.12),
        0 0 22px rgba(255, 43, 214, 0.08);
}

.hero-subtitle,
.hero-note,
.hero-helper,
.search-caption,
.example-shell,
.panel-copy,
.panel-note,
.empty-body,
.result-subnote {
    display: none !important;
}

div[data-testid="stForm"] {
    max-width: 860px;
    margin: 0 auto 22px;
    padding: 22px;
    border: 1px solid var(--line);
    background:
        linear-gradient(180deg, rgba(6, 10, 18, 0.99), rgba(1, 3, 7, 0.99));
    box-shadow: var(--shadow);
    position: relative;
}

.stForm {
    border: none !important;
    background: transparent !important;
}

.terminal-label {
    margin-bottom: 12px;
    color: var(--hot);
    text-align: left;
}

.stTextInput > div > div > input {
    min-height: 58px !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--line-strong) !important;
    background: rgba(0, 2, 6, 0.96) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 1rem !important;
    padding: 16px 18px !important;
    box-shadow:
        inset 0 0 0 1px rgba(255, 43, 214, 0.08),
        0 0 0 1px rgba(0, 246, 255, 0.03) !important;
    transition: border-color 120ms ease, box-shadow 120ms ease !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(134, 167, 190, 0.85) !important;
    opacity: 1;
}

.stTextInput > div > div > input:hover {
    border-color: var(--cyan) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--cyan) !important;
    box-shadow:
        inset 0 0 0 1px rgba(255, 43, 214, 0.15),
        0 0 0 1px rgba(0, 246, 255, 0.08),
        0 0 18px rgba(0, 246, 255, 0.14) !important;
}

.stFormSubmitButton > button,
.stButton > button,
.stDownloadButton > button,
.stLinkButton > a {
    min-height: 50px !important;
    border-radius: var(--radius) !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    transition:
        border-color 120ms ease,
        box-shadow 120ms ease,
        transform 120ms ease,
        background-color 120ms ease !important;
}

.stFormSubmitButton > button {
    border: 1px solid rgba(0, 246, 255, 0.9) !important;
    background:
        linear-gradient(90deg, rgba(0, 246, 255, 0.12), rgba(255, 43, 214, 0.1)) !important;
    color: var(--text) !important;
    box-shadow:
        inset 0 0 0 1px rgba(0, 246, 255, 0.08),
        0 0 18px rgba(0, 246, 255, 0.1) !important;
}

.stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    border-color: var(--hot) !important;
    box-shadow:
        inset 0 0 0 1px rgba(255, 43, 214, 0.08),
        0 0 20px rgba(255, 43, 214, 0.12) !important;
}

.stButton > button,
.stDownloadButton > button,
.stLinkButton > a {
    border: 1px solid var(--line) !important;
    background: rgba(3, 6, 12, 0.94) !important;
    color: var(--text) !important;
    box-shadow: none !important;
    text-decoration: none !important;
}

.stLinkButton > a {
    border-color: rgba(0, 246, 255, 0.45) !important;
    background: linear-gradient(90deg, rgba(0, 246, 255, 0.08), rgba(0, 246, 255, 0.02)) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stLinkButton > a:hover {
    transform: translateY(-1px) !important;
    border-color: var(--hot) !important;
    box-shadow: 0 0 16px rgba(255, 43, 214, 0.08) !important;
}

.stTextInput > div > div > input:focus-visible,
.stFormSubmitButton > button:focus-visible,
.stButton > button:focus-visible,
.stDownloadButton > button:focus-visible,
.stLinkButton > a:focus-visible {
    outline: 2px solid var(--cyan) !important;
    outline-offset: 2px !important;
}

.status-card,
.empty-guidance,
.result-shell,
div[data-testid="column"]:has(.panel-marker--map),
div[data-testid="column"]:has(.panel-marker--actions) {
    position: relative;
}

.status-card {
    max-width: 860px;
    margin: 0 auto 18px;
    padding: 18px 20px;
    border: 1px solid var(--line);
    background: var(--panel-strong);
    box-shadow: var(--shadow);
    animation: boot 140ms ease-out;
}

.status-card--info {
    border-color: rgba(0, 246, 255, 0.28);
}

.status-card--warning {
    border-color: rgba(255, 176, 0, 0.34);
}

.status-card--error {
    border-color: rgba(255, 77, 109, 0.34);
}

.status-meta {
    color: var(--cyan);
    text-shadow: 0 0 10px rgba(0, 246, 255, 0.24);
}

.status-title {
    margin: 10px 0 6px;
    font-family: var(--display);
    font-size: 1.15rem;
    color: var(--text);
    letter-spacing: 0.04em;
}

.status-body,
.status-hint {
    margin: 0;
    color: var(--muted);
    font-size: 0.9rem;
    line-height: 1.55;
}

.status-hint {
    margin-top: 4px;
}

.empty-guidance {
    max-width: 860px;
    margin: 12px auto 0;
    padding: 18px 20px;
    border: 1px solid var(--line);
    background: var(--panel);
    box-shadow: var(--shadow);
    text-align: center;
}

.empty-kicker {
    color: var(--hot);
}

.empty-title {
    margin: 10px 0 0;
    font-family: var(--display);
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text);
}

.result-shell {
    max-width: 980px;
    margin: 24px auto 16px;
    padding: 22px;
    border: 1px solid var(--line);
    background:
        linear-gradient(180deg, rgba(5, 8, 15, 0.99), rgba(1, 2, 6, 0.99));
    box-shadow: var(--shadow);
    animation: boot 160ms ease-out;
}

.result-badge {
    display: inline-flex;
    align-items: center;
    color: var(--lime);
    text-shadow: 0 0 12px rgba(141, 255, 95, 0.18);
}

.result-section-label,
.metric-label,
.detail-key {
    color: var(--muted);
}

.result-section-label {
    margin-top: 16px;
}

.result-address {
    margin-top: 12px;
    color: var(--text);
    font-size: clamp(1.2rem, 2vw, 2rem);
    font-weight: 700;
    line-height: 1.4;
    word-break: break-word;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    margin-top: 22px;
}

.metric-card {
    min-height: 112px;
    padding: 16px;
    border: 1px solid rgba(0, 246, 255, 0.14);
    background:
        linear-gradient(180deg, rgba(6, 10, 18, 0.96), rgba(1, 3, 7, 0.96));
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 12px;
}

.metric-card--highlight {
    border-color: rgba(0, 246, 255, 0.34);
    box-shadow:
        inset 0 0 0 1px rgba(255, 43, 214, 0.05),
        0 0 18px rgba(0, 246, 255, 0.05);
}

.metric-value {
    color: var(--text);
    font-size: 1.12rem;
    font-weight: 700;
    line-height: 1.4;
    word-break: break-word;
}

.metric-value--mono {
    font-family: var(--mono);
    color: var(--cyan-dim);
    text-shadow: 0 0 10px rgba(0, 246, 255, 0.08);
}

.metric-value--query {
    unicode-bidi: plaintext;
}

.detail-strip {
    max-width: 980px;
    margin: 0 auto 16px;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
}

.detail-item {
    padding: 14px 16px;
    border: 1px solid rgba(0, 246, 255, 0.12);
    background: rgba(2, 5, 10, 0.94);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}

.detail-value {
    color: var(--text);
    font-size: 0.82rem;
    font-weight: 600;
    text-align: right;
}

div[data-testid="column"]:has(.panel-marker--map),
div[data-testid="column"]:has(.panel-marker--actions) {
    padding: 18px;
    border: 1px solid var(--line);
    background: var(--panel-strong);
    box-shadow: var(--shadow);
}

.panel-kicker {
    color: var(--hot);
}

.panel-title {
    margin: 10px 0 16px;
    font-family: var(--display);
    font-size: 1.12rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text);
}

div[data-testid="column"]:has(.panel-marker--map) div[data-testid="stDeckGlJsonChart"] {
    border: 1px solid rgba(0, 246, 255, 0.18);
    overflow: hidden;
}

.stSpinner > div {
    border-color: var(--cyan) !important;
}

.app-footer {
    max-width: 980px;
    margin: 26px auto 0;
    padding-top: 14px;
    border-top: 1px solid rgba(0, 246, 255, 0.14);
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: var(--muted);
    text-transform: uppercase;
}

.footer-divider {
    color: var(--hot);
}

@media (max-width: 768px) {
    .block-container {
        padding: 24px 14px 30px !important;
    }

    .hero-shell,
    div[data-testid="stForm"],
    .status-card,
    .empty-guidance {
        max-width: 100%;
        padding: 16px;
    }

    .hero-title {
        font-size: 2rem;
    }

    .result-shell,
    div[data-testid="column"]:has(.panel-marker--map),
    div[data-testid="column"]:has(.panel-marker--actions) {
        padding: 16px;
    }

    .metrics-grid,
    .detail-strip {
        grid-template-columns: 1fr;
    }

    .detail-item {
        align-items: flex-start;
        flex-direction: column;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    .stFormSubmitButton > button,
    .stButton > button,
    .stDownloadButton > button,
    .stLinkButton > a {
        min-height: 48px !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation: none !important;
        transition: none !important;
        scroll-behavior: auto !important;
    }
}
</style>
"""
