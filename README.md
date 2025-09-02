📦 Vendor Inventory Analysis
📌 Overview

This project analyzes vendor purchase, sales, and inventory data to uncover insights on profitability, pricing strategies, vendor performance, and inventory optimization.

The workflow includes:

Data cleaning & summary table creation

Exploratory Data Analysis (EDA)

Vendor performance benchmarking

Insights on costs, margins, and unsold inventory

🗂 Data Sources

Purchases Table – product purchase details

Sales Table – sales transactions and revenue

Vendor Invoice Table – aggregated vendor purchases with freight cost

Purchase Prices Table – product-wise prices (purchase & actual)

⚙️ Tech Stack

Python (pandas, numpy, matplotlib, seaborn)

SQL (joins & summary table creation)

Jupyter Notebooks



Git & GitHub
# Clone the repo
git clone https://github.com/abheeshek02/vendor_inventory.git
cd vendor_inventory

# Create virtual environment
python -m venv env
env\Scripts\activate   # (Windows)

# Install requirements
pip install -r requirements.txt

# Run Jupyter Notebook
jupyter notebook

 Results & Insights

Bulk purchasing reduces costs by up to 72%.

High sales volumes often come at lower margins.

Unsold inventory locks significant capital.

Vendor performance varies — top vendors dominate sales but not always profits.
