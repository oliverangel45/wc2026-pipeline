import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit.components.v1 as components
from utils import BASE_CSS, THEME, flag_img, run_query, render_header, FLAG_CODES

st.set_page_config(
    page_title="FIFA World Cup 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(render_header("live"), unsafe_allow_html=True)

# ── Nav tabs ──────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if st.button("⚡ LIVE", use_container_width=True, type="primary"):
        pass
with col2:
    if st.button("⏱ RESULTS", use_container_width=True):
        st.switch_page("pages/2_Results.py")
with col3:
    if st.button("▦ GROUPS", use_container_width=True):
        st.switch_page("pages/3_Groups.py")
with col4:
    if st.button("◎ 3RD PLACE", use_container_width=True):
        st.switch_page("pages/4_Third_Place.py")
with col5:
    if st.button("★ SCORERS", use_container_width=True):
        st.switch_page("pages/5_Scorers.py")
with col6:
    if st.button("⬡ BRACKET", use_container_width=True):
        st.switch_page("pages/6_Bracket.py")

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── Live matches ──────────────────────────────────────────────────────────
try:
    cols, rows = run_query("""
        SELECT MATCH_ID, HOME_TEAM, AWAY_TEAM, HOME_SCORE, AWAY_SCORE, STATUS, STAGE, MATCHDAY,
               TO_CHAR(KICKOFF_TIME_BST, 'DD Mon · HH24:MI') AS KICKOFF_BST
        FROM WC2026.ANALYTICS_ANALYTICS.fct_match_results
        WHERE STATUS IN ('IN_PLAY', 'PAUSED')
        ORDER BY KICKOFF_TIME_BST DESC
    """)
    live_matches = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    live_matches = []

# ── Upcoming fixtures ─────────────────────────────────────────────────────
try:
    cols, rows = run_query("""
        SELECT MATCH_ID, HOME_TEAM, AWAY_TEAM, STATUS, STAGE, MATCHDAY,
               TO_CHAR(KICKOFF_TIME_BST, 'DD Mon · HH24:MI') AS KICKOFF_BST
        FROM WC2026.ANALYTICS_ANALYTICS.fct_match_results
        WHERE STATUS IN ('SCHEDULED', 'TIMED')
        ORDER BY KICKOFF_TIME_BST ASC
        LIMIT 10
    """)
    upcoming_matches = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    upcoming_matches = []

# ── Recent results ────────────────────────────────────────────────────────
try:
    cols, rows = run_query("""
        SELECT MATCH_ID, HOME_TEAM, AWAY_TEAM, HOME_SCORE, AWAY_SCORE, STATUS, STAGE, MATCHDAY,
               TO_CHAR(KICKOFF_TIME_BST, 'DD Mon · HH24:MI') AS KICKOFF_BST,
               TO_CHAR(KICKOFF_TIME_BST, 'DD Mon YYYY') AS MATCH_DATE
        FROM WC2026.ANALYTICS_ANALYTICS.fct_match_results
        WHERE STATUS = 'FINISHED'
        ORDER BY KICKOFF_TIME_BST DESC
        LIMIT 10
    """)
    recent_results = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    recent_results = []

# ── Render live matches ───────────────────────────────────────────────────
live_count = len(live_matches)
st.markdown(f"""
<div class="wc-section-title">
    <span style="color:{THEME['red']}">⚡</span>
    Live Matches
    <span class="wc-badge">{live_count} in progress</span>
</div>
""", unsafe_allow_html=True)

if live_matches:
    cols = st.columns(min(len(live_matches), 2))
    for i, m in enumerate(live_matches):
        with cols[i % 2]:
            home_flag = flag_img(m['HOME_TEAM'], 56)
            away_flag = flag_img(m['AWAY_TEAM'], 56)
            status_label = "HT" if m['STATUS'] == 'PAUSED' else "LIVE"
            st.markdown(f"""
            <div class="live-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span class="live-badge">
                            <span class="live-dot"></span>
                            {status_label}
                        </span>
                    </div>
                    <span class="live-venue">📍 {m.get('STAGE','Group Stage').replace('_',' ').title()}</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:16px;">
                    <div style="display:flex;flex-direction:column;align-items:center;gap:8px;">
                        {home_flag}
                        <span class="live-team">{m['HOME_TEAM']}</span>
                    </div>
                    <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
                        <div class="live-score">
                            {m['HOME_SCORE'] if m['HOME_SCORE'] is not None else '0'}
                            <span class="live-score-sep">–</span>
                            {m['AWAY_SCORE'] if m['AWAY_SCORE'] is not None else '0'}
                        </div>
                        <span class="live-group">Matchday {m.get('MATCHDAY','')}</span>
                    </div>
                    <div style="display:flex;flex-direction:column;align-items:center;gap:8px;">
                        {away_flag}
                        <span class="live-team">{m['AWAY_TEAM']}</span>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width:50%"></div>
                </div>
                <div class="progress-labels">
                    <span>0'</span><span>45'</span><span>90'</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background:{THEME['card']};border:1px solid {THEME['border']};border-radius:12px;
        padding:32px;text-align:center;color:{THEME['muted_fg']};">
        <div style="font-size:32px;margin-bottom:8px;">⚽</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:16px;
            text-transform:uppercase;letter-spacing:0.1em;">No live matches right now</div>
        <div style="font-size:13px;margin-top:4px;">Check upcoming fixtures below</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── Upcoming fixtures ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="wc-section-title">
    <span style="color:{THEME['primary']}">📅</span>
    Upcoming Fixtures
    <span class="wc-badge">{len(upcoming_matches)} scheduled</span>
</div>
""", unsafe_allow_html=True)

if upcoming_matches:
    upcoming_html = ""
    for m in upcoming_matches:
        home_flag = flag_img(m['HOME_TEAM'], 18)
        away_flag = flag_img(m['AWAY_TEAM'], 18)
        upcoming_html += f"""
        <div class="upcoming-row">
            <span class="upcoming-time">{m['KICKOFF_BST']} BST</span>
            <div class="match-teams">
                <div class="match-home">
                    <span class="match-team-name">{m['HOME_TEAM']}</span>
                    {home_flag}
                </div>
                <span class="upcoming-vs">vs</span>
                <div class="match-away">
                    {away_flag}
                    <span class="match-team-name">{m['AWAY_TEAM']}</span>
                </div>
            </div>
            <span class="match-group">MD {m.get('MATCHDAY','')}</span>
        </div>
        """
    st.markdown(upcoming_html, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="color:{THEME['muted_fg']};font-size:13px;padding:16px 0;">
        No upcoming fixtures available.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── Recent results ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="wc-section-title">
    <span style="color:{THEME['muted_fg']}">⏱</span>
    Recent Results
</div>
""", unsafe_allow_html=True)

if recent_results:
    results_html = ""
    current_date = None
    for m in recent_results:
        if m['MATCH_DATE'] != current_date:
            current_date = m['MATCH_DATE']
            results_html += f'<div style="font-size:11px;font-weight:600;color:#7B91B0;text-transform:uppercase;letter-spacing:0.2em;padding:12px 4px 8px;">{current_date.upper()}</div>'
        code_home = FLAG_CODES.get(m['HOME_TEAM'], 'un')
        code_away = FLAG_CODES.get(m['AWAY_TEAM'], 'un')
        home_flag = f'<img src="https://flagcdn.com/w40/{code_home}.png" height="18" style="border-radius:2px;object-fit:cover;" />'
        away_flag = f'<img src="https://flagcdn.com/w40/{code_away}.png" height="18" style="border-radius:2px;object-fit:cover;" />'
        results_html += f"""
        <div style="background:#0C1B30;border:1px solid rgba(255,255,255,0.07);border-radius:8px;
            padding:12px 16px;display:flex;align-items:center;gap:16px;margin-bottom:6px;">
            <span style="font-size:11px;color:#7B91B0;width:120px;flex-shrink:0;">{m['KICKOFF_BST']} BST</span>
            <div style="flex:1;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;">
                <div style="display:flex;align-items:center;gap:8px;justify-content:flex-end;">
                    <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:13px;
                        letter-spacing:0.08em;text-transform:uppercase;">{m['HOME_TEAM']}</span>
                    {home_flag}
                </div>
                <span style="font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:18px;
                    color:#EDF2FF;white-space:nowrap;">{m['HOME_SCORE']} – {m['AWAY_SCORE']}</span>
                <div style="display:flex;align-items:center;gap:8px;">
                    {away_flag}
                    <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:13px;
                        letter-spacing:0.08em;text-transform:uppercase;">{m['AWAY_TEAM']}</span>
                </div>
            </div>
            <span style="font-size:11px;color:#7B91B0;width:64px;text-align:right;flex-shrink:0;">MD {m.get('MATCHDAY','')}</span>
        </div>
        """

    full_iframe_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;900&display=swap" rel="stylesheet">
    <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: transparent; font-family: 'Inter', sans-serif; color: #EDF2FF; }}
    </style>
    </head>
    <body>
    {results_html}
    </body>
    </html>
    """
    components.html(full_iframe_html, height=len(recent_results) * 60 + 80, scrolling=False)
else:
    st.markdown(f'<div style="color:{THEME["muted_fg"]};font-size:13px;">No results yet.</div>',
                unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="wc-footer">
    <span class="wc-footer-logo">FIFA World Cup 2026™</span>
    <span>48 Teams · 3 Host Nations · 104 Matches</span>
</div>
""", unsafe_allow_html=True)