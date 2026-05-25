import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_data import generate_loan_data

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="XYZ Company Ltd — Loan Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Global */
  [data-testid="stAppViewContainer"]{background:#0d1117;}
  [data-testid="stSidebar"]{background:#161b22;border-right:1px solid #30363d;}
  .main .block-container{padding:1rem 2rem;}
  h1,h2,h3,h4,p,span,div{color:#e6edf3 !important;}
  [data-testid="stSidebar"] *{color:#e6edf3 !important;}

  /* KPI Cards */
  .kpi-card{
    background:linear-gradient(135deg,#161b22 0%,#21262d 100%);
    border:1px solid #30363d;border-radius:12px;
    padding:14px 16px;margin:4px 0;
    transition:transform .2s,box-shadow .2s;
  }
  .kpi-card:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(0,0,0,.4);}
  .kpi-label{font-size:11px;color:#8b949e !important;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px;}
  .kpi-value{font-size:20px;font-weight:700;letter-spacing:-.5px;}
  .kpi-teal {color:#22d3ee !important;}
  .kpi-gold {color:#f59e0b !important;}
  .kpi-red  {color:#f87171 !important;}
  .kpi-green{color:#4ade80 !important;}
  .kpi-white{color:#f0f6fc !important;}

  /* Section headers */
  .section-header{
    font-size:13px;font-weight:600;color:#8b949e !important;
    text-transform:uppercase;letter-spacing:1px;
    border-bottom:1px solid #30363d;padding-bottom:8px;margin:16px 0 10px;
  }

  /* Company header */
  .company-header{
    background:linear-gradient(90deg,#0d1117,#161b22);
    border-bottom:2px solid #22d3ee;
    padding:12px 0;margin-bottom:20px;
  }

  /* Tabs */
  [data-testid="stTabs"] button{
    background:#161b22 !important;border:1px solid #30363d !important;
    color:#8b949e !important;border-radius:8px 8px 0 0 !important;
    font-weight:600;font-size:13px;
  }
  [data-testid="stTabs"] button[aria-selected="true"]{
    background:#21262d !important;border-bottom:2px solid #22d3ee !important;
    color:#22d3ee !important;
  }

  /* Tables */
  [data-testid="stDataFrame"]{border:1px solid #30363d;border-radius:8px;}
  .stDataFrame thead tr th{background:#21262d !important;color:#22d3ee !important;}

  /* Metrics */
  [data-testid="metric-container"]{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:8px;}

  /* Scrollbar */
  ::-webkit-scrollbar{width:6px;height:6px;}
  ::-webkit-scrollbar-track{background:#0d1117;}
  ::-webkit-scrollbar-thumb{background:#30363d;border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading loan portfolio data...")
def load_data():
    df = generate_loan_data(40000, seed=42)
    df['Value Date']    = pd.to_datetime(df['Value Date'],    format='%d-%b-%y', errors='coerce')
    df['Maturity Date'] = pd.to_datetime(df['Maturity Date'], format='%d-%b-%y', errors='coerce')
    df['maturity_year_month'] = df['Maturity Date'].dt.to_period('M').astype(str)
    return df

df_all = load_data()

# ── HELPERS ──────────────────────────────────────────────────
def fmt_ngn(val, dec=0):
    if abs(val) >= 1e9:  return f"₦{val/1e9:.2f}B"
    if abs(val) >= 1e6:  return f"₦{val/1e6:.1f}M"
    if abs(val) >= 1e3:  return f"₦{val/1e3:.1f}K"
    return f"₦{val:,.{dec}f}"

def kpi(label, value, color="teal"):
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value kpi-{color}">{value}</div>
    </div>""", unsafe_allow_html=True)

def section(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

DARK_TEMPLATE = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e6edf3', size=11),
    xaxis=dict(gridcolor='#21262d', linecolor='#30363d', tickcolor='#8b949e'),
    yaxis=dict(gridcolor='#21262d', linecolor='#30363d', tickcolor='#8b949e'),
)
DARK_LEGEND = dict(bgcolor='#161b22', bordercolor='#30363d', borderwidth=1)
COLOURS = ['#22d3ee','#f59e0b','#4ade80','#f87171','#818cf8','#fb7185','#34d399','#60a5fa']
CLS_COLOURS = {
    'Performing':'#4ade80','Pass & Watch':'#22d3ee',
    'Substandard':'#f59e0b','Doubtful':'#fb923c','Lost':'#f87171'
}

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏦 XYZ Company Ltd")
    st.markdown("---")
    st.markdown("**Filters**")

    sel_channel = st.multiselect("Channel",
        df_all['Channel'].unique().tolist(), default=[])
    sel_state = st.multiselect("State",
        sorted(df_all['State'].unique().tolist()), default=[])
    sel_status = st.multiselect("Loan Status",
        df_all['Loan Status'].unique().tolist(), default=[])
    sel_cls = st.multiselect("Classification",
        ['Performing','Pass & Watch','Substandard','Doubtful','Lost'], default=[])
    sel_region = st.multiselect("Region",
        sorted(df_all['region_name'].unique().tolist()), default=[])

    st.markdown("---")
    st.markdown("**Report Date**")
    st.markdown("📅 25 May 2026")
    st.markdown("---")
    total_loans = len(df_all)
    st.metric("Total Loans", f"{total_loans:,}")

# ── FILTER DATA ──────────────────────────────────────────────
df = df_all.copy()
if sel_channel: df = df[df['Channel'].isin(sel_channel)]
if sel_state:   df = df[df['State'].isin(sel_state)]
if sel_status:  df = df[df['Loan Status'].isin(sel_status)]
if sel_cls:     df = df[df['Current Classification'].isin(sel_cls)]
if sel_region:  df = df[df['region_name'].isin(sel_region)]

# ── HEADER ──────────────────────────────────────────────────
st.markdown("""
<div class="company-header">
  <h2 style="margin:0;font-size:24px;">🏦 XYZ Company Ltd — Loan Analytics</h2>
  <p style="margin:4px 0 0;color:#8b949e;font-size:12px;">Loan Portfolio & Recovery Intelligence Dashboard • Report Date: 25 May 2026</p>
</div>""", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋  Portfolio Report", "⚠️  Recovery Dashboard"])

# ════════════════════════════════════════════════════════════
# TAB 1 — PORTFOLIO REPORT
# ════════════════════════════════════════════════════════════
with tab1:
    # Compute KPIs
    loan_disbursed   = df['Disbursed Amount'].sum()
    mon_principal    = df['monthly_principal'].sum()
    mon_interest     = df['monthly_interest'].sum()
    mon_repayment    = df['monthly_repayment'].sum()
    total_repaid     = df['total_paid'].sum()
    par_principal    = df['PAR Principal'].sum()
    total_expected   = df['total_expected_amount'].sum()
    outstanding      = df['outstanding_amount'].sum()
    prin_arrears     = df['principal_arrears'].sum()
    int_arrears      = df['interest_arrears'].sum()
    total_arrears    = df['total_arrears'].sum()
    gross_loan       = df['Gross_loan'].sum()
    loan_balance     = gross_loan
    prin_repaid_t    = df['principal_repaid'].sum()
    int_repaid_t     = df['interest_repaid'].sum()
    wallet_bal       = df['wallet_balance'].sum()
    loan_count       = len(df)

    # Row 1
    section("DISBURSEMENT & REPAYMENT")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi("Loan Disbursed", fmt_ngn(loan_disbursed), "teal")
    with c2: kpi("Monthly Principal", fmt_ngn(mon_principal), "gold")
    with c3: kpi("Monthly Interest", fmt_ngn(mon_interest), "gold")
    with c4: kpi("Monthly Repayment", fmt_ngn(mon_repayment), "teal")
    with c5: kpi("Total Repaid", fmt_ngn(total_repaid), "green")
    with c6: kpi("PAR Principal", fmt_ngn(par_principal), "red")

    # Row 2
    section("ARREARS & OUTSTANDING")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi("Total Expected", fmt_ngn(total_expected), "white")
    with c2: kpi("Outstanding", fmt_ngn(outstanding), "gold")
    with c3: kpi("Principal Arrears", fmt_ngn(prin_arrears), "red")
    with c4: kpi("Interest Arrears", fmt_ngn(int_arrears), "red")
    with c5: kpi("Total Arrears", fmt_ngn(total_arrears), "red")
    with c6: kpi("Gross Loan", fmt_ngn(gross_loan), "white")

    # Row 3
    section("BALANCES")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: kpi("Loan Balance", fmt_ngn(loan_balance), "teal")
    with c2: kpi("Total Repaid", fmt_ngn(total_repaid), "green")
    with c3: kpi("Principal Repaid", fmt_ngn(prin_repaid_t), "green")
    with c4: kpi("Interest Repaid", fmt_ngn(int_repaid_t), "green")
    with c5: kpi("Wallet Balance", fmt_ngn(wallet_bal), "gold")
    with c6: kpi("Adj Gross Loan", fmt_ngn(gross_loan), "white")

    st.markdown("---")

    # Charts Row 1
    col_gauge, col_prev, col_curr = st.columns([1.2,1.5,1.5])

    with col_gauge:
        section("LOAN COUNT")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=loan_count,
            number={'valueformat':',','font':{'size':36,'color':'#22d3ee'}},
            gauge={
                'axis':{'range':[0,45000],'tickcolor':'#8b949e','tickwidth':1},
                'bar':{'color':'#22d3ee','thickness':0.25},
                'bgcolor':'#21262d',
                'borderwidth':0,
                'steps':[
                    {'range':[0,15000],'color':'#1f2937'},
                    {'range':[15000,30000],'color':'#1e3a4c'},
                    {'range':[30000,45000],'color':'#1a3a2a'},
                ],
                'threshold':{'line':{'color':'#f59e0b','width':3},'value':40000}
            }
        ))
        fig_gauge.update_layout(
            height=220, margin=dict(l=20,r=20,t=20,b=20),
            paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e6edf3')
        )
        st.plotly_chart(fig_gauge, width='stretch')

    with col_prev:
        section("PREVIOUS CLASSIFICATION")
        prev_cls = df['previous_classification'].value_counts().reset_index()
        prev_cls.columns = ['Classification','Count']
        fig_prev = px.pie(prev_cls, values='Count', names='Classification',
            color='Classification', color_discrete_map=CLS_COLOURS, hole=0.45)
        fig_prev.update_traces(textinfo='percent', textfont_size=11,
            marker=dict(line=dict(color='#0d1117',width=2)))
        fig_prev.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0),
            showlegend=True, **DARK_TEMPLATE,
            legend=dict(**DARK_LEGEND, orientation='v',x=1,y=0.5,font=dict(size=10)))
        st.plotly_chart(fig_prev, width='stretch')

    with col_curr:
        section("CURRENT CLASSIFICATION")
        curr_cls = df['Current Classification'].value_counts().reset_index()
        curr_cls.columns = ['Classification','Count']
        fig_curr = px.pie(curr_cls, values='Count', names='Classification',
            color='Classification', color_discrete_map=CLS_COLOURS, hole=0.45)
        fig_curr.update_traces(textinfo='percent', textfont_size=11,
            marker=dict(line=dict(color='#0d1117',width=2)))
        fig_curr.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0),
            showlegend=True, **DARK_TEMPLATE,
            legend=dict(**DARK_LEGEND, orientation='v',x=1,y=0.5,font=dict(size=10)))
        st.plotly_chart(fig_curr, width='stretch')

    # Charts Row 2
    col_state, col_channel = st.columns([1.8,1.2])

    with col_state:
        section("TOP 10 STATES BY AVG LOAN DISBURSED")
        top_states = (df.groupby('State')['Disbursed Amount']
                      .mean().sort_values(ascending=False).head(10)
                      .reset_index())
        top_states.columns = ['State','Avg Disbursed']
        fig_states = px.bar(top_states, y='State', x='Avg Disbursed',
            orientation='h', color='Avg Disbursed',
            color_continuous_scale=['#1e3a4c','#22d3ee'])
        fig_states.update_traces(
            text=top_states['Avg Disbursed'].apply(lambda x: fmt_ngn(x)),
            textposition='outside', textfont=dict(size=10,color='#e6edf3'))
        fig_states.update_layout(height=320, margin=dict(l=0,r=60,t=10,b=10),
            coloraxis_showscale=False, **DARK_TEMPLATE)
        st.plotly_chart(fig_states, width='stretch')

    with col_channel:
        section("DISBURSEMENT BY CHANNEL")
        ch_data = df.groupby('Channel')['Disbursed Amount'].sum().reset_index()
        ch_data.columns = ['Channel','Total']
        fig_ch = px.bar(ch_data, x='Channel', y='Total',
            color='Channel', color_discrete_sequence=COLOURS)
        fig_ch.update_traces(
            text=ch_data['Total'].apply(lambda x: fmt_ngn(x)),
            textposition='outside', textfont=dict(size=10))
        fig_ch.update_layout(height=320, showlegend=False,
            margin=dict(l=0,r=0,t=10,b=10),
            xaxis_tickangle=-20, **DARK_TEMPLATE)
        st.plotly_chart(fig_ch, width='stretch')

    # Charts Row 3
    col_lost, col_par = st.columns(2)
    with col_lost:
        section("LOST % BY OFFICER (TOP 10)")
        lost_df = df[df['Current Classification']=='Lost']
        off_lost = (lost_df.groupby('officer').size()
                    .sort_values(ascending=False).head(10)
                    .reset_index())
        off_lost.columns = ['Officer','Lost Loans']
        off_total = df.groupby('officer').size().reset_index()
        off_total.columns = ['Officer','Total']
        off_merged = off_lost.merge(off_total, on='Officer')
        off_merged['Lost %'] = (off_merged['Lost Loans']/off_merged['Total']*100).round(2)
        off_merged = off_merged.sort_values('Lost %', ascending=False)
        st.dataframe(off_merged[['Officer','Lost Loans','Total','Lost %']].head(10),
            width='stretch', hide_index=True,
            column_config={'Lost %':st.column_config.ProgressColumn(
                'Lost %', min_value=0, max_value=100, format="%.1f%%")})

    with col_par:
        section("PAR PRINCIPAL BY CLASSIFICATION")
        par_cls = (df[df['PAR Principal']>0]
                   .groupby('Current Classification')['PAR Principal']
                   .sum().reset_index().sort_values('PAR Principal',ascending=False))
        par_cls['PAR (₦)'] = par_cls['PAR Principal'].apply(fmt_ngn)
        par_cls['Share %'] = (par_cls['PAR Principal']/par_cls['PAR Principal'].sum()*100).round(1)
        st.dataframe(par_cls[['Current Classification','PAR (₦)','Share %']],
            width='stretch', hide_index=True)

    # Portfolio Table
    st.markdown("---")
    section("PORTFOLIO REPORT TABLE")
    disp_cols = ['Loan ID','Customer_name','Channel','State','Disbursed Amount',
                 'Loan Status','Current Classification','dpd','total_paid',
                 'total_arrears','Maturity Date']
    df_disp = df[disp_cols].copy()
    df_disp['Disbursed Amount'] = df_disp['Disbursed Amount'].apply(lambda x: f"₦{x:,.0f}")
    df_disp['total_paid']       = df_disp['total_paid'].apply(lambda x: f"₦{x:,.0f}")
    df_disp['total_arrears']    = df_disp['total_arrears'].apply(lambda x: f"₦{x:,.0f}")
    df_disp['Maturity Date']    = df_disp['Maturity Date'].dt.strftime('%d %b %Y')
    df_disp.columns = ['Loan ID','Customer Name','Channel','State','Disbursed',
                       'Status','Classification','DPD','Total Paid','Arrears','Maturity']
    st.dataframe(df_disp.head(500), width='stretch', hide_index=True, height=280)
    st.caption(f"Showing top 500 of {len(df):,} records. Apply filters to narrow results.")


# ════════════════════════════════════════════════════════════
# TAB 2 — RECOVERY DASHBOARD
# ════════════════════════════════════════════════════════════
with tab2:
    today_str = '25-May-26'
    df_ov = df[df['dpd'] > 0].copy()
    df_active = df[df['Loan Status']=='Active'].copy()

    # KPI computations
    total_due         = df_ov['total_expected_amount'].sum()
    total_overdue     = df_ov['total_arrears'].sum()
    overdue_under_rec = df_ov['Overdue Under Recovery'].sum()
    total_recovered   = df_ov['total_paid'].sum()
    count_overdue     = len(df_ov)
    pct_recovered     = (total_recovered/total_due*100) if total_due>0 else 0
    pct_overdue_rec   = (total_recovered/total_overdue*100) if total_overdue>0 else 0
    actual_inflow_today = df_ov['ACTUAL_INFLOW_TODAY'].sum()
    wallet_total      = df_ov['wallet_balance'].sum()
    newly_due         = len(df[df['dpd'].between(1,7)])

    # MTD estimates (approx 10% of total for demo)
    mtd_due           = total_due * 0.08
    mtd_overdue       = total_overdue * 0.08
    mtd_recovered     = total_recovered * 0.06
    mtd_inflow        = actual_inflow_today * 22

    # Row 1
    section("DUE & OVERDUE SUMMARY")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("Total Due",          fmt_ngn(total_due),    "teal")
    with c2: kpi("MTD Due",            fmt_ngn(mtd_due),      "gold")
    with c3: kpi("Newly Due",          f"{newly_due:,}",      "gold")
    with c4: kpi("Overdue Under Rec",  fmt_ngn(overdue_under_rec), "red")
    with c5: kpi("Count",             f"{count_overdue:,}",   "white")

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("Total Overdue",      fmt_ngn(total_overdue),  "red")
    with c2: kpi("MTD Overdue",        fmt_ngn(mtd_overdue),    "red")
    with c3: kpi("Newly Overdue",      fmt_ngn(total_overdue*0.03), "red")
    with c4: kpi("Total OD Recovery",  fmt_ngn(total_recovered),"teal")
    with c5: kpi("MTD OD Recovery",    fmt_ngn(mtd_recovered),  "teal")

    # Row 2
    section("RECOVERY PERFORMANCE")
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("Total Recovered",     fmt_ngn(total_recovered),     "green")
    with c2: kpi("MTD Recovered",       fmt_ngn(mtd_recovered),       "green")
    with c3: kpi("Recovered Today",     fmt_ngn(actual_inflow_today), "green")
    with c4: kpi("% Recovered (Total)", f"{pct_recovered:.1f}%",      "teal")
    with c5: kpi("% Overdue Rec",       f"{pct_overdue_rec:.1f}%",    "teal")

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("MTD Actual Inflow",     fmt_ngn(mtd_inflow),          "gold")
    with c2: kpi("Daily Inflow Today",    fmt_ngn(actual_inflow_today), "gold")
    with c3: kpi("Overdue Inflow Today",  fmt_ngn(actual_inflow_today*0.6), "gold")
    with c4: kpi("Wallet Balance",        fmt_ngn(wallet_total),        "teal")

    st.markdown("---")

    # Charts Row 1
    col_trend, col_growth = st.columns(2)

    with col_trend:
        section("OVERDUE & RECOVERY TREND OVER TIME")
        # Build monthly trend from data
        df_ov['val_month'] = pd.to_datetime(df_ov['Value Date']).dt.to_period('M').astype(str)
        monthly = df_ov.groupby('val_month').agg(
            Total_Expected=('total_expected_amount','sum'),
            Total_Recovered=('total_paid','sum'),
            Overdue_Under_Recovery=('Overdue Under Recovery','sum')
        ).reset_index().sort_values('val_month').tail(16)

        fig_trend = go.Figure()
        for col_name, color, dash in [
            ('Total_Expected','#f59e0b','dash'),
            ('Overdue_Under_Recovery','#f87171','solid'),
            ('Total_Recovered','#4ade80','solid')
        ]:
            fig_trend.add_trace(go.Scatter(
                x=monthly['val_month'], y=monthly[col_name]/1e6,
                name=col_name.replace('_',' '), mode='lines',
                line=dict(color=color, width=2, dash=dash),
                fill='tonexty' if col_name=='Total_Recovered' else None,
                fillcolor='rgba(74,222,128,0.05)'
            ))
        fig_trend.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=10),
            yaxis_title='₦ Million', **DARK_TEMPLATE)
        st.plotly_chart(fig_trend, width='stretch')

    with col_growth:
        section("CUMULATIVE OVERDUE GROWTH")
        df_ov_sorted = df_ov.sort_values('Value Date')
        df_ov_sorted['val_month'] = pd.to_datetime(df_ov_sorted['Value Date']).dt.to_period('M').astype(str)
        monthly_ov = df_ov_sorted.groupby('val_month')['total_arrears'].sum().cumsum().reset_index()
        monthly_ov.columns = ['Month','Cumulative Overdue']
        monthly_ov = monthly_ov.tail(16)
        fig_growth = go.Figure(go.Scatter(
            x=monthly_ov['Month'], y=monthly_ov['Cumulative Overdue']/1e6,
            mode='lines', line=dict(color='#22d3ee', width=2.5),
            fill='tozeroy', fillcolor='rgba(34,211,238,0.08)'
        ))
        fig_growth.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=10),
            yaxis_title='₦ Million', **DARK_TEMPLATE)
        st.plotly_chart(fig_growth, width='stretch')

    # Charts Row 2
    col_channel_bar, col_donut = st.columns([1.6,1])

    with col_channel_bar:
        section("EXPECTED vs OVERDUE vs RECOVERED — BY CHANNEL")
        ch_recovery = df_ov.groupby('Channel').agg(
            Total_Expected=('total_expected_amount','sum'),
            Overdue_Under_Recovery=('Overdue Under Recovery','sum'),
            Total_Recovered=('total_paid','sum')
        ).reset_index()
        ch_melt = ch_recovery.melt(id_vars='Channel', var_name='Metric', value_name='Amount')
        color_map = {'Total_Expected':'#f59e0b',
                     'Overdue_Under_Recovery':'#f87171','Total_Recovered':'#4ade80'}
        fig_bar = px.bar(ch_melt, x='Channel', y='Amount', color='Metric',
            barmode='group', color_discrete_map=color_map)
        fig_bar.update_traces(
            text=ch_melt['Amount'].apply(lambda x: fmt_ngn(x)),
            textposition='outside', textfont=dict(size=9))
        fig_bar.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=10),
            xaxis_tickangle=-10, **DARK_TEMPLATE)
        st.plotly_chart(fig_bar, width='stretch')

    with col_donut:
        section("OVERDUE BY CLASSIFICATION")
        cls_ov = df_ov.groupby('Current Classification')['Overdue Under Recovery'].sum().reset_index()
        cls_ov.columns = ['Classification','Overdue']
        fig_donut = px.pie(cls_ov, values='Overdue', names='Classification',
            color='Classification', color_discrete_map=CLS_COLOURS, hole=0.55)
        fig_donut.update_traces(textinfo='percent+label', textfont_size=10,
            marker=dict(line=dict(color='#0d1117',width=2)))
        fig_donut.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0),
            showlegend=False, **DARK_TEMPLATE)
        st.plotly_chart(fig_donut, width='stretch')

    # Breakdown Tables
    st.markdown("---")
    section("RECOVERY BREAKDOWN TABLES")
    t1,t2,t3,t4 = st.columns(4)

    def recovery_table(df_src, group_col, label):
        tbl = df_src.groupby(group_col).agg(
            Loans=('Loan ID','count'),
            Overdue=('total_arrears','sum'),
            Recovered=('total_paid','sum')
        ).reset_index()
        tbl['Rec %'] = (tbl['Recovered']/tbl['Overdue']*100).round(1).fillna(0)
        tbl = tbl.sort_values('Rec %', ascending=False).head(8)
        tbl['Overdue']   = tbl['Overdue'].apply(fmt_ngn)
        tbl['Recovered'] = tbl['Recovered'].apply(fmt_ngn)
        return tbl

    with t1:
        st.markdown("**By State**")
        st.dataframe(recovery_table(df_ov,'State','State')[['State','Loans','Rec %']],
                     width='stretch', hide_index=True, height=260)
    with t2:
        st.markdown("**By Region**")
        st.dataframe(recovery_table(df_ov,'region_name','Region')[['region_name','Loans','Rec %']],
                     width='stretch', hide_index=True, height=260)
    with t3:
        st.markdown("**By Channel**")
        st.dataframe(recovery_table(df_ov,'Channel','Channel')[['Channel','Loans','Rec %']],
                     width='stretch', hide_index=True, height=260)
    with t4:
        st.markdown("**By Cluster**")
        st.dataframe(recovery_table(df_ov,'Cluster','Cluster')[['Cluster','Loans','Rec %']],
                     width='stretch', hide_index=True, height=260)

    # Recovery Table
    st.markdown("---")
    section("RECOVERY TABLE — OVERDUE ACCOUNTS")
    rec_cols = ['Loan ID','Customer_name','Channel','State','Disbursed Amount',
                'total_arrears','total_paid','dpd','Current Classification','Recovery Rate']
    rec_disp = df_ov[rec_cols].copy()
    rec_disp['Disbursed Amount'] = rec_disp['Disbursed Amount'].apply(lambda x: f"₦{x:,.0f}")
    rec_disp['total_arrears']    = rec_disp['total_arrears'].apply(lambda x: f"₦{x:,.0f}")
    rec_disp['total_paid']       = rec_disp['total_paid'].apply(lambda x: f"₦{x:,.0f}")
    rec_disp.columns = ['Loan ID','Customer Name','Channel','State',
                        'Disbursed','Arrears','Paid','DPD','Classification','Recovery Rate']
    st.dataframe(rec_disp.head(500), width='stretch', hide_index=True, height=280)
    st.caption(f"Showing top 500 of {len(df_ov):,} overdue accounts.")

# ── FOOTER ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#8b949e;font-size:11px;padding:8px'>
  XYZ Company Ltd — Loan Analytics Dashboard &nbsp;|&nbsp;
  Built with Python & Streamlit &nbsp;|&nbsp;
  Data: Synthetic (demonstration purposes)
</div>""", unsafe_allow_html=True)
