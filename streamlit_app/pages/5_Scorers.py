import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import BASE_CSS, THEME, flag_img, run_query, render_header

st.set_page_config(page_title="Scorers | FIFA WC 2026", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")
st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(render_header("scorers"), unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if st.button("⚡ LIVE", use_container_width=True):
        st.switch_page("Home.py")
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
    if st.button("★ SCORERS", use_container_width=True, type="primary"):
        pass
with col6:
    if st.button("⬡ BRACKET", use_container_width=True):
        st.switch_page("pages/6_Bracket.py")

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

try:
    cols, rows = run_query("""
        SELECT PLAYER_NAME, TEAM_NAME, GOALS_SCORED, PENALTIES, NORMAL_GOALS
        FROM WC2026.ANALYTICS_ANALYTICS.fct_top_scorers
        WHERE GOALS_SCORED > 0
        ORDER BY GOALS_SCORED DESC, PENALTIES DESC
        LIMIT 25
    """)
    scorers = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    scorers = []
    st.error(f"Error: {e}")

if not scorers:
    st.markdown(f"""
    <div style="background:{THEME['card']};border:1px solid {THEME['border']};
        border-radius:12px;padding:48px 32px;text-align:center;">
        <div style="font-size:40px;margin-bottom:12px;">⚽</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;
            font-size:18px;text-transform:uppercase;letter-spacing:0.1em;
            color:{THEME['foreground']};margin-bottom:8px;">
            No Scorers Data Available
        </div>
        <div style="font-size:13px;color:{THEME['muted_fg']};max-width:400px;margin:0 auto;line-height:1.6;">
            Goals data requires a paid football-data.org API tier. 
            The pipeline is correctly built and will populate automatically 
            when events data becomes available.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.markdown(f"""
<div class="wc-section-title">
    <span style="color:{THEME['primary']}">★</span>
    Top Scorers
    <span class="wc-badge">Group Stage</span>
</div>
""", unsafe_allow_html=True)

html = f"""
<div class="scorers-table">
    <div class="scorers-header">
        <span>#</span>
        <span>Player</span>
        <span style="text-align:center">Goals</span>
        <span style="text-align:center">Pens</span>
        <span style="text-align:center">MP</span>
    </div>
"""

for i, s in enumerate(scorers):
    is_top = i < 3
    row_class = "scorers-row scorers-row-top" if is_top else "scorers-row"

    if i == 0:
        rank_html = f'<span class="scorer-rank-1">1</span>'
    elif i == 1:
        rank_html = f'<span class="scorer-rank-2">2</span>'
    elif i == 2:
        rank_html = f'<span class="scorer-rank-3">3</span>'
    else:
        rank_html = f'<span class="scorer-rank-rest">{i+1}</span>'

    goals_class = "scorer-goals-top" if is_top else "scorer-goals-rest"
    flag = flag_img(s['TEAM_NAME'], 18)

    html += f"""
    <div class="{row_class}">
        <div>{rank_html}</div>
        <div class="scorer-player">
            {flag}
            <div>
                <div class="scorer-name">{s['PLAYER_NAME']}</div>
                <div class="scorer-country">{s['TEAM_NAME']}</div>
            </div>
        </div>
        <div class="{goals_class}">{s['GOALS_SCORED']}</div>
        <div class="scorer-assists">{s.get('PENALTIES', 0) or 0}</div>
        <div class="scorer-mp">—</div>
    </div>
    """

html += "</div>"
st.markdown(html, unsafe_allow_html=True)

st.markdown(f"""
<div class="wc-footer">
    <span class="wc-footer-logo">FIFA World Cup 2026™</span>
    <span>48 Teams · 3 Host Nations · 104 Matches</span>
</div>
""", unsafe_allow_html=True)