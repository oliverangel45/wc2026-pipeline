import streamlit as st
import streamlit.components.v1 as components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import THEME, flag_img, run_query, render_header, BASE_CSS

st.set_page_config(page_title="Groups | FIFA WC 2026", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")
st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(render_header("groups"), unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if st.button("⚡ LIVE", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("⏱ RESULTS", use_container_width=True):
        st.switch_page("pages/2_Results.py")
with col3:
    if st.button("▦ GROUPS", use_container_width=True, type="primary"):
        pass
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
        SELECT TEAM_NAME, GROUP_NAME, POSITION, PLAYED_GAMES, WON, DRAW, LOST,
               POINTS, GOALS_FOR, GOALS_AGAINST, GOAL_DIFF
        FROM WC2026.ANALYTICS_ANALYTICS.dim_group_standings
        ORDER BY GROUP_NAME ASC, POSITION ASC
    """)
    standings = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    standings = []
    st.error(f"Error loading standings: {e}")

st.markdown(f"""
<div class="wc-section-title">
    <span>▦</span>
    Group Standings
    <span class="wc-badge">All 12 Groups</span>
</div>
""", unsafe_allow_html=True)

# Group into dict
groups = {}
for row in standings:
    g = row['GROUP_NAME']
    if g not in groups:
        groups[g] = []
    groups[g].append(row)

group_names = sorted(groups.keys())

# Build the complete HTML including its own styles — rendered in iframe via components.html
grid_html = ""
for row_start in range(0, len(group_names), 3):
    group_row = group_names[row_start:row_start+3]
    grid_html += '<div class="grid-row">'
    for gname in group_row:
        teams = groups[gname]
        grid_html += f'<div class="group-card"><div class="group-header"><span class="group-title">{gname}</span><div class="group-cols"><span>P</span><span>W</span><span>D</span><span>L</span><span>GD</span><span>Pts</span></div></div>'
        for i, t in enumerate(teams):
            is_q = i < 2
            gd = t['GOAL_DIFF']
            gd_str = f"+{gd}" if gd > 0 else str(gd)
            gd_color = "#22C55E" if gd > 0 else ("#EF4444" if gd < 0 else "#7B91B0")
            pos_color = "#D4A931" if is_q else "#7B91B0"
            team_color = "#EDF2FF" if is_q else "rgba(237,242,255,0.6)"
            q_badge = '<span class="q-badge">Q</span>' if is_q else ""
            flag_url = f"https://flagcdn.com/w40/{{}}.png".format
            from utils import FLAG_CODES
            code = FLAG_CODES.get(t['TEAM_NAME'], 'un')
            flag = f'<img src="https://flagcdn.com/w40/{code}.png" height="16" style="border-radius:2px;object-fit:cover;flex-shrink:0;" />'
            grid_html += f'''
            <div class="team-row">
                <span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:900;font-size:15px;width:16px;flex-shrink:0;color:{pos_color}">{i+1}</span>
                {flag}
                <span style="font-family:\'Barlow Condensed\',sans-serif;font-weight:700;font-size:13px;text-transform:uppercase;flex:1;color:{team_color};letter-spacing:0.05em;">{t['TEAM_NAME']}</span>
                {q_badge}
                <div class="stats">
                    <span>{t['PLAYED_GAMES']}</span>
                    <span>{t['WON']}</span>
                    <span>{t['DRAW']}</span>
                    <span>{t['LOST']}</span>
                    <span style="color:{gd_color}">{gd_str}</span>
                    <span style="font-weight:700;color:#EDF2FF">{t['POINTS']}</span>
                </div>
            </div>'''
        grid_html += '</div>'
    grid_html += '</div>'

full_iframe_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;900&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: transparent; font-family: 'Inter', sans-serif; }}
.grid-row {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 16px;
}}
.group-card {{
    background: #0C1B30;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    overflow: hidden;
}}
.group-header {{
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    background: linear-gradient(to right, rgba(212,169,49,0.1), transparent);
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.group-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 16px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #D4A931;
}}
.group-cols {{
    display: flex;
    gap: 8px;
    font-size: 10px;
    color: #7B91B0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}}
.group-cols span {{ width: 20px; text-align: center; }}
.group-cols span:last-child {{ font-weight: 700; color: rgba(237,242,255,0.5); }}
.team-row {{
    display: flex;
    align-items: center;
    padding: 8px 14px;
    gap: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.team-row:last-child {{ border-bottom: none; }}
.stats {{
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: #7B91B0;
}}
.stats span {{ width: 20px; text-align: center; }}
.q-badge {{
    font-size: 9px;
    font-weight: 700;
    color: #D4A931;
    background: rgba(212,169,49,0.1);
    padding: 1px 5px;
    border-radius: 3px;
    text-transform: uppercase;
    flex-shrink: 0;
}}
</style>
</head>
<body>
{grid_html}
</body>
</html>
"""

components.html(full_iframe_html, height=len(group_names) // 3 * 230 + 230, scrolling=False)

st.markdown(f"""
<div class="wc-footer">
    <span class="wc-footer-logo">FIFA World Cup 2026™</span>
    <span>48 Teams · 3 Host Nations · 104 Matches</span>
</div>
""", unsafe_allow_html=True)