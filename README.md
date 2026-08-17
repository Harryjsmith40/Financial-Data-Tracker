# Financial Data Tracker

## Requirements

- Python 3.13.13
- CSV export from your bank

## Installation

1. Clone the repository
2. Install dependencies

```
pip install -r requirements.txt
```

## Usage

1. Place your CSV export in the Data folder
2. Run the program with python main.py
3. Follow the prompts to upload or visualise

## Data Format

Your CSV export should have the following columns in this order:
date,amount,desc,balance
25/12/2020,-15.00,Coles,1000.00

## Data Storage

Data is stored locally in a DuckDB database (`Data/data_base.db`), created automatically on first run. Two tables:

- **accounts** — one row per tracked account (`account_id`, `account_name`, `account_type`, `last_updated`)
- **master** — one row per transaction (`master_id`, `date`, `amount`, `desc`, `balance`, `account_name`, `account_type`)

Both tables use a DuckDB `SEQUENCE` to auto-generate primary keys, since DuckDB has no built-in `AUTOINCREMENT`.

### Why DuckDB over SQLite

This project's read pattern is aggregation-heavy (net worth over time, spending/income by category, sums across accounts) rather than single-row lookups — an OLAP-shaped workload. DuckDB's columnar storage is optimised for scanning and aggregating across columns, whereas SQLite's row-oriented storage is optimised for OLTP-style single-row reads/writes. DuckDB also queries pandas DataFrames directly without a separate load step, fitting the existing pandas-based pipeline.

```
flowchart TD
    A([Start]) --> B{Upload or Visualise?}
    B -->|A Upload| C[Upload File]
    B -->|B Visualise| D[Visualisation Options]
    B -->|C Exit| E([Exit])

    D --> F{Plot Type?}
    F -->|A Net Worth| G[Networth Plot]
    F -->|B Expenses| H[Spending Plot]
    F -->|C Income| I[Income Plot]
    F -->|D Back to main menu| B
    F -->|E Exit| E1([Exit])

    G --> G1[Pivot Table\naggfunc=last]
    G1 --> G2[Forward Fill\nFill days with no transactions]
    G2 --> G3[Sum across accounts]
    G3 --> PLOT[Format and Display Graph]
    PLOT --> F

    H --> J1[Filter Expenses]
    I --> J2[Filter Income]
    J1 --> J2[⚠️ Known Issue ⚠️ Current internal transfers will show towards income and expenses in the data]
    J2 --> J3[Pivot Table\naggfunc=sum]
    J3 --> J4[Sum across accounts]
    J4 --> PLOT

    C --> C1{CSV Filename?}
    C1 --> B
    C1 --> C2[Build File Path]
    C2 --> C3[File Exists?]
    C3 -->|Yes| C5[⚠️ Clean Data ⚠️ Transaction Order column unused]
    C5 --> C6[Select Account]
    C6 --> C7[Deduplicate\nLeft merge with master]
    C7 --> C8[Bulk Insert to DuckDB master table]
    C8 --> B
    C3 -->|No| C1
```

## The Problem

I need a financial tracker that can manage multiple accounts and account types in order to be able to visualise the complete picture of my finances historically, currently and their forecast in one program.

## Solution

Key reasons other methods have failed:

- Manual input of every transaction required
- Manual categorisation even on repeats
- Lacks financial picture across accounts
- Lacks a historical context and future forecast

Key techniques aimed to boost long term success chance:

- Historical context highlights improvements and changes in spending
- Future forecasts make the ability to achieve goals crystal clear
- Reduction of friction of use by limiting manual input needed, done via:
  - Autocategorisation where possible
  - Transaction input being a downloaded CSV
  - Tracking all accounts shows the full picture

## The Plan

Key Stages:

### Stage 1 (Reordered)

The basic program

- 1. Basic shell i/o that takes CSV from my main account, stores it in a master record, cleans data to ensure no repeats or invalid data
- 1.2 Add the ability to use multiple accounts *(developed before 1.1, as multi-account support was required for meaningful visualisation)*
- 1.1 Track and visualise net worth, spending and income *(developed after 1.2)*
- 1.3 Migrate storage from CSV to a DuckDB database, to support the aggregation-heavy access pattern above and remove manual file handling

### Stage 2

Machine learning / artificial intelligence categorisation

- 2. Train a model in order to categorise transactions automatically; if confidence score is below X% flag for manual review, if confidence score is below X% do not categorise and ask for manual review
- 2.1 Use new categories to increase data visualisation detail

## Known Issues

- Internal transfers currently show towards both income and expenses in the visualised data (tracked separately)
- `account_id` selection currently assumes contiguous IDs starting at 1; not yet robust to account deletion (not a feature yet)

## Skills

Python, Pandas, SQL, DuckDB, OOP design , Matplotlib, Git, ML model building and training (planned)