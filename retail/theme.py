"""Session-local display theme. Model behavior is independent of theme."""
import streamlit as st

def render_theme():
    dark=st.toggle('Dark mode',value=False,key='salescope_dark')
    if dark:
        bg,surface,text,muted,border,accent='#171717','#202020','#f5f5f2','#b4b4ad','#3c3c38','#ecece5'
    else:
        bg,surface,text,muted,border,accent='#fafaf8','#ffffff','#242421','#66665f','#ddddd5','#30302b'
    st.html(f'''<style>
    .stApp {{background:{bg}!important;color:{text}!important;color-scheme:{'dark' if dark else 'light'};}}
    [data-testid="stHeader"] {{background:{bg}!important;}}
    [data-testid="stMainBlockContainer"] {{max-width:980px;padding-top:3rem;padding-bottom:3rem;}}
    .stApp h1 {{font-size:2.4rem;font-weight:650;letter-spacing:-0.045em;}}
    .stApp h3 {{font-size:1.25rem;font-weight:550;letter-spacing:-0.025em;}}
    .stApp hr {{border-color:{border};margin:1.5rem 0;}}
    .stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMetricValue"] {{color:{text};}}
    .stApp [data-testid="stCaptionContainer"] p {{color:{muted}!important;}}
    .stApp [data-testid="stForm"] {{background:{surface}!important;border:1px solid {border}!important;border-radius:16px;padding:1.6rem;}}
    .stApp .react-aria-ComboBox [role="group"],
    .stApp .react-aria-DatePicker,
    .stApp .react-aria-DateField,
    .stApp .react-aria-DateField [role="group"],
    .stApp .react-aria-DatePicker > div {{background:{bg}!important;color:{text}!important;border-color:{border}!important;}}
    .stApp .react-aria-ComboBox input,
    .stApp .react-aria-ComboBox button,
    .stApp .react-aria-DateField span,
    .stApp .react-aria-DatePicker button {{background:transparent!important;color:{text}!important;}}
    .react-aria-Popover,.react-aria-ListBox,.react-aria-Calendar,
    [role="listbox"],[role="option"], [role="dialog"] {{background:{surface}!important;color:{text}!important;}}
    [role="option"][data-focused], [role="option"][data-selected] {{background:{border}!important;color:{text}!important;}}
    .stApp [data-baseweb="select"] > div,
    .stApp [data-baseweb="input"],.stApp [data-baseweb="input"] input {{background:{bg};color:{text};border-color:{border};}}
    .stApp [data-baseweb="select"] span {{color:{text};}}
    .stApp [data-baseweb="checkbox"] > span:first-of-type {{background:{accent};border-color:{border};}}
    .stApp [data-baseweb="checkbox"] input:checked + div {{background:{accent};border-color:{accent};}}
    .stApp [data-baseweb="checkbox"] svg {{color:{bg};fill:{bg};}}
    .stApp [data-testid="stWidgetLabel"] p {{font-size:0.93rem;}}
    .stApp input {{color:{text};caret-color:{accent};}}
    .stApp svg {{color:{muted};}}
    .stApp [data-testid="stFormSubmitButton"] button {{background:{accent}!important;color:{bg}!important;border:0;border-radius:10px;font-weight:600;}}
    .stApp [data-testid="stFormSubmitButton"] button p {{color:{bg}!important;}}
    .stApp [data-testid="stMetric"] {{background:{surface};border:1px solid {border};border-radius:14px;padding:1.2rem;}}
    .stApp [data-testid="stMetricValue"] {{font-size:3.2rem;font-weight:500;letter-spacing:-0.05em;}}
    .stApp [data-testid="stExpander"] details {{border-color:{border};background:{surface};}}
    .stApp [data-testid="stExpander"] summary {{color:{text};}}
    .stApp button:focus-visible,.stApp input:focus-visible {{outline:2px solid {accent};outline-offset:3px;}}
    [data-baseweb="popover"] > div,[data-baseweb="menu"],
    [role="listbox"],[role="option"], [data-baseweb="calendar"] {{background:{surface}!important;color:{text}!important;}}
    [data-baseweb="calendar"] button {{color:{text};}}
    </style>''')
    return dark
