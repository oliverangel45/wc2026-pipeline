import streamlit as st
import streamlit.components.v1 as components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import BASE_CSS, THEME, flag_img, run_query, render_header, FLAG_CODES

st.set_page_config(page_title="3rd Place | FIFA WC 2026", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")
st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(render_header("third"), unsafe_allow_html=True)

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
    if st.button("◎ 3RD PLACE", use_container_width=True, type="primary"):
        pass
with col5:
    if st.button("★ SCORERS", use_container_width=True):
        st.switch_page("pages/5_Scorers.py")
with col6:
    if st.button("⬡ BRACKET", use_container_width=True):
        st.switch_page("pages/6_Bracket.py")

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

try:
    cols, rows = run_query("""
        SELECT TEAM_NAME, GROUP_NAME, PLAYED_GAMES, WON, DRAW, LOST,
               POINTS, GOALS_FOR, GOALS_AGAINST, GOAL_DIFF
        FROM WC2026.ANALYTICS_ANALYTICS.dim_third_place_standings
        ORDER BY POINTS DESC, GOAL_DIFF DESC, GOALS_FOR DESC
        LIMIT 12
    """)
    teams = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    teams = []
    st.error(f"Error: {e}")

st.markdown(f"""
<div class="wc-section-title">
    <span>◎</span>
    Best Third-Placed Teams
</div>
<p style="color:{THEME['muted_fg']};font-size:13px;margin-bottom:24px;">
    Top 8 third-placed teams advance to the Round of 32.
</p>
""", unsafe_allow_html=True)

# Build table rows
rows_html = ""
for i, t in enumerate(teams):
    advances = i < 8
    gd = t['GOAL_DIFF']
    gd_str = f"+{gd}" if gd > 0 else str(gd)
    gd_color = "#22C55E" if gd >= 0 else "#EF4444"
    rank_color = "#22C55E" if advances else "#7B91B0"
    row_bg = "rgba(34,197,94,0.03)" if advances else "transparent"
    row_opacity = "1" if advances else "0.6"
    badge = '<span class="advance-badge">ADVANCE</span>' if advances else '<span class="out-badge">OUT</span>'
    code = FLAG_CODES.get(t['TEAM_NAME'], 'un')
    flag = f'<img src="https://flagcdn.com/w40/{code}.png" height="20" style="border-radius:2px;object-fit:cover;flex-shrink:0;" />'

    rows_html += f"""
    <div class="team-row" style="background:{row_bg};opacity:{row_opacity};">
        <span class="rank" style="color:{rank_color};">{i+1}</span>
        <div class="team-info">
            {flag}
            <div>
                <span class="team-name">{t['TEAM_NAME']}</span>
                <span class="group-label">{t['GROUP_NAME']}</span>
            </div>
        </div>
        <span class="stat-pts">{t['POINTS']}</span>
        <span class="stat-gd" style="color:{gd_color};">{gd_str}</span>
        <span class="stat-gf">{t['GOALS_FOR']}</span>
        <div class="badge-col">{badge}</div>
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
.third-table {{
    background: #0C1B30;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    overflow: hidden;
}}
.table-header {{
    display: grid;
    grid-template-columns: 32px 1fr 60px 60px 60px 90px;
    gap: 8px;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    font-size: 10px;
    color: #7B91B0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}}
.team-row {{
    display: grid;
    grid-template-columns: 32px 1fr 60px 60px 60px 90px;
    gap: 8px;
    padding: 12px 16px;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    transition: background 0.15s;
}}
.team-row:last-child {{ border-bottom: none; }}
.rank {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 16px;
}}
.team-info {{
    display: flex;
    align-items: center;
    gap: 10px;
}}
.team-name {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
.group-label {{
    font-size: 10px;
    color: #7B91B0;
    margin-left: 6px;
}}
.stat-pts {{
    font-weight: 700;
    font-size: 14px;
    color: #EDF2FF;
    text-align: center;
}}
.stat-gd {{
    font-size: 13px;
    text-align: center;
}}
.stat-gf {{
    font-size: 13px;
    color: #7B91B0;
    text-align: center;
}}
.badge-col {{
    text-align: center;
}}
.advance-badge {{
    font-size: 10px;
    font-weight: 700;
    color: #22C55E;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.2);
    padding: 3px 10px;
    border-radius: 99px;
}}
.out-badge {{
    font-size: 10px;
    font-weight: 600;
    color: #7B91B0;
    background: #162340;
    padding: 3px 10px;
    border-radius: 99px;
}}
</style>
</head>
<body>
<div class="third-table">
    <div class="table-header">
        <span>#</span>
        <span>Team</span>
        <span style="text-align:center">Pts</span>
        <span style="text-align:center">GD</span>
        <span style="text-align:center">GF</span>
        <span style="text-align:center">Status</span>
    </div>
    {rows_html}
</div>
<div style="margin-top:16px;display:flex;align-items:center;gap:8px;font-size:12px;color:#7B91B0;">
    <span style="width:8px;height:8px;border-radius:50%;background:#22C55E;display:inline-block;"></span>
    Ranked by: Points → Goal Difference → Goals Scored
</div>
</body>
</html>
"""

components.html(full_iframe_html, height=len(teams) * 50 + 120, scrolling=False)

st.markdown(f"""
<div class="wc-footer">
    <span class="wc-footer-logo">FIFA World Cup 2026™</span>
    <span>48 Teams · 3 Host Nations · 104 Matches</span>
</div>
""", unsafe_allow_html=True)