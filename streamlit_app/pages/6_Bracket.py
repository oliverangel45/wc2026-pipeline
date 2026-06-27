import streamlit as st
import streamlit.components.v1 as components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import BASE_CSS, THEME, run_query, render_header, FLAG_CODES

st.set_page_config(page_title="Bracket | FIFA WC 2026", page_icon="🏆", layout="wide", initial_sidebar_state="collapsed")
st.markdown(BASE_CSS, unsafe_allow_html=True)
st.markdown(render_header("bracket"), unsafe_allow_html=True)

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
    if st.button("★ SCORERS", use_container_width=True):
        st.switch_page("pages/5_Scorers.py")
with col6:
    if st.button("⬡ BRACKET", use_container_width=True, type="primary"):
        pass

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

st.markdown(f"""
<div class="wc-section-title">
    <span>⬡</span>
    Knockout Bracket
    <span class="wc-badge">Round of 32 → Final</span>
</div>
<p style="color:{THEME['muted_fg']};font-size:13px;margin-bottom:24px;">
    Teams populate automatically as the knockout stage progresses. Group stage ends 27 Jun · Round of 32 begins 28 Jun.
</p>
""", unsafe_allow_html=True)

# Query knockout matches from Snowflake
try:
    cols, rows = run_query("""
        SELECT MATCH_ID, HOME_TEAM, AWAY_TEAM, HOME_SCORE, AWAY_SCORE,
               STATUS, STAGE, MATCHDAY,
               TO_CHAR(KICKOFF_TIME_BST, 'DD Mon · HH24:MI') AS KICKOFF_BST
        FROM WC2026.ANALYTICS_ANALYTICS.fct_match_results
        WHERE STAGE NOT IN ('GROUP_STAGE', 'REGULAR_SEASON')
        ORDER BY KICKOFF_TIME_BST ASC
    """)
    knockout_matches = [dict(zip(cols, r)) for r in rows]
except Exception as e:
    knockout_matches = []

# Organise by stage
stage_order = ['ROUND_OF_32', 'ROUND_OF_16', 'QUARTER_FINALS', 'SEMI_FINALS', 'FINAL']
stage_labels = {
    'ROUND_OF_32': 'Round of 32',
    'ROUND_OF_16': 'Round of 16',
    'QUARTER_FINALS': 'Quarter-Finals',
    'SEMI_FINALS': 'Semi-Finals',
    'FINAL': 'Final'
}
stage_counts = {
    'ROUND_OF_32': 16,
    'ROUND_OF_16': 8,
    'QUARTER_FINALS': 4,
    'SEMI_FINALS': 2,
    'FINAL': 1
}

by_stage = {s: [] for s in stage_order}
for m in knockout_matches:
    stage = m.get('STAGE', '')
    if stage in by_stage:
        by_stage[stage].append(m)

def match_card_html(m=None, placeholder_home="TBD", placeholder_away="TBD"):
    if m:
        home = m['HOME_TEAM'] or placeholder_home
        away = m['AWAY_TEAM'] or placeholder_away
        status = m['STATUS']
        is_live = status in ('IN_PLAY', 'PAUSED')
        is_finished = status == 'FINISHED'
        home_score = m['HOME_SCORE'] if m['HOME_SCORE'] is not None else ''
        away_score = m['AWAY_SCORE'] if m['AWAY_SCORE'] is not None else ''
        kickoff = m.get('KICKOFF_BST', '')

        code_h = FLAG_CODES.get(home, 'un')
        code_a = FLAG_CODES.get(away, 'un')
        flag_h = f'<img src="https://flagcdn.com/w40/{code_h}.png" height="14" style="border-radius:1px;object-fit:cover;flex-shrink:0;" />' if home != 'TBD' else '<span style="font-size:14px;">🏳</span>'
        flag_a = f'<img src="https://flagcdn.com/w40/{code_a}.png" height="14" style="border-radius:1px;object-fit:cover;flex-shrink:0;" />' if away != 'TBD' else '<span style="font-size:14px;">🏳</span>'

        if is_live:
            border_color = "#EF4444"
            score_html = f'<span style="color:#EF4444;font-weight:900;">{home_score}–{away_score}</span>'
        elif is_finished:
            border_color = "#D4A931"
            score_html = f'<span style="color:#EDF2FF;font-weight:900;">{home_score}–{away_score}</span>'
        else:
            border_color = "rgba(255,255,255,0.1)"
            score_html = f'<span style="color:#7B91B0;font-size:10px;">{kickoff}</span>'

        return f"""
        <div style="background:#0C1B30;border:1px solid {border_color};border-radius:8px;
            padding:8px 10px;width:160px;flex-shrink:0;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
                <div style="display:flex;align-items:center;gap:5px;flex:1;min-width:0;">
                    {flag_h}
                    <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:12px;
                        text-transform:uppercase;letter-spacing:0.05em;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;color:#EDF2FF;">{home}</span>
                </div>
                <div style="margin-left:6px;flex-shrink:0;">{score_html if is_finished or is_live else ""}</div>
            </div>
            <div style="height:1px;background:rgba(255,255,255,0.06);margin:4px 0;"></div>
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:5px;flex:1;min-width:0;">
                    {flag_a}
                    <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:12px;
                        text-transform:uppercase;letter-spacing:0.05em;white-space:nowrap;
                        overflow:hidden;text-overflow:ellipsis;color:#EDF2FF;">{away}</span>
                </div>
                {f'<div style="margin-left:6px;flex-shrink:0;">{score_html}</div>' if not is_finished and not is_live else ""}
            </div>
            {f'<div style="margin-top:5px;font-size:9px;color:#7B91B0;text-align:center;">{kickoff}</div>' if not is_finished and not is_live else ""}
        </div>
        """
    else:
        return f"""
        <div style="background:#0A1628;border:1px solid rgba(255,255,255,0.06);border-radius:8px;
            padding:8px 10px;width:160px;flex-shrink:0;opacity:0.5;">
            <div style="display:flex;align-items:center;gap:5px;margin-bottom:5px;">
                <span style="font-size:14px;">🏳</span>
                <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:12px;
                    color:#7B91B0;text-transform:uppercase;">TBD</span>
            </div>
            <div style="height:1px;background:rgba(255,255,255,0.04);margin:4px 0;"></div>
            <div style="display:flex;align-items:center;gap:5px;">
                <span style="font-size:14px;">🏳</span>
                <span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:12px;
                    color:#7B91B0;text-transform:uppercase;">TBD</span>
            </div>
        </div>
        """

# Build bracket HTML
bracket_html = '<div style="display:flex;gap:24px;align-items:flex-start;overflow-x:auto;padding-bottom:16px;">'

for stage in stage_order:
    matches = by_stage[stage]
    total = stage_counts[stage]
    label = stage_labels[stage]

    # Pad with empty slots if not enough real matches yet
    cards = []
    for i in range(total):
        if i < len(matches):
            cards.append(match_card_html(matches[i]))
        else:
            cards.append(match_card_html())

    # Column gap between cards scales with round (later rounds have more vertical space)
    gap = {
        'ROUND_OF_32': 8,
        'ROUND_OF_16': 72,
        'QUARTER_FINALS': 152,
        'SEMI_FINALS': 312,
        'FINAL': 632
    }.get(stage, 8)

    col_html = f"""
    <div style="flex-shrink:0;display:flex;flex-direction:column;align-items:center;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:11px;
            text-transform:uppercase;letter-spacing:0.15em;color:#D4A931;
            margin-bottom:12px;white-space:nowrap;">{label}</div>
        <div style="display:flex;flex-direction:column;gap:{gap}px;">
    """
    for card in cards:
        col_html += card
    col_html += "</div></div>"
    bracket_html += col_html

bracket_html += "</div>"

# Render in iframe
full_iframe_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;900&display=swap" rel="stylesheet">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: transparent; font-family: 'Inter', sans-serif; color: #EDF2FF; overflow-x: auto; }}
::-webkit-scrollbar {{ height: 6px; background: #0C1B30; }}
::-webkit-scrollbar-thumb {{ background: #162340; border-radius: 3px; }}
</style>
</head>
<body>
{bracket_html}
</body>
</html>
"""

components.html(full_iframe_html, height=stage_counts['ROUND_OF_32'] * 75 + 60, scrolling=True)

# Legend
st.markdown(f"""
<div style="display:flex;gap:20px;margin-top:16px;font-size:12px;color:{THEME['muted_fg']};">
    <div style="display:flex;align-items:center;gap:6px;">
        <span style="width:12px;height:12px;border-radius:2px;background:#EF4444;display:inline-block;"></span>
        Live
    </div>
    <div style="display:flex;align-items:center;gap:6px;">
        <span style="width:12px;height:12px;border-radius:2px;background:#D4A931;display:inline-block;"></span>
        Finished
    </div>
    <div style="display:flex;align-items:center;gap:6px;">
        <span style="width:12px;height:12px;border-radius:2px;background:rgba(255,255,255,0.1);display:inline-block;"></span>
        Scheduled / TBD
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="wc-footer">
    <span class="wc-footer-logo">FIFA World Cup 2026™</span>
    <span>48 Teams · 3 Host Nations · 104 Matches</span>
</div>
""", unsafe_allow_html=True)