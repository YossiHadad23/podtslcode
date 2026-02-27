"""Premium CSS Design System."""

DESIGN_SYSTEM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --void: #05060a;
    --obsidian: #0a0c11;
    --onyx: #0f1218;
    --graphite: #161925;
    --slate: #1f2433;
    --silver: #6b7280;
    --cloud: #9ca3af;
    --snow: #f9fafb;
    
    --accent-dark: #4f46e5;
    --accent: #6366f1;
    --accent-light: #818cf8;
    --accent-glow: rgba(99, 102, 241, 0.35);
    --accent-glow-strong: rgba(99, 102, 241, 0.6);
    
    --success: #10b981;
    --success-glow: rgba(16, 185, 129, 0.25);
    --warning: #f59e0b;
    --error: #ef4444;
    
    --gradient-brand: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --gradient-brand-alt: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
    --gradient-dark: linear-gradient(180deg, #0f1218 0%, #05060a 100%);
    --gradient-card: linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, rgba(139, 92, 246, 0.02) 100%);
    --gradient-glow: radial-gradient(ellipse at center, rgba(99, 102, 241, 0.12) 0%, transparent 70%);
    --gradient-success: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.02) 100%);
    
    --glass-bg: rgba(18, 21, 26, 0.7);
    --glass-border: rgba(99, 102, 241, 0.15);
    
    --shadow-xs: 0 1px 3px -1px rgba(0, 0, 0, 0.2);
    --shadow-sm: 0 2px 8px -2px rgba(0, 0, 0, 0.25);
    --shadow-md: 0 4px 16px -4px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 12px 32px -8px rgba(0, 0, 0, 0.4);
    --shadow-xl: 0 20px 48px -12px rgba(0, 0, 0, 0.5);
    --shadow-glow: 0 0 40px -8px var(--accent-glow);
    --shadow-glow-strong: 0 0 60px -10px var(--accent-glow-strong);
    
    --space-1: 4px;
    --space-2: 8px;
    --space-3: 12px;
    --space-4: 16px;
    --space-5: 24px;
    --space-6: 32px;
    --space-7: 48px;
    --space-8: 64px;
    --space-9: 96px;
    
    --radius-xs: 6px;
    --radius-sm: 10px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 28px;
    --radius-2xl: 36px;
    --radius-full: 9999px;
    
    --ease-smooth: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
    --ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.stApp {
    background: var(--void);
    font-family: 'Inter', 'Heebo', -apple-system, BlinkMacSystemFont, sans-serif;
}

#MainMenu, footer, header {visibility: hidden;}

.block-container {
    max-width: 900px !important;
    padding: var(--space-7) var(--space-5) !important;
    margin: 0 auto !important;
}

.main .block-container {
    padding-top: var(--space-6) !important;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.96); }
    to { opacity: 1; transform: scale(1); }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
}

@keyframes glow {
    0%, 100% { box-shadow: 0 0 30px var(--accent-glow); }
    50% { box-shadow: 0 0 50px var(--accent-glow-strong); }
}

@keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

.brand-header {
    text-align: center;
    padding: var(--space-8) 0 var(--space-7);
    position: relative;
    animation: fadeUp 0.9s var(--ease-smooth);
}

.brand-header::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 450px;
    height: 450px;
    background: var(--gradient-glow);
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 0;
    filter: blur(70px);
    opacity: 0.7;
}

.brand-logo {
    position: relative;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    background: var(--gradient-brand);
    border-radius: var(--radius-xl);
    margin-bottom: var(--space-5);
    box-shadow: var(--shadow-glow-strong);
    animation: float 5s ease-in-out infinite;
    transition: all 0.5s var(--ease-smooth);
}

.brand-logo:hover {
    transform: translateY(-4px) scale(1.05);
    box-shadow: var(--shadow-glow-strong), var(--shadow-lg);
}

.brand-logo-icon {
    font-size: 36px;
    filter: brightness(1.3) drop-shadow(0 2px 8px rgba(0,0,0,0.3));
}

.brand-title {
    position: relative;
    z-index: 1;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--cloud) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 2px 20px rgba(99, 102, 241, 0.3);
}

.brand-tagline {
    position: relative;
    z-index: 1;
    color: var(--silver);
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-top: var(--space-4);
    opacity: 0.8;
}

.search-container {
    position: relative;
    max-width: 720px;
    margin: 0 auto var(--space-8);
    animation: fadeUp 0.9s var(--ease-smooth) 0.1s both;
}

.stTextInput > div > div > input {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(20px) !important;
    border: 1.5px solid var(--glass-border) !important;
    border-radius: var(--radius-xl) !important;
    color: var(--snow) !important;
    font-size: 1.05rem !important;
    font-weight: 400 !important;
    padding: 22px 28px !important;
    transition: all 0.4s var(--ease-smooth) !important;
    box-shadow: var(--shadow-md) !important;
}

.stTextInput > div > div > input:hover {
    border-color: rgba(99, 102, 241, 0.25) !important;
    background: rgba(18, 21, 26, 0.8) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12), var(--shadow-lg) !important;
    background: var(--graphite) !important;
    transform: translateY(-1px);
}

.stTextInput > div > div > input::placeholder {
    color: var(--silver) !important;
    opacity: 0.6;
}

.stButton > button {
    background: var(--gradient-brand) !important;
    border: none !important;
    border-radius: var(--radius-lg) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 18px 32px !important;
    transition: all 0.4s var(--ease-smooth) !important;
 text-transform: none !important;
    box-shadow: var(--shadow-md) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.6s;
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-glow), var(--shadow-lg) !important;
}

.stButton > button:active {
    transform: translateY(0px) scale(0.98) !important;
}

.result-card {
    position: relative;
    background: var(--glass-bg);
    backdrop-filter: blur(30px);
    border: 1.5px solid var(--glass-border);
    border-radius: var(--radius-2xl);
    padding: var(--space-8);
    text-align: center;
    margin: var(--space-7) auto;
    max-width: 820px;
    overflow: hidden;
    animation: scaleIn 0.6s var(--ease-smooth);
    box-shadow: var(--shadow-xl);
}

.result-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--gradient-brand);
    box-shadow: 0 2px 12px var(--accent-glow);
}

.result-card::after {
    content: "";
    position: absolute;
    top: 30%;
    left: 50%;
    width: 600px;
    height: 600px;
    background: var(--gradient-glow);
    transform: translate(-50%, -50%);
    pointer-events: none;
    opacity: 0.4;
    filter: blur(80px);
}

.result-status {
    position: relative;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    background: var(--gradient-success);
    backdrop-filter: blur(10px);
    border: 1.5px solid rgba(16, 185, 129, 0.3);
    color: var(--success);
    padding: var(--space-2) var(--space-5);
    border-radius: var(--radius-full);
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: var(--space-6);
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.2);
    animation: slideDown 0.5s var(--ease-smooth);
}

.result-status::before {
    content: "";
    width: 8px;
    height: 8px;
    background: var(--success);
    border-radius: 50%;
    animation: pulse 2.5s infinite;
    box-shadow: 0 0 8px var(--success);
}

.result-address {
    position: relative;
    z-index: 1;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--snow);
    line-height: 1.7;
    max-width: 680px;
    margin: 0 auto;
    animation: fadeIn 0.7s 0.2s both;
}

.data-card {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    border: 1.5px solid rgba(99, 102, 241, 0.1);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    transition: all 0.4s var(--ease-smooth);
    box-shadow: var(--shadow-sm);
}

.data-card:hover {
    border-color: rgba(99, 102, 241, 0.3);
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
    background: rgba(18, 21, 26, 0.85);
}

.data-label {
    font-size: 0.65rem;
    font-weight: 800;
    color: var(--silver);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: var(--space-4);
    display: flex;
    align-items: center;
    gap: var(--space-2);
    opacity: 0.9;
}

.data-value {
    font-family: 'Space Grotesk', monospace;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--accent-light);
    text-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

.stDownloadButton > button,
.stLinkButton > a {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(15px) !important;
    border: 1.5px solid rgba(99, 102, 241, 0.15) !important;
    border-radius: var(--radius-md) !important;
    color: var(--snow) !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    padding: 14px 24px !important;
    transition: all 0.4s var(--ease-smooth) !important;
    text-decoration: none !important;
    box-shadow: var(--shadow-sm) !important;
}

.stDownloadButton > button:hover,
.stLinkButton > a:hover {
    border-color: var(--accent) !important;
    background: rgba(99, 102, 241, 0.1) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}

.empty-state {
    text-align: center;
    padding: var(--space-8) var(--space-5) var(--space-9);
    animation: fadeUp 0.9s var(--ease-smooth) 0.2s both;
}

.empty-illustration {
    font-size: 6rem;
    margin-bottom: var(--space-6);
    animation: float 6s ease-in-out infinite;
    filter: drop-shadow(0 8px 24px rgba(99, 102, 241, 0.25));
    opacity: 0.95;
}

.empty-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--snow);
    margin-bottom: var(--space-4);
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.empty-description {
    font-size: 1.05rem;
    color: var(--cloud);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
    opacity: 0.9;
}

.streamlit-expanderHeader {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(15px) !important;
    border: 1.5px solid rgba(99, 102, 241, 0.1) !important;
    border-radius: var(--radius-md) !important;
    color: var(--cloud) !important;
    font-weight: 700 !important;
    padding: var(--space-5) !important;
    transition: all 0.3s var(--ease-smooth) !important;
}

.streamlit-expanderHeader:hover {
    border-color: rgba(99, 102, 241, 0.3) !important;
    color: var(--snow) !important;
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm) !important;
}

.streamlit-expanderContent {
    background: var(--obsidian) !important;
    border: 1.5px solid rgba(99, 102, 241, 0.1) !important;
    border-top: none !important;
    border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
    padding: var(--space-6) !important;
    animation: slideDown 0.3s ease;
}

div[data-testid="stCodeBlock"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

div[data-testid="stCodeBlock"] pre {
    background: var(--obsidian) !important;
    border: 1.5px solid rgba(99, 102, 241, 0.1) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--accent-light) !important;
    font-family: 'Space Grotesk', 'JetBrains Mono', monospace !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    padding: var(--space-5) !important;
    box-shadow: var(--shadow-sm) !important;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.2), transparent) !important;
    margin: var(--space-8) 0 !important;
}

.stAlert {
    border-radius: var(--radius-md) !important;
    border: 1.5px solid rgba(99, 102, 241, 0.2) !important;
    backdrop-filter: blur(10px) !important;
    animation: slideDown 0.3s ease;
}

::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: var(--obsidian);
}

::-webkit-scrollbar-thumb {
    background: var(--slate);
    border-radius: var(--radius-full);
    border: 2px solid var(--obsidian);
    transition: background 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--silver);
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--snow);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    margin-bottom: var(--space-5);
    letter-spacing: -0.01em;
}

.stSpinner > div {
    border-color: var(--accent) !important;
}

.stForm {
    border: none !important;
    background: transparent !important;
}

@media (max-width: 768px) {
    .block-container {
        max-width: 100% !important;
        padding: var(--space-5) var(--space-4) !important;
    }

    .main .block-container {
        padding-top: var(--space-4) !important;
    }

    .brand-header {
        padding: var(--space-6) 0 var(--space-5);
    }

    .brand-header::before {
        width: 280px;
        height: 280px;
        filter: blur(50px);
    }

    .brand-logo {
        width: 64px;
        height: 64px;
        margin-bottom: var(--space-4);
    }

    .brand-logo-icon {
        font-size: 28px;
    }

    .brand-title {
        font-size: 2.1rem;
        line-height: 1.15;
    }

    .brand-tagline {
        font-size: 0.72rem;
        letter-spacing: 0.18em;
    }

    .stTextInput > div > div > input {
        font-size: 1rem !important;
        padding: 16px 18px !important;
        border-radius: var(--radius-lg) !important;
    }

    .result-card,
    .data-card,
    .streamlit-expanderContent {
        padding: var(--space-5) !important;
        border-radius: var(--radius-md) !important;
    }

    .result-address {
        font-size: 1.2rem;
        line-height: 1.5;
    }

    .empty-state {
        padding: var(--space-6) var(--space-3) var(--space-7);
    }

    .empty-illustration {
        font-size: 4.4rem;
    }

    .empty-title {
        font-size: 1.6rem;
    }

    .empty-description {
        font-size: 0.95rem;
        line-height: 1.55;
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
    }

    .stDownloadButton > button,
    .stLinkButton > a,
    .stButton > button,
    .stFormSubmitButton > button {
        width: 100% !important;
        min-height: 44px !important;
        padding: 12px 14px !important;
        font-size: 0.9rem !important;
    }
}

</style>
"""
