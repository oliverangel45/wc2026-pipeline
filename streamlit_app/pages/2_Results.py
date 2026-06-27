import streamlit as st
import streamlit.components.v1 as components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import BASE_CSS, THEME, run_query, render_header, FLAG_CODES

st.set_page_config(page_title="Results | FIFA WC 2026", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")
st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(render_header("results"), unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if st.button("⚡ LIVE", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("⏱ RESULTS", use_container_width=True, type="primary"):
        pass
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

try:
    cols, rows = run_query("""
        SELECT HOME_TEAM, AWAY_TEAM, HOME_SCORE, AWAY_SCORE, MATCHDAY,
               TO_CHAR(KICKOFF_TIME_BST, 'DD Mon · HH24:MI') AS KICKOFF_BST,
               TO_CHAR(KICKOFF_TIME_BST, 'DD Mon YYYY') AS MATCH_DATE
        FROM WC2026.ANALYTICS_ANALYTICS.fct_match_results
        WHERE STATUS = 'FINISHED'
        ORDER BY KICKOFF_TIME_BST DESC
    """)
    results = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    results = []
    st.error(f"Error loading results: {e}")

st.markdown(f"""
<div class="wc-section-title">
    <span style="color:{THEME['muted_fg']}">⏱</span>
    Match Results
    <span class="wc-badge">Group Stage</span>
</div>
""", unsafe_allow_html=True)

if results:
    results_html = ""
    current_date = None
    for m in results:
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
    components.html(full_iframe_html, height=len(results) * 60 + 100, scrolling=True)
else:
    st.markdown(f'<div style="color:{THEME["muted_fg"]};padding:32px;text-align:center;">No results yet.</div>',
                unsafe_allow_html=True)

st.markdown(f"""
<div class="wc-footer">
    <span class="wc-footer-logo">FIFA World Cup 2026™</span>
    <span>48 Teams · 3 Host Nations · 104 Matches</span>
</div>
""", unsafe_allow_html=True)