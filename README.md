# Lending Club Credit-Risk Analysis

**What drives a loan to default — and how much money is actually at risk?**

I analyzed **1.3 million real Lending Club loans** (2007–2018) end-to-end: cleaning the raw data in Python/pandas, finding what predicts default, and building an interactive dashboard. This README walks through *how I thought about the problem* — the questions I asked, the decisions I made, and what I found.

📊 **[View the interactive Tableau dashboard →](https://public.tableau.com/app/profile/nirmala.choudhary/viz/LendingClubCredit-RiskAnalysis/Dashboard1)**

> **Headline:** Of **$18.76B** lent, **$4.06B (21.6%)** went to borrowers who defaulted. And that risk isn't random — it follows clear, predictable patterns.

![Dashboard](Dashboard%201.png)

---

## The business question

Lending Club is a peer-to-peer lender: people borrow money, investors fund it. The whole business depends on one thing — **predicting who pays back and who doesn't.**

So I framed the project around questions a real credit-risk team would ask:

1. **Does the lender's grading system (A–G) actually sort risk** — or is it just a label?
2. **Is risk priced correctly?** Do riskier borrowers pay enough interest to cover their losses?
3. **What features of a loan signal danger** — the loan term? the reason for borrowing? the borrower's finances?
4. **How much money is genuinely at risk** — not as a percentage, but in dollars?

---

## The data

- **Source:** Lending Club loan data (Kaggle) — 2.26M loans × 145 columns of raw data.
- **First decision — avoid data leakage:** Many columns are only known *after* a loan goes bad (e.g. recovery amounts, last payment date). Using those to "predict" default would be cheating — the model would only work in hindsight. So I selected **~22 columns that are knowable at the moment the loan is approved**: amount, term, grade, interest rate, purpose, income, debt-to-income, employment length, etc.
- **Defining the target:** I kept only loans with a *final* outcome (`Fully Paid`, `Charged Off`, `Default`) and built a binary flag — `defaulted` = 1 if charged off/defaulted, 0 if fully paid. Loans still "Current" were dropped: we don't yet know how they end.

> 💡 *A 0/1 column has a useful property: its **average equals the rate**. The mean of `defaulted` is 0.20 → a 20% overall default rate. I used this trick throughout.*

---

## Part 1 — Cleaning the data (and the decisions behind it)

Real data is messy. I followed a deliberate sequence: **fix types → handle missing values → remove garbage → check duplicates → save a clean file.** Here's the thinking at each step.

### Fixing column types
`term` was stored as `"36 months"` (text) and dates as `"Dec-2015"` (text) — you can't sort or calculate on those. I extracted the numbers (`"36 months"` → `36`) and parsed the dates into real datetime values.

### Missing values — the moment I caught my own mistake
When I counted missing values, `emp_length` showed **100% missing**. My instinct: *that's not missing data — that's a broken column.* A few hundred gaps is normal; an entire column gone means I broke it somewhere.

I went back to the **raw file as the source of truth** and checked — the real values (`"10+ years"`, `"2 years"`, `"n/a"`) were perfectly fine. My notebook had accidentally clobbered the column by re-running cells out of order. I re-extracted it cleanly from the original file.

**Then I triaged each gap by size:**
- `emp_length` had ~75,000 genuine missing values (5.8%) → too much real data to throw away, so I **filled with the median** (6 years — outlier-proof).
- `revol_util`, `dti`, `pub_rec_bankruptcies` had only a few hundred gaps each → **dropped those rows** (losing 1,800 of 1.3M changes nothing).

> 💡 *Lesson I took from this: 100% missing ≠ missing data — it means **you** broke the column. Always check reality (`.dtypes`, the raw file) instead of guessing.*

### Catching garbage values
I ran `describe()` and compared every column's min/max to what's actually possible. `dti` (debt-to-income ratio) had a **min of -1** (a debt ratio can't be negative) and a **max of 999** (a fake placeholder cap). Both are junk. I kept only the valid 0–100 range, dropping 478 bad rows.

I also noticed `annual_inc` had a mean ($76k) well above its median ($65k), with a max of $11M. That's **not** garbage — it's a few high earners pulling the average up (right-skew). The median is the honest "typical" income. Knowing the difference between *skew* and *error* matters.

### Result
**2.26M raw rows → 1,301,341 clean rows × 23 columns, zero missing values.** Saved to a fresh file so the cleaning never has to be redone.

---

## Part 2 — What I found

### 1. The grading system works — risk climbs cleanly from A to G
Average default rate by grade:

| A | B | C | D | E | F | G |
|---|---|---|---|---|---|---|
| 6% | 13% | 23% | 30% | 39% | 45% | **50%** |

A perfect, monotonic climb. **Grade G defaults 8× more often than Grade A.** This both confirms the lender's risk model is real *and* validates my cleaning — broken data would have produced noise, not this clean staircase.

### 2. Risk is priced — but maybe not enough
Average interest rate by grade climbs the same way: **7% (A) → 28% (G).** So riskier borrowers do pay more.

But pairing the two findings raised the sharpest question of the project: **Grade G borrowers default 50% of the time but are only charged ~28% interest. Is 28% enough to cover losing half your loans?** That's a genuine risk-based-pricing-adequacy tension a credit team would investigate.

### 3. Longer loans are riskier
60-month loans default **33%** vs **16%** for 36-month loans — **twice the risk.** A longer term gives life more time to go wrong (job loss, illness, emergencies).

### 4. Why someone borrows predicts whether they repay
Default rate by purpose ranged from **small business (30% — riskiest)** down to **weddings (12% — safest)** — nearly 3× difference. Small businesses mostly fail, and the loan rides on the business surviving; a wedding is a one-time, planned expense.

### 5. The profile of a defaulter (and what *doesn't* matter)
Comparing borrowers who defaulted vs those who repaid:

| | Interest rate | Debt-to-income | Annual income | Employment length |
|---|---|---|---|---|
| Repaid | 12.6% | 17.7 | $77,654 | 6.1 yrs |
| **Defaulted** | **15.7%** | **20.1** | **$70,369** | 6.0 yrs |

Defaulters carry **higher interest, higher debt-to-income, and lower income.** The surprise: **employment length barely differs** — it doesn't predict default. *Reporting what doesn't matter is just as valuable as reporting what does* — it tells a lender which signals to stop weighting.

### The headline — putting dollars on the risk
- **Total lent:** $18,763,000,150 (**$18.76B**)
- **In defaulted loans:** $4,061,573,400 (**$4.06B**)
- **% of money at risk:** **21.6%**

One subtlety worth flagging: **21.6% of the money is at risk, but only ~20% of loans default.** That gap means **defaulted loans tend to be larger than average** — bigger loans are harder to repay. The dollar view tells a slightly scarier story than the count view.

---

## Part 3 — An AI layer that writes the analyst's takeaway

A dashboard tells you *what happened*; a hiring manager wants to know *what to do about it*. So I added an **AI insight layer** (`ai_insights.py`): pandas boils the data down to a small facts table (default rate + dollars by grade), and that table is passed to a large language model (**Llama 3.3 via the Groq API**) with a role-based prompt asking for a finding → dollar impact → recommendation. The result — generated automatically from the real numbers, not written by hand:

> 🤖 *"The default rate increases sharply as loan grade deteriorates, with the riskiest grade G loans defaulting at 50.09%, more than 8 times the 6.09% rate of grade A. The total lent to the four riskiest grades (D–G) is approximately $2.25 billion, exposing a significant portion of the portfolio to high default risk. To mitigate this, I recommend immediately increasing reserve requirements for grades D, E, F, and G by at least 20%."*

Every figure it cites traces back to the cleaned dataset. The API key is loaded from a gitignored `.env` (never hard-coded), and the summariser is a reusable `generate_insight()` function, so any facts table can be turned into an executive summary. This turns the project from **descriptive** ("here's the default rate") into **prescriptive** ("here's the risk, the money, and the fix").

---

## Recommendations a credit team could act on

1. **Re-examine pricing on the lowest grades (F/G).** If a 50%-default grade only earns 28% interest, the math may not work — either raise rates or tighten approval.
2. **Treat 60-month loans as a distinct risk tier** — they default at double the rate.
3. **Add purpose to risk scoring.** Small-business loans need extra scrutiny or collateral.
4. **Stop weighting employment length** as a default signal — the data says it doesn't discriminate.

---

## Tools & method

- **Python / pandas** — data cleaning, type fixing, missing-value handling, analysis
- **Jupyter Notebook** — the full analysis ([`lending_club_analysis.ipynb`](lending_club_analysis.ipynb)), built to run top-to-bottom reproducibly
- **Tableau Public** — the [interactive dashboard](https://public.tableau.com/app/profile/nirmala.choudhary/viz/LendingClubCredit-RiskAnalysis/Dashboard1)
- **LLM / Groq API (Llama 3.3)** — the AI insight layer ([`ai_insights.py`](ai_insights.py)) that auto-writes the executive takeaway, with secure `.env` key handling and structured prompt design
- **Framework** — the standard analyst workflow: Ask → Prepare → Process → Analyze → Share → Act

> The raw and cleaned CSVs (1.6 GB) are excluded from this repo. The original data is public on Kaggle; `LCDataDictionary.xlsx` documents every column.

---

## What I'd do next
- Build a logistic-regression model to *predict* default probability per loan (this analysis is the feature-selection groundwork).
- Layer in time: did default rates spike around specific years / economic conditions?
- Calculate expected loss per grade (default rate × loan size × loss-given-default) to formally test the pricing question.

---

*Built by **Nirmala Choudhary** — Data Analyst. [Portfolio](https://nikita1-pixel.github.io/) · [Tableau Public](https://public.tableau.com/app/profile/nirmala.choudhary/viz/LendingClubCredit-RiskAnalysis/Dashboard1)*
