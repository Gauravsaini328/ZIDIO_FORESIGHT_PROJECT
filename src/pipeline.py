import pandas as pd
from pathlib import Path

# reading all CSV
sales = pd.read_csv('data/raw/sales_daily.csv')
sku_master = pd.read_csv('data/raw/sku_master.csv')
calendar = pd.read_csv('data/raw/calendar.csv')
inventory_snapshots = pd.read_csv('data/raw/inventory_snapshots.csv')

# Checking Shapes
print(sales.shape)
print(sku_master.shape)
print(calendar.shape)
print(inventory_snapshots.shape)

# Checking missing values
print("Sales missing values:")
print(sales.isnull().sum())

print("SKU Master missing values:")
print(sku_master.isnull().sum())

print("Calendar missing values:")
print(calendar.isnull().sum())

print("Inventory missing values:")
print(inventory_snapshots.isnull().sum())

# Checking Datatypes
print(sales.dtypes)
print(sku_master.dtypes)
print(calendar.dtypes)
print(inventory_snapshots.dtypes)

# Converting Required Datatypes
sales["Date"] =pd.to_datetime(sales['Date'])
sku_master["Launch_Date"] =pd.to_datetime(sku_master['Launch_Date'])
calendar["date"] =pd.to_datetime(calendar['date'])
inventory_snapshots["Snapshot_Date"] =pd.to_datetime(inventory_snapshots['Snapshot_Date'])

# Printing Changed Datatypes
print(sales["Date"].dtype)
print(sku_master["Launch_Date"].dtype)
print(calendar["date"].dtype)
print(inventory_snapshots["Snapshot_Date"].dtype)

# Check duplicate rows
print("Sales duplicate rows:",sales.duplicated().sum())
print("SKU Master duplicate rows:",sku_master.duplicated().sum())
print("Calendar duplicate rows:", calendar.duplicated().sum())
print("Inventory duplicate rows:",inventory_snapshots.duplicated().sum())
print("Sales duplicate SKU-Date rows:", sales.duplicated(subset=["SKU", "Date"]).sum())

# Checking invalid values of sales
print("Negative Units Sold:",(sales["Units_Sold"]< 0).sum())
print("Negative Revenue:",(sales["Revenue"]< 0).sum())
print("Negative Price:",(sales["Price"]<0).sum())

# Checking invalid values of sku_master
print("Negative Cost Price:", (sku_master['Cost_Price']<0).sum())
print("Negative Selling Price:",(sku_master["Selling_Price"]<0).sum())

# Checking invalid values of inventory_snapshots
print("Negative Current Stock:",(inventory_snapshots["Current_Stock"]<0).sum())
print("Negative On Order:",(inventory_snapshots["On_Order"]< 0).sum())
print("Negative Lead Time:",(inventory_snapshots["Lead_Time_Days"]< 0).sum())
print("Negative Safety Stock:",(inventory_snapshots["Safety_Stock"]< 0).sum())
print("Negative Reorder Point:",(inventory_snapshots["Reorder_Point"]<0).sum())
print("Negative Inventory Value:", (inventory_snapshots["Inventory_Value"]<0).sum())

# Handling missing event values in calendar
calendar["holiday"] = calendar["holiday"].fillna("None")
calendar["promotion_event"] = calendar["promotion_event"].fillna("None")

# Verify that the missing values have been handled
print("Calendar missing event values:")
print(calendar[["holiday","promotion_event"]].isnull().sum())

# Checking all Sales SKUs exist in SKU master
sales_skus_not_in_master = sales[~sales["SKU"].isin(sku_master["SKU"])]

print("Sales records with SKU not in master:",len(sales_skus_not_in_master))

# Checking all inventory SKUs exist in SKU Master
inventory_skus_not_in_master = inventory_snapshots[~inventory_snapshots["SKU"].isin(sku_master["SKU"])]
print("Inventory records with SKU not in master:",len(inventory_skus_not_in_master))

print("Unique inventory SKUs not in master:",inventory_skus_not_in_master["SKU"].nunique())

# Checking which inventory SKUs are not present in SKU master
print(inventory_skus_not_in_master["SKU"].unique())

# Checking unmatched inventory SKUs exist in sales
inventory_skus = inventory_skus_not_in_master["SKU"].unique()

sales_extra_skus = sales[sales["SKU"].isin(inventory_skus)]
print("Unmatched inventory SKUs found in sales:",sales_extra_skus["SKU"].nunique())
print("Sales records for unmatched inventory SKUs:",len(sales_extra_skus))

# Checking Reorder Point and Safety Stock
print("Reorder Point lower than Safety Stock:",
    (inventory_snapshots["Reorder_Point"]< inventory_snapshots["Safety_Stock"]).sum())

# Checking invalid lead Time
print("Lead Time less than or equal to zero:",
    (inventory_snapshots["Lead_Time_Days"] <= 0).sum())

# Checking Sales Date range
print("Sales start date:",sales["Date"].min())
print("Sales end date:",sales["Date"].max())

# Checking Calendar Date Range
print("Calendar start date:", calendar["date"].min())
print("Calendar end date:",calendar["date"].max())

# Checking Sales and Calendar have same date range
print("Sales and Calendar date range match:",
    sales["Date"].min() == calendar["date"].min()
    and sales["Date"].max() == calendar["date"].max())

# Checking gaps in Calendar dates
calendar_date_diff = calendar["date"].sort_values().diff()

calendar_date_gaps = calendar[calendar_date_diff.notna()
    & (calendar_date_diff != pd.Timedelta(days=1))]

print("Calendar date gaps:",len(calendar_date_gaps))

# Checking duplicate SKU IDs in SKU master
print("Duplicate SKU IDs in master:",sku_master["SKU"].duplicated().sum())

# Checking all Sales Dates exist in Calendar
sales_dates_not_in_calendar = sales[~sales["Date"].isin(calendar["date"])]

print("Sales records with date not in calendar:",len(sales_dates_not_in_calendar))

# Removing Duplicate Rows
sales = sales.drop_duplicates()
sku_master = sku_master.drop_duplicates()
calendar = calendar.drop_duplicates()
inventory_snapshots = inventory_snapshots.drop_duplicates()

# Keeping only Inventory SKUs Available in SKU master
inventory_snapshots = inventory_snapshots[
    inventory_snapshots["SKU"].isin(sku_master["SKU"])]

# Checking final Shapes
print("Final Sales shape:",sales.shape)
print("Final SKU Master shape:",sku_master.shape)
print("Final Calendar shape:",calendar.shape)
print("Final Inventory shape:", inventory_snapshots.shape)

# Creating processed folder
Path("data/processed").mkdir(parents=True,exist_ok=True)

# Saving The Cleaned Datasets
sales.to_csv("data/processed/sales_cleaned.csv",index=False)

sku_master.to_csv("data/processed/sku_master_cleaned.csv",index=False)

calendar.to_csv("data/processed/calendar_cleaned.csv",index=False)

inventory_snapshots.to_csv("data/processed/inventory_cleaned.csv",index=False)

# Checking saved Files
print("Cleaned files saved successfully")

print("Sales cleaned:",sales.shape)
print("SKU Master cleaned:", sku_master.shape)
print("Calendar cleaned:",calendar.shape)
print("Inventory cleaned:",inventory_snapshots.shape)

print("Pipeline completed successfully")