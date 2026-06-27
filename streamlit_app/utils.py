import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

# Flag code mapping - matches flagcdn.com codes
FLAG_CODES = {
    "Mexico": "mx", "South Korea": "kr", "Czechia": "cz", "South Africa": "za",
    "Switzerland": "ch", "Canada": "ca", "Qatar": "qa", "Bosnia-Herzegovina": "ba",
    "Brazil": "br", "Haiti": "ht", "Morocco": "ma", "Scotland": "gb-sct",
    "Australia": "au", "Paraguay": "py", "Turkey": "tr", "United States": "us",
    "Curaçao": "cw", "Germany": "de", "Ecuador": "ec", "Ivory Coast": "ci",
    "Japan": "jp", "Netherlands": "nl", "Sweden": "se", "Tunisia": "tn",
    "Egypt": "eg", "Belgium": "be", "Iran": "ir", "New Zealand": "nz",
    "Cape Verde Islands": "cv", "Saudi Arabia": "sa", "Spain": "es", "Uruguay": "uy",
    "France": "fr", "Iraq": "iq", "Norway": "no", "Senegal": "sn",
    "Algeria": "dz", "Argentina": "ar", "Jordan": "jo", "Austria": "at",
    "Congo DR": "cd", "Colombia": "co", "Portugal": "pt", "Uzbekistan": "uz",
    "England": "gb-eng", "Ghana": "gh", "Croatia": "hr", "Panama": "pa",
}

THEME = {
    "bg": "#060C1A",
    "card": "#0C1B30",
    "card2": "#122040",
    "muted": "#162340",
    "primary": "#D4A931",
    "foreground": "#EDF2FF",
    "muted_fg": "#7B91B0",
    "border": "rgba(255,255,255,0.07)",
    "green": "#22C55E",
    "red": "#EF4444",
    "blue": "#3B82F6",
}

def get_flag_url(team_name: str, size: int = 40) -> str:
    code = FLAG_CODES.get(team_name, "un")
    return f"https://flagcdn.com/w{size}/{code}.png"

def flag_img(team_name: str, height: int = 20) -> str:
    url = get_flag_url(team_name)
    return f'<img src="{url}" height="{height}" style="border-radius:2px;object-fit:cover;" />'

def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_ANALYTICS_SCHEMA"),
        role=os.getenv("SNOWFLAKE_DBT_ROLE"),
    )

def run_query(sql: str):
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return columns, rows
    finally:
        conn.close()

BASE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Inter:wght@400;500;600&display=swap');

.stApp {{
    background-color: {THEME['bg']};
    color: {THEME['foreground']};
    font-family: 'Inter', sans-serif;
}}

/* Hide Streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 0 !important; max-width: 1200px; }}
div[data-testid="stSidebarNav"] {{ display: none; }}

/* Navigation */
.wc-header {{
    background: {THEME['card']};
    border-bottom: 1px solid {THEME['border']};
    padding: 0 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(8px);
}}

.wc-logo-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 20px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {THEME['foreground']};
    line-height: 1;
}}

.wc-logo-sub {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: {THEME['primary']};
    line-height: 1;
}}

.wc-header-right {{
    display: flex;
    gap: 24px;
    align-items: center;
}}

.wc-header-stat {{
    text-align: right;
}}

.wc-header-stat-label {{
    font-size: 10px;
    color: {THEME['muted_fg']};
    text-transform: uppercase;
    letter-spacing: 0.15em;
}}

.wc-header-stat-value {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: {THEME['foreground']};
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

.wc-divider {{
    width: 1px;
    height: 32px;
    background: {THEME['border']};
}}

/* Section headings */
.wc-section-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 20px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {THEME['foreground']};
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}}

.wc-badge {{
    font-size: 11px;
    color: {THEME['muted_fg']};
    background: {THEME['muted']};
    padding: 2px 10px;
    border-radius: 99px;
    font-weight: 500;
    font-family: 'Inter', sans-serif;
}}

/* Live match cards */
.live-card {{
    background: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}}

.live-card:hover {{
    border-color: rgba(212,169,49,0.3);
}}

.live-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 2px 10px;
    border-radius: 99px;
    background: rgba(239,68,68,0.2);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.3);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
}}

.live-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #f87171;
    animation: pulse 1.5s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.4; }}
}}

.live-minute {{
    font-size: 12px;
    font-weight: 700;
    color: #f87171;
}}

.live-venue {{
    font-size: 11px;
    color: {THEME['muted_fg']};
}}

.live-score {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 42px;
    color: {THEME['foreground']};
    letter-spacing: -1px;
}}

.live-score-sep {{
    color: {THEME['muted_fg']};
    margin: 0 4px;
}}

.live-team {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-align: center;
}}

.live-group {{
    font-size: 10px;
    color: {THEME['muted_fg']};
    text-transform: uppercase;
    letter-spacing: 0.2em;
}}

.progress-bar {{
    height: 3px;
    background: {THEME['muted']};
    border-radius: 99px;
    overflow: hidden;
    margin-top: 16px;
}}

.progress-fill {{
    height: 100%;
    background: #ef4444;
    border-radius: 99px;
}}

.progress-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: {THEME['muted_fg']};
    margin-top: 4px;
}}

/* Match result rows */
.match-row {{
    background: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: background 0.15s;
    margin-bottom: 6px;
}}

.match-row:hover {{
    background: {THEME['card2']};
}}

.match-date {{
    font-size: 11px;
    color: {THEME['muted_fg']};
    width: 120px;
    flex-shrink: 0;
}}

.match-teams {{
    flex: 1;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 12px;
}}

.match-home {{
    display: flex;
    align-items: center;
    gap: 8px;
    justify-content: flex-end;
}}

.match-away {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.match-team-name {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

.match-score {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 18px;
    color: {THEME['foreground']};
    white-space: nowrap;
}}

.match-group {{
    font-size: 11px;
    color: {THEME['muted_fg']};
    width: 64px;
    text-align: right;
    flex-shrink: 0;
}}

/* Upcoming match rows */
.upcoming-row {{
    background: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 6px;
    opacity: 0.85;
}}

.upcoming-time {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    color: {THEME['primary']};
    width: 120px;
    flex-shrink: 0;
}}

.upcoming-vs {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 14px;
    color: {THEME['muted_fg']};
}}

/* Group table */
.group-card {{
    background: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 16px;
}}

.group-header {{
    padding: 12px 16px;
    border-bottom: 1px solid {THEME['border']};
    background: linear-gradient(to right, rgba(212,169,49,0.1), transparent);
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.group-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 18px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: {THEME['primary']};
}}

.group-cols {{
    display: flex;
    gap: 12px;
    font-size: 10px;
    color: {THEME['muted_fg']};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}}

.group-col {{
    width: 20px;
    text-align: center;
}}

.group-col-wide {{
    width: 28px;
    text-align: center;
}}

.group-row {{
    display: flex;
    align-items: center;
    padding: 10px 16px;
    gap: 10px;
    border-bottom: 1px solid {THEME['border']};
    transition: background 0.15s;
}}

.group-row:last-child {{
    border-bottom: none;
}}

.group-row:hover {{
    background: rgba(212,169,49,0.04);
}}

.group-pos {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 15px;
    width: 16px;
    flex-shrink: 0;
}}

.group-pos-q {{
    color: {THEME['primary']};
}}

.group-pos-out {{
    color: {THEME['muted_fg']};
}}

.group-team {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    flex: 1;
}}

.group-team-q {{
    color: {THEME['foreground']};
}}

.group-team-out {{
    color: rgba(237,242,255,0.6);
}}

.q-badge {{
    font-size: 9px;
    font-weight: 700;
    color: {THEME['primary']};
    background: rgba(212,169,49,0.1);
    padding: 2px 6px;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}

.group-stats {{
    display: flex;
    gap: 12px;
    font-size: 12px;
    color: {THEME['muted_fg']};
}}

.group-stat {{
    width: 20px;
    text-align: center;
}}

.group-stat-wide {{
    width: 28px;
    text-align: center;
}}

.gd-pos {{ color: {THEME['green']}; }}
.gd-neg {{ color: {THEME['red']}; }}

.pts-bold {{
    font-weight: 700;
    color: {THEME['foreground']};
}}

/* Third place table */
.third-table {{
    background: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 12px;
    overflow: hidden;
}}

.third-header {{
    display: grid;
    grid-template-columns: 32px 1fr 60px 60px 60px 80px;
    gap: 8px;
    padding: 12px 16px;
    border-bottom: 1px solid {THEME['border']};
    font-size: 10px;
    color: {THEME['muted_fg']};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}}

.third-row {{
    display: grid;
    grid-template-columns: 32px 1fr 60px 60px 60px 80px;
    gap: 8px;
    padding: 12px 16px;
    align-items: center;
    border-bottom: 1px solid {THEME['border']};
    transition: background 0.15s;
}}

.third-row:last-child {{
    border-bottom: none;
}}

.third-row-advance:hover {{ background: rgba(34,197,94,0.05); }}
.third-row-out {{ opacity: 0.6; }}
.third-row-out:hover {{ background: rgba(255,255,255,0.02); }}

.third-rank-advance {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 16px;
    color: {THEME['green']};
}}

.third-rank-out {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 16px;
    color: {THEME['muted_fg']};
}}

.third-team {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.third-team-name {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

.third-group-label {{
    font-size: 10px;
    color: {THEME['muted_fg']};
    margin-left: 6px;
}}

.third-pts {{
    font-weight: 700;
    font-size: 14px;
    color: {THEME['foreground']};
    text-align: center;
}}

.third-gd-neg {{
    color: {THEME['red']};
    font-size: 13px;
    text-align: center;
}}

.third-gd-pos {{
    color: {THEME['green']};
    font-size: 13px;
    text-align: center;
}}

.third-gf {{
    color: {THEME['muted_fg']};
    font-size: 13px;
    text-align: center;
}}

.advance-badge {{
    font-size: 10px;
    font-weight: 700;
    color: {THEME['green']};
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.2);
    padding: 2px 10px;
    border-radius: 99px;
    text-align: center;
}}

.out-badge {{
    font-size: 10px;
    font-weight: 600;
    color: {THEME['muted_fg']};
    background: {THEME['muted']};
    padding: 2px 10px;
    border-radius: 99px;
    text-align: center;
}}

/* Scorers table */
.scorers-table {{
    background: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 12px;
    overflow: hidden;
}}

.scorers-header {{
    display: grid;
    grid-template-columns: 32px 1fr 80px 80px 60px;
    gap: 8px;
    padding: 12px 16px;
    border-bottom: 1px solid {THEME['border']};
    font-size: 10px;
    color: {THEME['muted_fg']};
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}}

.scorers-row {{
    display: grid;
    grid-template-columns: 32px 1fr 80px 80px 60px;
    gap: 8px;
    padding: 12px 16px;
    align-items: center;
    border-bottom: 1px solid {THEME['border']};
    transition: background 0.15s;
}}

.scorers-row:last-child {{
    border-bottom: none;
}}

.scorers-row:hover {{
    background: rgba(255,255,255,0.02);
}}

.scorers-row-top {{
    background: rgba(212,169,49,0.03);
}}

.scorer-rank-1 {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 16px;
    color: {THEME['primary']};
}}

.scorer-rank-2 {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 16px;
    color: rgba(237,242,255,0.6);
}}

.scorer-rank-3 {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 16px;
    color: rgba(237,242,255,0.4);
}}

.scorer-rank-rest {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 13px;
    color: {THEME['muted_fg']};
}}

.scorer-player {{
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}}

.scorer-name {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

.scorer-country {{
    font-size: 10px;
    color: {THEME['muted_fg']};
}}

.scorer-goals-top {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 22px;
    color: {THEME['primary']};
    text-align: center;
}}

.scorer-goals-rest {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 22px;
    color: {THEME['foreground']};
    text-align: center;
}}

.scorer-assists {{
    font-weight: 600;
    font-size: 13px;
    color: {THEME['muted_fg']};
    text-align: center;
}}

.scorer-mp {{
    font-size: 12px;
    color: {THEME['muted_fg']};
    text-align: center;
}}

/* Date divider */
.date-divider {{
    font-size: 11px;
    font-weight: 600;
    color: {THEME['muted_fg']};
    text-transform: uppercase;
    letter-spacing: 0.2em;
    padding: 12px 4px 8px;
}}

/* Footer */
.wc-footer {{
    border-top: 1px solid {THEME['border']};
    margin-top: 48px;
    padding: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: {THEME['muted_fg']};
}}

.wc-footer-logo {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.2em;
}}

/* Navigation buttons */
div[data-testid="stButton"] button {{
    background-color: #162340 !important;
    color: #7B91B0 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}

div[data-testid="stButton"] button:hover {{
    background-color: #1a2d50 !important;
    color: #EDF2FF !important;
    border-color: rgba(255,255,255,0.15) !important;
}}

div[data-testid="stButton"] button[kind="primary"] {{
    background-color: #D4A931 !important;
    color: #060C1A !important;
    border-color: #D4A931 !important;
}}

div[data-testid="stButton"] button[kind="primary"]:hover {{
    background-color: #e6bb3a !important;
}}

/* Streamlit column fixes */
div[data-testid="column"] > div {{
    height: 100%;
}}
</style>
"""

def render_header(active_tab: str):
    from datetime import date
    today = date.today().strftime("%b %d, %Y").upper()
    tabs = [
        ("live", "⚡ LIVE", 2),
        ("results", "⏱ RESULTS", None),
        ("groups", "▦ GROUPS", None),
        ("third", "◎ 3RD PLACE", None),
        ("scorers", "★ SCORERS", None),
    ]
    return f"""
    <div class="wc-header">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;border-radius:8px;background:rgba(212,169,49,0.1);
                border:1px solid rgba(212,169,49,0.2);display:flex;align-items:center;justify-content:center;
                font-size:18px;">🏆</div>
            <div>
                <div class="wc-logo-title">FIFA World Cup</div>
                <div class="wc-logo-sub">2026 · USA · Canada · Mexico</div>
            </div>
        </div>
        <div class="wc-header-right">
            <div class="wc-header-stat">
                <div class="wc-header-stat-label">Stage</div>
                <div class="wc-header-stat-value">Group Stage</div>
            </div>
            <div class="wc-divider"></div>
            <div class="wc-header-stat">
                <div class="wc-header-stat-label">Matchday</div>
                <div class="wc-header-stat-value">{today}</div>
            </div>
        </div>
    </div>
    <div style="height:10px;background:#060C1A;"></div>
    """