import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

import os
OUTPUT_DIR = r'D:\\files'

# ── Styling ──────────────────────────────────────────────────────────────────
BLUE   = '#1565C0'
GREEN  = '#2E7D32'
RED    = '#C62828'
ORANGE = '#E65100'
GOLD   = '#F9A825'
GREY   = '#ECEFF1'
DARK   = '#212121'
MID    = '#546E7A'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.facecolor': GREY,
    'figure.facecolor': 'white',
    'axes.grid': True,
    'grid.color': 'white',
    'grid.linewidth': 1.2,
    'axes.labelcolor': DARK,
    'xtick.color': DARK,
    'ytick.color': DARK,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'axes.titlecolor': DARK,
})

# ── Load & Prep ───────────────────────────────────────────────────────────────
df = pd.read_excel(r'D:\\files\\Analyst_case_study_dataset_1.xls')

# Classify leads
def classify(s):
    if pd.isna(s):
        return 'Unknown'
    if s == 'Closed':
        return 'Good'
    if s in ('EP Sent', 'EP Received', 'EP Confirmed'):
        return 'Good'
    if s in ('Unable to contact - Bad Contact Information',
             'Contacted - Invalid Profile',
             "Contacted - Doesn't Qualify"):
        return 'Bad'
    return 'Unknown'

df['Quality'] = df['CallStatus'].apply(classify)
df['IsGood']  = (df['Quality'] == 'Good').astype(int)
df['IsBad']   = (df['Quality'] == 'Bad').astype(int)
df['LeadCreated'] = pd.to_datetime(df['LeadCreated'])
df['YearMonth'] = df['LeadCreated'].dt.to_period('M')
df['Week']      = df['LeadCreated'].dt.to_period('W')

# Normalise widget names (300250 == 302252)
df['WidgetClean'] = (df['WidgetName']
    .str.replace('w-300250-', 'w-302252-', regex=False)
    .str.replace('w-302252-DebtReduction1-', '', regex=False)
    .str.replace('DebtReduction1-', '', regex=False))

# Fix partner case
df['PartnerClean'] = df['Partner'].str.replace('google', 'Google', case=False).str.strip()
df.loc[df['Partner'] == 'Google', 'PartnerClean'] = 'Google'
df.loc[df['Partner'] == 'google', 'PartnerClean'] = 'Google'
df['PartnerClean'] = df['Partner'].str.title()

# Overall quality rate
overall_good = df['IsGood'].mean()
overall_bad  = df['IsBad'].mean()
print(f"Overall good rate: {overall_good:.1%}")
print(f"Overall bad rate:  {overall_bad:.1%}")
print(f"Total leads: {len(df):,}")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Overview Dashboard (pie + bar of call status)
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Lead Overview Dashboard', fontsize=16, fontweight='bold', color=DARK, y=1.01)

# Pie: quality breakdown
quality_counts = df['Quality'].value_counts()
colors_pie = [GREEN, RED, GOLD]
wedges, texts, autotexts = axes[0].pie(
    quality_counts, labels=quality_counts.index,
    colors=colors_pie, autopct='%1.1f%%', startangle=140,
    pctdistance=0.75, textprops={'fontsize': 11})
for at in autotexts:
    at.set_fontweight('bold')
axes[0].set_title('Lead Quality Distribution\n(n=3,021)', pad=15)

# Bar: call status breakdown
status_counts = df['CallStatus'].value_counts()
status_labels = [s.replace(' - ', '\n').replace('contact - ', 'contact\n') for s in status_counts.index]
bar_colors = [GREEN if s=='Closed' else
              '#66BB6A' if s in ('EP Confirmed','EP Received','EP Sent') else
              RED if 'contact' in s.lower() or 'Invalid' in s or "Qualify" in s
              else GOLD for s in status_counts.index]
bars = axes[1].barh(status_labels[::-1], status_counts.values[::-1], color=bar_colors[::-1], edgecolor='white')
for bar in bars:
    w = bar.get_width()
    axes[1].text(w + 5, bar.get_y() + bar.get_height()/2, f'{int(w):,}',
                 va='center', fontsize=9, color=DARK)
axes[1].set_xlabel('Number of Leads')
axes[1].set_title('Leads by Call Status')
axes[1].set_facecolor(GREY)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig1_overview.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig1")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Q1: Lead Quality Trend Over Time
# ─────────────────────────────────────────────────────────────────────────────
monthly = df.groupby('YearMonth').agg(
    total=('IsGood', 'count'),
    good=('IsGood', 'sum'),
    bad=('IsBad', 'sum')
).reset_index()
monthly['good_rate'] = monthly['good'] / monthly['total']
monthly['bad_rate']  = monthly['bad']  / monthly['total']
monthly['month_num'] = range(len(monthly))

# Linear regression for trend
slope, intercept, r, p, se = stats.linregress(monthly['month_num'], monthly['good_rate'])
trend_line = intercept + slope * monthly['month_num']
trend_dir  = "Improving ↑" if slope > 0 else "Declining ↓"
sig_str    = f"p={p:.3f} ({'Significant' if p<0.05 else 'Not significant'})"

fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
fig.suptitle('Q1 — Lead Quality Trends Over Time', fontsize=15, fontweight='bold', color=DARK)

labels = [str(m) for m in monthly['YearMonth']]
x = range(len(labels))

# Top: good rate
axes[0].bar(x, monthly['good_rate'], color=GREEN, alpha=0.75, label='Good Rate')
axes[0].plot(x, trend_line, color=ORANGE, linewidth=2.5, linestyle='--', label=f'Trend ({trend_dir})')
axes[0].axhline(0.096, color=RED, linewidth=2, linestyle=':', label='Target 9.6%')
axes[0].axhline(overall_good, color=BLUE, linewidth=1.5, linestyle='-', alpha=0.6,
                label=f'Overall avg {overall_good:.1%}')
axes[0].set_ylabel('Good Lead Rate')
axes[0].yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
axes[0].legend(fontsize=9)
axes[0].set_title(f'Good Lead Rate by Month  |  Trend: {trend_dir}  |  {sig_str}', fontsize=11)

for i, (rate, total) in enumerate(zip(monthly['good_rate'], monthly['total'])):
    axes[0].text(i, rate + 0.003, f'{rate:.1%}', ha='center', fontsize=8.5, color=DARK, fontweight='bold')

# Bottom: volume
axes[1].bar(x, monthly['good'],  color=GREEN, alpha=0.8, label='Good')
axes[1].bar(x, monthly['bad'],   color=RED,   alpha=0.8, label='Bad', bottom=monthly['good'])
axes[1].bar(x, monthly['total']-monthly['good']-monthly['bad'], color=GOLD, alpha=0.6,
            label='Unknown', bottom=monthly['good']+monthly['bad'])
axes[1].set_ylabel('Number of Leads')
axes[1].set_xticks(list(x))
axes[1].set_xticklabels(labels, rotation=30, ha='right')
axes[1].legend(fontsize=9)
axes[1].set_title('Lead Volume by Month', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig2_trend.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"Saved fig2 | slope={slope:.4f} p={p:.3f}")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — Q2: Widget Analysis
# ─────────────────────────────────────────────────────────────────────────────
widget = df.groupby('WidgetClean').agg(
    total=('IsGood','count'), good=('IsGood','sum')).reset_index()
widget['rate'] = widget['good'] / widget['total']
widget = widget[widget['total'] >= 20].sort_values('rate', ascending=True)

fig, ax = plt.subplots(figsize=(13, 7))
bars = ax.barh(widget['WidgetClean'], widget['rate'],
               color=[GREEN if r >= 0.096 else ORANGE if r >= overall_good else RED
                      for r in widget['rate']])
ax.axvline(overall_good, color=BLUE, linewidth=2, linestyle='--', label=f'Overall avg {overall_good:.1%}')
ax.axvline(0.096, color=RED, linewidth=2, linestyle=':', label='Target 9.6%')
for bar, total in zip(bars, widget['total']):
    w = bar.get_width()
    ax.text(w + 0.002, bar.get_y() + bar.get_height()/2,
            f'{w:.1%}  (n={total:,})', va='center', fontsize=9)
ax.xaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
ax.set_xlabel('Good Lead Rate')
ax.set_title('Q2 — Good Lead Rate by Widget / Ad Creative', fontsize=14, fontweight='bold')
ax.legend()
green_patch  = mpatches.Patch(color=GREEN,  label='≥ Target 9.6%')
orange_patch = mpatches.Patch(color=ORANGE, label='Above avg, below target')
red_patch    = mpatches.Patch(color=RED,    label='Below average')
ax.legend(handles=[green_patch, orange_patch, red_patch], fontsize=9, loc='lower right')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig3_widget.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig3")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — Q2: Multi-segment comparison (2x3 grid)
# ─────────────────────────────────────────────────────────────────────────────
def segment_bar(ax, col, title, min_n=30, rotate=False):
    seg = df.groupby(col).agg(total=('IsGood','count'), good=('IsGood','sum')).reset_index()
    seg = seg[seg['total'] >= min_n]
    seg['rate'] = seg['good'] / seg['total']
    seg = seg.sort_values('rate', ascending=False)
    colors = [GREEN if r >= 0.096 else ORANGE if r >= overall_good else RED for r in seg['rate']]
    bars = ax.bar(seg[col].astype(str), seg['rate'], color=colors, edgecolor='white')
    ax.axhline(overall_good, color=BLUE, linewidth=1.5, linestyle='--', alpha=0.8)
    ax.axhline(0.096, color=RED, linewidth=1.5, linestyle=':', alpha=0.8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
    for bar, n in zip(bars, seg['total']):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                f'{bar.get_height():.1%}\nn={n}', ha='center', fontsize=7.5)
    ax.set_title(title, fontsize=11, fontweight='bold')
    if rotate:
        ax.set_xticklabels(seg[col].astype(str), rotation=25, ha='right', fontsize=8)
    else:
        ax.set_xticklabels(seg[col].astype(str), fontsize=9)

fig, axes = plt.subplots(2, 3, figsize=(17, 11))
fig.suptitle('Q2 — Good Lead Rate by Segment', fontsize=15, fontweight='bold', color=DARK)

segment_bar(axes[0,0], 'PublisherCampaignName',  'Campaign Type\n(Online vs Call Center)')
segment_bar(axes[0,1], 'AdvertiserCampaignName', 'Advertiser Campaign\n(Branded vs Generic)', rotate=True)
segment_bar(axes[0,2], 'PartnerClean',            'Traffic Source / Partner', rotate=True)

# Debt level
debt_order = ['7500-10000','7500-15000','10001-15000','15001-20000','20001-30000',
               '30001-50000','50001-70000','70001-90000','90000-100000','More_than_100000']
seg_debt = df.groupby('DebtLevel').agg(total=('IsGood','count'), good=('IsGood','sum')).reset_index()
seg_debt['rate'] = seg_debt['good'] / seg_debt['total']
seg_debt['order'] = seg_debt['DebtLevel'].apply(lambda x: debt_order.index(x) if x in debt_order else 99)
seg_debt = seg_debt[seg_debt['total'] >= 20].sort_values('order')
colors_d = [GREEN if r >= 0.096 else ORANGE if r >= overall_good else RED for r in seg_debt['rate']]
axes[1,0].bar(seg_debt['DebtLevel'], seg_debt['rate'], color=colors_d, edgecolor='white')
axes[1,0].axhline(overall_good, color=BLUE, linewidth=1.5, linestyle='--')
axes[1,0].axhline(0.096, color=RED, linewidth=1.5, linestyle=':')
axes[1,0].yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
for bar, n in zip(axes[1,0].patches, seg_debt['total']):
    axes[1,0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                   f'{bar.get_height():.1%}\nn={n}', ha='center', fontsize=7)
axes[1,0].set_xticklabels(seg_debt['DebtLevel'], rotation=30, ha='right', fontsize=7.5)
axes[1,0].set_title('Debt Level', fontsize=11, fontweight='bold')

# Address score
seg_addr = df[df['AddressScore'].notna()].groupby('AddressScore').agg(
    total=('IsGood','count'), good=('IsGood','sum')).reset_index()
seg_addr['rate'] = seg_addr['good'] / seg_addr['total']
colors_a = [GREEN if r >= 0.096 else ORANGE if r >= overall_good else RED for r in seg_addr['rate']]
axes[1,1].bar(seg_addr['AddressScore'].astype(str), seg_addr['rate'], color=colors_a, edgecolor='white')
axes[1,1].axhline(overall_good, color=BLUE, linewidth=1.5, linestyle='--')
axes[1,1].axhline(0.096, color=RED, linewidth=1.5, linestyle=':')
axes[1,1].yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
for bar, n in zip(axes[1,1].patches, seg_addr['total']):
    axes[1,1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                   f'{bar.get_height():.1%}\nn={n}', ha='center', fontsize=8)
axes[1,1].set_xlabel('Address Score (5=perfect match)')
axes[1,1].set_title('Address Score\n(Data Quality)', fontsize=11, fontweight='bold')

# State top 10
seg_state = df.groupby('State').agg(total=('IsGood','count'), good=('IsGood','sum')).reset_index()
seg_state['rate'] = seg_state['good'] / seg_state['total']
seg_state = seg_state[seg_state['total'] >= 30].sort_values('rate', ascending=False).head(10)
colors_s = [GREEN if r >= 0.096 else ORANGE if r >= overall_good else RED for r in seg_state['rate']]
axes[1,2].bar(seg_state['State'], seg_state['rate'], color=colors_s, edgecolor='white')
axes[1,2].axhline(overall_good, color=BLUE, linewidth=1.5, linestyle='--')
axes[1,2].axhline(0.096, color=RED, linewidth=1.5, linestyle=':')
axes[1,2].yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
for bar, n in zip(axes[1,2].patches, seg_state['total']):
    axes[1,2].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                   f'{bar.get_height():.1%}\nn={n}', ha='center', fontsize=7.5)
axes[1,2].set_title('Top 10 States by Good Rate', fontsize=11, fontweight='bold')

# legend
for ax in axes.flat:
    ax.set_facecolor(GREY)

legend_patches = [
    mpatches.Patch(color=GREEN,  label='≥ Target (9.6%)'),
    mpatches.Patch(color=ORANGE, label='Above avg, below target'),
    mpatches.Patch(color=RED,    label='Below average'),
    mpatches.Patch(color=BLUE,   label=f'Overall avg ({overall_good:.1%})', linestyle='--'),
]
fig.legend(handles=legend_patches, loc='lower center', ncol=4, fontsize=10,
           bbox_to_anchor=(0.5, -0.02), framealpha=0.9)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig4_segments.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig4")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5 — Q3: Opportunity Analysis — What-if simulation
# ─────────────────────────────────────────────────────────────────────────────
# Build scenarios
scenarios = []

# Scenario 1: Drop bad partner (AdKnowledge, Advertise.com)
mask1 = ~df['PartnerClean'].isin(['Adknowledge','Advertise.Com'])
rate1 = df[mask1]['IsGood'].mean()
scenarios.append({'Scenario': 'Drop low-quality\npartners', 'Rate': rate1,
                  'Leads': mask1.sum(), 'Revenue Impact': '+Volume risk'})

# Scenario 2: Only address score >= 3 (where available, keep NaN as-is)
mask2 = (df['AddressScore'] >= 3) | df['AddressScore'].isna()
rate2 = df[mask2]['IsGood'].mean()
scenarios.append({'Scenario': 'Filter Address\nScore ≥ 3', 'Rate': rate2,
                  'Leads': mask2.sum(), 'Revenue Impact': '-Moderate volume'})

# Scenario 3: Focus on best widgets only (>= overall avg)
top_widgets = widget[widget['rate'] >= overall_good]['WidgetClean'].tolist()
mask3 = df['WidgetClean'].isin(top_widgets)
rate3 = df[mask3]['IsGood'].mean()
scenarios.append({'Scenario': 'Best widgets\nonly', 'Rate': rate3,
                  'Leads': mask3.sum(), 'Revenue Impact': '-Heavy volume loss'})

# Scenario 4: Branded campaign only
mask4 = df['AdvertiserCampaignName'] == 'creditsolutions-branded-shortform'
rate4 = df[mask4]['IsGood'].mean()
scenarios.append({'Scenario': 'Branded\ncampaign only', 'Rate': rate4,
                  'Leads': mask4.sum(), 'Revenue Impact': '-50% volume'})

# Scenario 5: Drop partner + addr score filter combined
mask5 = mask1 & mask2
rate5 = df[mask5]['IsGood'].mean()
scenarios.append({'Scenario': 'Drop bad partners\n+ Addr Score ≥ 3', 'Rate': rate5,
                  'Leads': mask5.sum(), 'Revenue Impact': 'Recommended combo'})

# Scenario 6: High debt only (>= 20k)
high_debt_vals = ['20001-30000','30001-50000','50001-70000','70001-90000',
                  '90000-100000','More_than_100000']
mask6 = df['DebtLevel'].isin(high_debt_vals)
rate6 = df[mask6]['IsGood'].mean()
scenarios.append({'Scenario': 'High debt\n(≥ $20K)', 'Rate': rate6,
                  'Leads': mask6.sum(), 'Revenue Impact': '-Moderate volume'})

scen_df = pd.DataFrame(scenarios)
scen_df = scen_df.sort_values('Rate', ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(15, 7))
fig.suptitle('Q3 — Revenue Opportunity: Path to 9.6% Quality Target', fontsize=15,
             fontweight='bold', color=DARK)

# Left: scenario rates
colors_scen = [GREEN if r >= 0.096 else ORANGE if r >= overall_good else RED for r in scen_df['Rate']]
bars = axes[0].barh(scen_df['Scenario'], scen_df['Rate'], color=colors_scen, edgecolor='white')
axes[0].axvline(overall_good, color=BLUE, linewidth=2, linestyle='--', label=f'Current {overall_good:.1%}')
axes[0].axvline(0.096, color=RED, linewidth=2, linestyle=':', label='Target 9.6%')
for bar in bars:
    w = bar.get_width()
    axes[0].text(w + 0.001, bar.get_y() + bar.get_height()/2,
                 f'{w:.1%}', va='center', fontsize=10, fontweight='bold')
axes[0].xaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
axes[0].legend(fontsize=9)
axes[0].set_title('Good Lead Rate per Scenario', fontsize=12)
axes[0].set_facecolor(GREY)

# Right: revenue impact
cpl_current = 30
cpl_target  = 33
base_volume = len(df)
for sc in scenarios:
    vol = sc['Leads']
    sc['Rev_Current'] = vol * cpl_current
    sc['Rev_Target']  = vol * cpl_target if sc['Rate'] >= 0.096 else vol * cpl_current

scen_df2 = pd.DataFrame(scenarios).sort_values('Rate', ascending=False)
x_pos = range(len(scen_df2))
width = 0.35
axes[1].bar([xi - width/2 for xi in x_pos], scen_df2['Rev_Current']/1000,
            width, label=f'At $30 CPL', color=BLUE, alpha=0.8)
axes[1].bar([xi + width/2 for xi in x_pos], scen_df2['Rev_Target']/1000,
            width, label=f'At $33 CPL (if target met)', color=GREEN, alpha=0.8)
axes[1].set_xticks(list(x_pos))
axes[1].set_xticklabels(scen_df2['Scenario'], rotation=20, ha='right', fontsize=8)
axes[1].set_ylabel('Revenue ($K)')
axes[1].legend(fontsize=9)
axes[1].set_title('Revenue Impact per Scenario\n(Volume × CPL)', fontsize=12)
axes[1].set_facecolor(GREY)
axes[1].yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'${y:.0f}K'))

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig5_opportunity.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig5")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6 — 1DC vs 2DC form analysis
# ─────────────────────────────────────────────────────────────────────────────
df['FormPages'] = df['WidgetClean'].apply(
    lambda x: '2-Page Form (2DC)' if '2DC' in str(x) else '1-Page Form (1DC)')

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle('Q2 — Form Length: 1-Page vs 2-Page Form Impact', fontsize=14,
             fontweight='bold', color=DARK)

pages = df.groupby('FormPages').agg(total=('IsGood','count'), good=('IsGood','sum')).reset_index()
pages['rate'] = pages['good'] / pages['total']
axes[0].bar(pages['FormPages'], pages['rate'],
            color=[GREEN if r >= overall_good else RED for r in pages['rate']], edgecolor='white')
axes[0].axhline(overall_good, color=BLUE, linewidth=2, linestyle='--')
axes[0].axhline(0.096, color=RED, linewidth=2, linestyle=':')
axes[0].yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
for bar, row in zip(axes[0].patches, pages.itertuples()):
    axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                 f'{bar.get_height():.1%}\nn={row.total:,}', ha='center', fontsize=10)
axes[0].set_title('Good Lead Rate by Form Length')
axes[0].set_facecolor(GREY)

# Phone score impact
ps = df[df['PhoneScore'].notna()].groupby('PhoneScore').agg(
    total=('IsGood','count'), good=('IsGood','sum')).reset_index()
ps['rate'] = ps['good'] / ps['total']
axes[1].bar(ps['PhoneScore'].astype(str), ps['rate'],
            color=[GREEN if r >= overall_good else RED for r in ps['rate']], edgecolor='white')
axes[1].axhline(overall_good, color=BLUE, linewidth=2, linestyle='--', label=f'Avg {overall_good:.1%}')
axes[1].axhline(0.096, color=RED, linewidth=2, linestyle=':', label='Target 9.6%')
axes[1].yaxis.set_major_formatter(FuncFormatter(lambda y,_: f'{y:.0%}'))
for bar, n in zip(axes[1].patches, ps['total']):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.003,
                 f'{bar.get_height():.1%}\nn={n}', ha='center', fontsize=9)
axes[1].set_xlabel('Phone Score (5=perfect match)')
axes[1].set_title('Good Lead Rate by Phone Score\n(Data Quality Signal)')
axes[1].legend(fontsize=9)
axes[1].set_facecolor(GREY)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig6_form_phone.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig6")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 7 — Statistical significance table
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
ax.axis('off')
fig.suptitle('Statistical Significance Summary — Chi-Square Tests', fontsize=14,
             fontweight='bold', color=DARK)

def chi2_test(col, min_n=20):
    seg = df.groupby(col)['IsGood'].agg(['sum','count']).reset_index()
    seg = seg[seg['count'] >= min_n]
    if len(seg) < 2:
        return None, None
    table = np.array([seg['sum'].values, (seg['count']-seg['sum']).values])
    chi2, p, dof, _ = stats.chi2_contingency(table)
    return chi2, p

tests = [
    ('Widget Creative',         'WidgetClean'),
    ('Form Pages (1DC vs 2DC)', 'FormPages'),
    ('Traffic Partner',         'PartnerClean'),
    ('Advertiser Campaign',     'AdvertiserCampaignName'),
    ('Campaign Type',           'PublisherCampaignName'),
    ('Debt Level',              'DebtLevel'),
    ('State',                   'State'),
]

rows = []
for label, col in tests:
    chi2, p = chi2_test(col)
    if p is not None:
        sig = '✅ Yes' if p < 0.05 else '❌ No'
        rows.append([label, f'{chi2:.1f}', f'{p:.4f}', sig])

table_data = [['Segment', 'Chi² Stat', 'p-value', 'Significant?']] + rows
colors_tab = [['#1565C0']*4] + [
    ['#E8F5E9' if '✅' in r[3] else '#FFEBEE']*4 for r in rows]

tbl = ax.table(cellText=table_data, cellLoc='center', loc='center',
               cellColours=colors_tab)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)
tbl.scale(1.3, 2.0)
for (row, col), cell in tbl.get_celld().items():
    if row == 0:
        cell.set_text_props(color='white', fontweight='bold')
    cell.set_edgecolor('white')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'fig7_stats.png'), dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig7")

print("\n✅ All charts saved!")

# Print summary stats for PDF
print("\n─── SUMMARY STATS ───")
print(f"Total leads: {len(df):,}")
print(f"Overall good rate: {overall_good:.2%}")
print(f"Target rate: 9.60%")
print(f"Gap: {0.096 - overall_good:.2%}")
print(f"\nTrend: slope={slope:.5f}, p={p:.4f}, direction={trend_dir}")
print(f"\nScenario results:")
for s in scenarios:
    print(f"  {s['Scenario'].replace(chr(10),' ')}: {s['Rate']:.2%} (n={s['Leads']:,})")
