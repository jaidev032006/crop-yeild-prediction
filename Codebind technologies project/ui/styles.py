"""
UI CSS Styles and Themes for Streamlit Web Application.
Provides customized Dark and Light themes with mobile-friendly card layouts.
"""

def get_theme_css(theme_mode: str = 'dark') -> str:
    """Generate CSS rules based on selected theme mode."""
    if theme_mode == 'dark':
        bg_primary = "#090d16"
        bg_card = "#111827"
        bg_card_inner = "#1f2937"
        text_primary = "#f9fafb"
        text_muted = "#9ca3af"
        border_color = "rgba(75, 85, 99, 0.4)"
        accent_color = "#10b981"
        badge_bg = "rgba(16, 185, 129, 0.15)"
        gold_color = "#f59e0b"
    else:
        bg_primary = "#f8fafc"
        bg_card = "#ffffff"
        bg_card_inner = "#f1f5f9"
        text_primary = "#0f172a"
        text_muted = "#64748b"
        border_color = "#e2e8f0"
        accent_color = "#059669"
        badge_bg = "rgba(5, 150, 105, 0.1)"
        gold_color = "#d97706"

    return f"""
    <style>
    /* Main container theme overrides */
    .stApp {{
        background-color: {bg_primary};
        color: {text_primary};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    /* Custom Header Banner */
    .advisor-header-card {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_card_inner} 100%);
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }}
    
    .advisor-title {{
        color: {accent_color};
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }}
    
    .advisor-subtitle {{
        color: {text_muted};
        font-size: 1.05rem;
        margin-bottom: 0px;
    }}
    
    /* Recommendation Card Styling */
    .crop-card {{
        background-color: {bg_card};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    
    .crop-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
    }}
    
    .crop-rank-1 {{
        border-left: 6px solid {accent_color};
    }}
    
    .crop-rank-2 {{
        border-left: 6px solid #3b82f6;
    }}
    
    .crop-rank-3 {{
        border-left: 6px solid {gold_color};
    }}
    
    .badge-chip {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: {badge_bg};
        color: {accent_color};
        margin-right: 8px;
    }}
    
    .metric-value-highlight {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {accent_color};
    }}
    
    .profit-pill {{
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
    }}
    
    /* Section Title */
    .section-headline {{
        color: {text_primary};
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    /* Explanatory callout */
    .shap-callout {{
        background-color: {bg_card_inner};
        border-left: 4px solid {accent_color};
        border-radius: 8px;
        padding: 16px;
        color: {text_primary};
        font-size: 1rem;
        margin-bottom: 18px;
    }}
    </style>
    """
