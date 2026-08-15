import streamlit as st

LOGO_PRE_ENEM_BASE64 = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAaQAAADQCAYAAABIiBVWAAD2K0lEQVR42uz9ebRk13XeCf72OefeGN6UcwJIJIbESBIgSBAiOIriIJIiJZmiLduSq1Qa3NUeukqu8iqvql69alX3H+1aq5d7uapctlx22RosarAGarAoioMoziRIkMREAMQ8ZCIzkeMbIuLee87uP865N27Ei5f5MpEgEuzYXI+Jl/leRNx7zzl7729/+9uiqsrc5ja3uc1tbq+wmfktmNvc5ja3uc0d0tzmNre5zW1uc4c0t7nNbW5zmzukuc1tbnOb29zmDmluc5vb3OY2d0hzm9vc5ja3uc0d0tzmNre5zW3ukOY2t7nNbW5zmzukuc1tbnOb29whzW1uc5vb3OY2d0hzm9vc5ja3uUOa29zmNre5zW3ukOY2t7nNbW5zhzS3uc1tbnOb29whzW1uc5vb3OYOaW5zm9vc5ja3uUOa29zmNre5zR3S3OY2t7nNbW5zhzS3uc1tbnObO6S5zW1uc5vb3OYOaW5zm9vc5jZ3SHOb29zmNre5zR3S3OY2t7nNbe6Q5ja3uc1tbnN7mc29XC+sqj/QN05E5qtnbnOb29zmGdLc5ja3uc1t7pDmNre5zW1uc5s7pLnNbW5zm9sPql26GpI2/weAKOgPQJllVi1sXj+a29zmNrfL1SHVZ3ZofS8gQJD4bUCaf9QJ17W1XdixL+M3Ri/oY0tyMgKItp2qTv6UXtQHm9vc5ja3uW3nFNeLoMPNPJeDRocUQvyJoGAt6oQBwlAVI4IIDICi7QzO4WJkCwclW3ym6b8738UJEbe0CrlED23xiPcYAiIm3SiDxTSeVmWeKc1tbnOb2yueIUkrGWqcgwKq8QvAWFThLMq6COsirA1Lzm5scDKUjGTsLky7lBXGmYgBJBi0/lmJuZaim5xV41d17MpUJr+vP23925L+yQTFlCV7l3rsXVpkxVlyK2ShxAEOwWryQnXqZ3W+euY2t7nN7ZV2SO0MRDalGwZUGGlg1LEcRXlyfZWnz57h8ImTPHf8RVZDIFgbHYMKpv0qXlovF/9dRcdfhOigpvxB45AEpHYeAhLGzkeI38fMxlABQwnkAn2UK5eWuHbvHvYvLnH1Qo+D3YxFEXpecKF2tgqW5vXnNre5zW1ul8ZeEmQ3mSEl96SgBl4YFRyzGQ+fPsFXn3qMx06fpnSWCkfIcoLNkqMwE+wHCTTfx5qOjDMktPlvQc+Bx7UzpFY2RPxeElDnjaHIQLwnK0v6KAsCmfcc7Hf44Ruu45adO9npYVnBacrSDKiVOWQ3t7nNbW6vdIY0q36jIvh0/nvgbJ5xz+FjfOWJR3muGLCxuEhlHYMyoDZDTBYzrMZB1C8+huwEwTS4myawLdaoROOPjn9NNjmkiP6NnVMD9CmAQa2hdCBSIQjreM7gsdZy/MxpyieeJNyQc2t/gdxCH0FsoMH65ja3uc1tbq+sQ2q8kEwS7EYow3LESJSvPnOELzx7mCPMAMFsoMH65ja3uc1tbpfgkGQIhh5Q7QAAAABJRU5ErkJggg=="""

def inject_custom_theme():
    """Aplica o design system exato do Pré-Enem Digital MT com fontes Baloo 2, Inter, IBM Plex Mono e cores oficiais."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

    :root {{
        --teal: #2FC9D2;
        --teal-dark: #1FA8B0;
        --yellow: #FDDE40;
        --yellow-dark: #E8C520;
        --coral: #F2564F;
        --coral-dark: #DC3E3A;
        --ink: #0C535E;
        --ink-soft: #4A7B83;
        --paper: #FBFEFE;
        --paper-tint: #EAFAFA;
        --paper-card: #FFFFFF;
        --line: #DDF0EF;
        --panel-bg: #073036;
        --panel-card: #0E454D;
        --panel-line: rgba(255,255,255,.14);
        --panel-text: #F3FBFB;
        --panel-sub: #9FD3D3;
        --font-display: 'Baloo 2', system-ui, sans-serif;
        --font-body: 'Inter', system-ui, sans-serif;
        --font-mono: 'IBM Plex Mono', monospace;
    }}

    /* Global Typography & Background */
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        font-family: var(--font-body) !important;
        background-color: var(--paper) !important;
        color: var(--ink) !important;
    }}

    /* Top decorative brand blobs */
    .brand-blob {{
        position: absolute;
        z-index: 0;
        border-radius: 50%;
        opacity: .16;
        filter: blur(2px);
        pointer-events: none;
    }}
    .blob1 {{ width: 220px; height: 220px; background: var(--teal); top: -40px; right: 20px; }}
    .blob2 {{ width: 140px; height: 140px; background: var(--yellow); top: 100px; right: 180px; opacity: .14; }}

    /* Typography */
    h1, h2, h3, .stHeading {{
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        color: var(--ink) !important;
    }}
    h1 {{ font-size: clamp(26px, 4vw, 36px) !important; letter-spacing: -0.01em !important; }}
    h2 {{ font-size: 22px !important; font-weight: 600 !important; }}
    h3 {{ font-size: 18px !important; }}
    p, span, label, div {{
        font-family: var(--font-body);
        color: var(--ink);
    }}

    /* Brand Header Box */
    .brand-header-box {{
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }}
    .brand-header-box img {{
        height: 54px;
        width: auto;
        display: block;
    }}
    .eyebrow-text {{
        font-family: var(--font-mono) !important;
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--ink-soft);
        margin: 0 0 4px;
        font-weight: 600;
    }}

    /* Card Component */
    .pre-card {{
        background: var(--paper-card);
        border: 2px solid var(--line);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 3px 0 var(--line);
    }}

    /* Identification PIN Card */
    .pin-display-card {{
        background: var(--paper-card);
        border: 2.5px solid var(--teal);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(47, 201, 210, 0.15);
        margin: 16px 0 24px 0;
    }}
    .pin-display-card .pin-number {{
        font-family: var(--font-mono);
        font-size: 44px;
        font-weight: 700;
        color: var(--ink);
        letter-spacing: 10px;
        margin: 8px 0;
        background: var(--paper-tint);
        display: inline-block;
        padding: 4px 24px;
        border-radius: 12px;
        border: 2px dashed var(--teal);
    }}

    /* Tags de Dificuldade */
    .tag-diff {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: var(--font-mono);
        font-size: 11px;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: .04em;
        font-weight: 700;
    }}
    .tag-facil {{ background: rgba(47,201,210,.18); color: var(--teal-dark); border: 1px solid var(--teal); }}
    .tag-medio {{ background: rgba(253,222,64,.25); color: #8a6f00; border: 1px solid var(--yellow-dark); }}
    .tag-dificil {{ background: rgba(242,86,79,.18); color: var(--coral-dark); border: 1px solid var(--coral); }}

    /* Streamlit Form Input Fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        border: 2px solid var(--line) !important;
        border-radius: 12px !important;
        font-family: var(--font-body) !important;
        font-size: 14.5px !important;
        background: var(--paper-tint) !important;
        color: var(--ink) !important;
        padding: 10px 14px !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {{
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 2px rgba(47,201,210,0.2) !important;
    }}

    /* Buttons */
    .stButton button[kind="primary"], div.stButton > button:first-child {{
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 12px 28px !important;
        background: var(--teal) !important;
        color: #043338 !important;
        box-shadow: 0 3px 0 rgba(0,0,0,.15) !important;
        transition: transform .12s ease, box-shadow .12s ease !important;
    }}
    .stButton button[kind="primary"]:hover, div.stButton > button:first-child:hover {{
        background: var(--teal-dark) !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }}
    .stButton button[kind="secondary"] {{
        background: #ffffff !important;
        color: var(--ink) !important;
        border: 2px solid var(--line) !important;
        border-radius: 999px !important;
        box-shadow: none !important;
    }}

    /* Radio Question Bubbles Styling */
    div[data-testid="stRadio"] > div {{
        gap: 10px;
    }}
    div[data-testid="stRadio"] label {{
        background: var(--paper-card);
        border: 2px solid var(--line);
        border-radius: 16px;
        padding: 10px 16px !important;
        transition: all 0.15s ease-in-out;
        cursor: pointer;
        display: flex;
        align-items: center;
        margin-bottom: 6px;
    }}
    div[data-testid="stRadio"] label:hover {{
        border-color: var(--teal) !important;
        background: var(--paper-tint) !important;
    }}
    div[data-testid="stRadio"] label[data-checked="true"], 
    div[data-testid="stRadio"] label:has(input:checked) {{
        border-color: var(--teal) !important;
        background: rgba(47,201,210,.14) !important;
        font-weight: 600 !important;
    }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: var(--panel-bg) !important;
        color: var(--panel-text) !important;
        border-right: 1px solid var(--panel-line) !important;
    }}
    [data-testid="stSidebar"] * {{
        color: var(--panel-text) !important;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        background: var(--panel-card) !important;
        border-color: var(--panel-line) !important;
        color: var(--panel-text) !important;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
        border-color: var(--teal) !important;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 2px solid var(--line);
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: var(--font-display) !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 10px 20px !important;
        border-radius: 12px 12px 0 0 !important;
        color: var(--ink-soft) !important;
        background: transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: var(--ink) !important;
        border-bottom: 3px solid var(--teal) !important;
        background: var(--paper-tint) !important;
    }}

    /* Score Reveal Big Box */
    .score-reveal-box {{
        text-align: center;
        padding: 28px 20px;
        background: var(--paper-card);
        border: 2px solid var(--line);
        border-radius: 20px;
        box-shadow: 0 4px 16px rgba(12,83,94,.08);
    }}
    .score-big {{
        font-family: var(--font-mono);
        font-size: 58px;
        font-weight: 700;
        color: var(--ink);
        line-height: 1;
        margin: 10px 0;
    }}
    .score-label {{
        font-family: var(--font-mono);
        font-size: 12.5px;
        color: var(--ink-soft);
        text-transform: uppercase;
        letter-spacing: .1em;
        font-weight: 600;
    }}
    .score-msg {{
        font-family: var(--font-display);
        font-size: 20px;
        font-weight: 700;
        margin-top: 10px;
        color: var(--ink);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_brand_header(title: str, subtitle: str = "Simulador TRI · Pré-Enem Digital MT"):
    """Renderiza o cabeçalho oficial com o logo do Pré-Enem Digital MT e tipografia correspondente."""
    html = f"""
    <div style="position: relative; margin-bottom: 12px;">
        <span class="brand-blob blob1"></span>
        <span class="brand-blob blob2"></span>
        <div class="brand-header-box">
            <img src="{LOGO_PRE_ENEM_BASE64}" alt="Pré-Enem Digital MT">
        </div>
        <p class="eyebrow-text">{subtitle}</p>
        <h1 style="margin: 0 0 6px 0;">{title}</h1>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
