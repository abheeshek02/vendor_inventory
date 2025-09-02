import pandas as pd
import numpy as np
import logging
from sqlalchemy import create_engine

# Logging setup
logging.basicConfig(
    filename="vendor_summary.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)


def load_vendor_sales_summary():
    logging.info(" Script started")

    try:
        # MySQL connection setup
        host = "localhost"
        user = "root"
        password = "MYSQL"
        database = "inventory"

        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")
        logging.info(" Connected to MySQL successfully")

        # SQL query
        query = """
        WITH FreightSummary AS (
            SELECT VendorNumber, SUM(Freight) AS FreightCost
            FROM vendor_Invoice 
            GROUP BY VendorNumber
        ),
        PurchaseSummary AS (
            SELECT
                p.VendorNumber,
                p.VendorName,
                p.Brand,
                p.Description,
                p.PurchasePrice,
                pp.Volume,
                pp.Price AS AcutalPrice,
                SUM(p.Quantity) AS TotalPurchaseQuantity,
                SUM(p.Dollars) AS TotalPurchaseDollars
            FROM purchase p 
            JOIN purchase_price pp ON p.Brand = pp.Brand
            WHERE p.PurchasePrice > 0
            GROUP BY p.VendorNumber, p.VendorName, p.Brand, p.Description, p.PurchasePrice, pp.Price, pp.Volume
        ),
        SalesSummary AS (
            SELECT
                VendorNo, 
                Brand,
                SUM(SalesDollars) AS TotalSalesDollars,
                SUM(SalesPrice) AS TotalSalePrice,
                SUM(SalesQuantity) AS TotalSaleQuantity,
                SUM(ExciseTax) AS TotalExciseTax
            FROM sales
            GROUP BY VendorNo, Brand
        )
        SELECT 
            ps.VendorNumber,
            ps.VendorName,
            ps.Brand,
            ps.Description,
            ps.PurchasePrice,
            ps.AcutalPrice,
            ps.Volume,
            ps.TotalPurchaseQuantity,
            ps.TotalPurchaseDollars,
            ss.TotalSaleQuantity,
            ss.TotalSalesDollars,
            ss.TotalSalePrice,
            ss.TotalExciseTax,
            fs.FreightCost 
        FROM PurchaseSummary ps
        LEFT JOIN SalesSummary ss
            ON ps.VendorNumber = ss.VendorNo 
            AND ps.Brand = ss.Brand 
        LEFT JOIN FreightSummary fs 
            ON ps.VendorNumber = fs.VendorNumber
        ORDER BY ps.TotalPurchaseDollars DESC;
        """

        vendor_sales_summary = pd.read_sql(query, con=engine)
        logging.info(" Data fetched from database")

        # Data cleaning
        vendor_sales_summary = vendor_sales_summary.replace([np.inf, -np.inf], np.nan)
        vendor_sales_summary.fillna(0, inplace=True)
        vendor_sales_summary['VendorName'] = vendor_sales_summary['VendorName'].str.strip()
        vendor_sales_summary['Volume'] = vendor_sales_summary['Volume'].astype('float64')

        # Calculated columns
        vendor_sales_summary['GrossProfit'] = (
            vendor_sales_summary['TotalSalesDollars'] - vendor_sales_summary['TotalPurchaseDollars']
        )

        vendor_sales_summary['ProfitMargin'] = np.where(
            vendor_sales_summary['TotalSalesDollars'] > 0,
            (vendor_sales_summary['GrossProfit'] / vendor_sales_summary['TotalSalesDollars']) * 100,
            0
        )

        vendor_sales_summary['StockTurnover'] = np.where(
            vendor_sales_summary['TotalPurchaseQuantity'] > 0,
            vendor_sales_summary['TotalSaleQuantity'] / vendor_sales_summary['TotalPurchaseQuantity'],
            0
        )

        vendor_sales_summary['SalesPurchaseRatio'] = np.where(
            vendor_sales_summary['TotalPurchaseDollars'] > 0,
            vendor_sales_summary['TotalSalesDollars'] / vendor_sales_summary['TotalPurchaseDollars'],
            0
        )

        vendor_sales_summary = vendor_sales_summary.rename(columns={"AcutalPrice": "ActualPrice"})
        logging.info(" Data cleaned & calculated columns added")

        # Final cleaning: ensure NO inf/nan before inserting
        vendor_sales_summary = vendor_sales_summary.replace([np.inf, -np.inf], np.nan)
        vendor_sales_summary.fillna(0, inplace=True)

        # Force numeric columns to valid floats
        for col in vendor_sales_summary.select_dtypes(include=[np.number]).columns:
            vendor_sales_summary[col] = pd.to_numeric(vendor_sales_summary[col], errors="coerce").fillna(0)

        logging.info("✅ Final cleaning done, no inf/nan left")

        # 🚀 Drop duplicates on PRIMARY KEY columns before insert
        vendor_sales_summary.drop_duplicates(
            subset=["VendorNumber", "Brand"],  
            keep="last",
            inplace=True
        )
        logging.info("✅ Duplicates dropped on VendorNumber + Brand")

        # Insert into MySQL
        vendor_sales_summary.to_sql(
            name='vendor_sales_summary',
            con=engine,
            if_exists='append',
            index=False,
            method="multi"  # safer bulk insert
        )
        logging.info("✅ Data inserted successfully into MySQL table 'vendor_sales_summary'")

        print("✅ Data Load Completed. Here are the first 10 rows:\n")
        print(vendor_sales_summary.head(10))  # 👀 Preview in console
        return vendor_sales_summary

    except Exception as e:
        logging.error(f"❌ Error occurred: {e}")
        print(f"❌ Error: {e}")


# Run function
if __name__ == "__main__":
    df = load_vendor_sales_summary()
