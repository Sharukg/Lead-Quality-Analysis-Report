# 📊 Lead Quality Analysis Report

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458?style=flat&logo=pandas)
![matplotlib](https://img.shields.io/badge/matplotlib-Visualisation-orange?style=flat)
![scipy](https://img.shields.io/badge/scipy-Statistics-8CAAE6?style=flat)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=flat)

---

## 📌 Project Overview

This project is a complete end-to-end data analytics challenge submitted as part of the **Associate Analyst hiring process at Aarki**. The dataset contains **3,021 debt-reduction leads** sold to an advertiser between April–September 2009. The goal was to analyse lead quality, identify key drivers, and determine whether a 20% quality improvement target was achievable to unlock a higher Cost Per Lead (CPL) from the advertiser.

---

## 🎯 Business Questions Answered

| # | Question | Key Finding |
|---|---|---|
| 1 | Are lead quality trends improving or declining over time? Are they statistically significant? | Slight upward trend (slope = +0.0043/month) but **NOT statistically significant** (p = 0.387) |
| 2 | What segments drive differing lead quality rates? | **Traffic Partner** and **Debt Level** are the only statistically proven drivers (p < 0.05) |
| 3 | Can we hit 9.6% quality to earn a $33 CPL (up from $30)? | **Already at 13.0%** — well above target. Focus is on maintaining quality at scale |

---

## 📁 Project Structure

```
lead-quality-analysis/
│
├── 📂 data/
│   └── Analyst_case_study_dataset.xls        # Raw dataset (3,021 leads)
│
├── 📂 charts/
│   ├── fig1_overview.png                      # Lead quality distribution
│   ├── fig2_trend.png                         # Monthly quality trend + regression
│   ├── fig3_widget.png                        # Widget / ad creative performance
│   ├── fig4_segments.png                      # Multi-segment analysis grid
│   ├── fig5_opportunity.png                   # Scenario revenue analysis
│   ├── fig6_form_phone.png                    # Form length + phone score
│   └── fig7_stats.png                         # Statistical significance table
│
├── 📂 output/
│   └── Lead_Quality_Analysis_Report.pdf       # Final submission PDF report
│
├── analysis_code.py                           # Main Python analysis script
└── README.md                                  # This file
```

---

## 🛠️ Tools & Libraries Used

| Tool | Purpose |
|---|---|
| **Python 3.10+** | Core programming language |
| **pandas** | Data loading, cleaning, groupby aggregations |
| **matplotlib** | All 7 charts and visualisations |
| **seaborn** | Visual styling and chart theming |
| **scipy.stats** | Linear regression + chi-square statistical tests |
| **reportlab** | Multi-page PDF report generation |
| **xlrd / openpyxl** | Reading the legacy .xls Excel file |
| **numpy** | Numerical operations for regression |

---

## 📊 Charts & Visualisations

### Figure 1 — Lead Quality Overview Dashboard
Pie chart showing Good (13%), Bad (16.2%), Unknown (70.8%) distribution alongside a horizontal bar chart of all call statuses.

### Figure 2 — Lead Quality Trend Over Time
Monthly good-lead rate bars with a linear regression trend line, 9.6% target reference line, and stacked volume breakdown by month.

### Figure 3 — Widget / Ad Creative Performance
Horizontal bar chart ranking each ad widget by good-lead rate. Colour coded: 🟢 Green = meets target, 🟠 Orange = above average, 🔴 Red = below average.

### Figure 4 — Multi-Segment Analysis Grid
2×3 grid of bar charts covering 6 segments: Campaign Type, Advertiser Campaign, Traffic Partner, Debt Level, Address Score, and Top 10 States.

### Figure 5 — Scenario Revenue Analysis
What-if analysis showing quality rate and revenue impact ($30 vs $33 CPL) for 6 business strategy scenarios.

### Figure 6 — Form Length & Phone Score
Side-by-side comparison of 1-page vs 2-page form quality rates, and Phone Score (1–5) impact on lead quality.

### Figure 7 — Statistical Significance Table
Chi-square test results for all 7 segments, showing which differences are statistically real vs. random noise.

---

## 🔬 Methodology

### Lead Quality Classification
| Category | Call Statuses |
|---|---|
| ✅ **Good** | Closed, EP Sent, EP Received, EP Confirmed |
| ❌ **Bad** | Unable to Contact, Contacted - Invalid Profile, Contacted - Doesn't Qualify |
| ⚪ **Unknown** | NULL / all other statuses |

### Statistical Tests
- **Q1 Trend:** OLS Linear Regression using `scipy.stats.linregress()` on monthly good-lead rate vs. month index
- **Q2 Segments:** Chi-square test of independence using `scipy.stats.chi2_contingency()` on 2×N contingency tables
- **Significance threshold:** p < 0.05 (two-tailed, 95% confidence level)

---

## 📈 Key Findings

### 1. Quality Trend
- Slight upward trend of **+0.43% per month**
- p-value = 0.387 → **NOT statistically significant**
- R-squared = 0.11 → Time explains only 11% of quality variance
- Recommendation: Monitor monthly; collect 12+ months of data before concluding

### 2. Lead Quality Drivers
- **✅ Traffic Partner** (p = 0.003) — Google/Yahoo outperform AdKnowledge significantly
- **✅ Debt Level** (p = 0.000) — Strongest signal; $50K–$90K debt range converts at 18–19%
- ❌ Widget creative, form length, campaign type, state — differences not statistically conclusive

### 3. Path to CPL Uplift
| Scenario | Quality Rate | Notes |
|---|---|---|
| Best widgets only | 13.9% | ✅ Above target |
| High debt (≥ $20K) | 13.7% | ✅ Above target |
| Branded campaign | 13.0% | ✅ Above target |
| Filter Address Score ≥ 3 | 13.0% | ✅ Above target |
| Drop bad partners | 12.6% | ✅ Above target |

---

## ✅ Recommended Actions

| # | Action | Expected Impact | Ease |
|---|---|---|---|
| 1 | Scale 1DC-CreditSolutions widget | Maintain 14%+ rate | 🟢 Easy |
| 2 | Pause AdKnowledge traffic | Remove low-quality source | 🟢 Easy |
| 3 | Require Debt ≥ $20K in form | Filter low-intent leads | 🟡 Medium |
| 4 | Require Address Score ≥ 3 | Remove unverified leads | 🟡 Medium |
| 5 | Shift budget to Branded campaign | Better intent signals | 🟢 Easy |
| 6 | Expand Call Center channel | Human validation = quality | 🔴 Hard |

---

## ⚠️ Data Limitations

- Address and Phone Scores are only available for ~40–60% of leads (collected only from mid-period onwards)
- 70.8% of leads have Unknown status — if these resolve to Bad, overall quality could drop significantly
- 6 months of data is insufficient for strong trend conclusions; 12+ months recommended
- Widget sizes 300×250 and 302×252 were normalised as they represent the same ad unit
- 1DC-yellowarrow has the highest rate (24.5%) but only 49 leads — treat as directional only

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/your-username/lead-quality-analysis.git
cd lead-quality-analysis
```

### 2. Install dependencies
```bash
pip install pandas matplotlib seaborn scipy openpyxl xlrd reportlab numpy
```

### 3. Update file path in `analysis_code.py`
Open `analysis_code.py` and update line 1 to point to your local dataset:
```python
df = pd.read_excel('data/Analyst_case_study_dataset.xls')
```
Also update all chart save paths to your local output folder:
```python
OUTPUT_DIR = 'charts/'   # add this near the top
```

### 4. Run the analysis
```bash
python analysis_code.py
```
All 7 chart PNG files will be saved to your `charts/` folder.

---

## 📄 Output

The final PDF report `Lead_Quality_Analysis_Report.pdf` includes:
- Cover page with KPI summary
- Executive summary table
- Q1 trend analysis with statistical test results
- Q2 segment analysis across 7 dimensions
- Q3 scenario analysis with revenue projections
- Recommended actions table
- Data limitations and methodology appendix

---

## 👤 Author

**Sharukesh**

---

> *"The current good-lead rate of 13.0% already exceeds the 9.6% target. The priority is not chasing quality — it is protecting it at scale."*
