import pandas as pd
from sqlalchemy import create_engine

# Step 1: MySQL connection details
host = "localhost"  
user = "root"       
password = "MYSQL"  # add your actual password
database = "inventory"   
table_name = "sales"  
csv_file = r"C:\Users\abhis\Desktop\vendor_inventory\data\sales.csv"
new_path = csv_file.replace("\\", "/")

# Step 2: Read CSV file
df = pd.read_csv(new_path)

# Step 3: Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Step 4: Write DataFrame to MySQL
try:
    df.to_sql(name=table_name, con=engine, index=False, if_exists="replace")
    print(f"Table `{table_name}` created successfully in database `{database}`.")
except Exception as e:
    print("Error:", e)
