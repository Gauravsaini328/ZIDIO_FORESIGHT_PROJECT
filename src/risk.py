import pandas as pd
from pathlib import Path

# Reading processed CSV files
forecast = pd.read_csv("data/processed/sku_8_week_forecast.csv")
inventory = pd.read_csv("data/processed/inventory_cleaned.csv")
sku_master = pd.read_csv("data/processed/sku_master_cleaned.csv")


# Checking Shapes

print("Forecast shape:", forecast.shape)
print("Inventory shape:", inventory.shape)
print("SKU Master shape:", sku_master.shape)


# Checking Columns

print("Forecast columns:")
print(forecast.columns.tolist())

print("Inventory columns:")
print(inventory.columns.tolist())

print("SKU Master columns:")
print(sku_master.columns.tolist())


# Converting Required Datatypes

forecast["Week"] = pd.to_datetime(forecast["Week"])
inventory["Snapshot_Date"] = pd.to_datetime(inventory["Snapshot_Date"])


# Checking Datatypes

print("Forecast Week datatype:", forecast["Week"].dtype)
print("Inventory Snapshot Date datatype:", inventory["Snapshot_Date"].dtype)


# Checking Missing Values

print("Forecast missing values:")
print(forecast.isnull().sum())

print("Inventory missing values:")
print(inventory.isnull().sum())


# Checking Duplicate Rows

print("Forecast duplicate rows:",forecast.duplicated().sum())
print("Inventory duplicate rows:",inventory.duplicated().sum())


# Checking Duplicate SKU records in forecast

print("Duplicate SKU-Week rows:",forecast.duplicated(subset=["SKU", "Week"]).sum())

# Checking Forecast Values

print("Negative Forecast values:",(forecast["Forecast"] < 0).sum())

# Checking Inventory Values

print("Negative Current Stock:",(inventory["Current_Stock"] < 0).sum())
print("Negative On Order:",(inventory["On_Order"] < 0).sum())
print("Negative Safety Stock:",(inventory["Safety_Stock"] < 0).sum())
print( "Negative Reorder Point:",(inventory["Reorder_Point"] < 0).sum())
print("Negative Inventory Value:",(inventory["Inventory_Value"] < 0).sum())

# Checking Forecast Date Range

print("Forecast start week:",forecast["Week"].min())
print("Forecast end week:",forecast["Week"].max())

# Checking Number of SKUs

print("Forecast SKUs:",forecast["SKU"].nunique())
print("Inventory SKUs:",inventory["SKU"].nunique())

# Checking whether all forecast SKUs exist in inventory

forecast_skus_not_in_inventory = forecast[~forecast["SKU"].isin(inventory["SKU"])]

print("Forecast SKUs not in inventory:",forecast_skus_not_in_inventory["SKU"].nunique())

# Keeping only the latest inventory snapshot

latest_snapshot_date = inventory["Snapshot_Date"].max()

print("Latest inventory snapshot:",latest_snapshot_date)

inventory_latest = inventory[inventory["Snapshot_Date"]== latest_snapshot_date].copy()

print("Latest inventory shape:",inventory_latest.shape)

# Checking duplicate SKU in latest inventory

print("Duplicate latest inventory SKUs:",inventory_latest["SKU"].duplicated().sum())

# Calculating total 8-week forecast demand for each SKU

forecast_summary = (forecast.groupby("SKU", as_index=False)["Forecast"].sum())
forecast_summary = forecast_summary.rename(columns={"Forecast": "Forecast_8_Week_Demand"})

print("8-week forecast summary:")
print(forecast_summary.head())


# Calculating average weekly forecast

weekly_average = (forecast.groupby("SKU", as_index=False)["Forecast"].mean())
weekly_average = weekly_average.rename(columns={ "Forecast": "Average_Weekly_Forecast"})

# Adding average weekly forecast

forecast_summary = forecast_summary.merge(weekly_average,on="SKU",how="left")

# Calculating average daily forecast

forecast_summary["Average_Daily_Forecast"] = (forecast_summary["Forecast_8_Week_Demand"]/ 56)

# Calculating 30-day forecast demand

forecast_summary["Forecast_30_Day_Demand"] = (forecast_summary["Average_Daily_Forecast"]* 30)

# Checking forecast summary

print("Forecast summary:")
print(forecast_summary.head())

# Combining forecast with inventory

risk_data = inventory_latest.merge(forecast_summary,on="SKU",how="left")

# Filling missing forecast values with zero

risk_data[["Forecast_8_Week_Demand","Average_Weekly_Forecast","Average_Daily_Forecast","Forecast_30_Day_Demand"]] = (
    risk_data[["Forecast_8_Week_Demand","Average_Weekly_Forecast","Average_Daily_Forecast","Forecast_30_Day_Demand"]].fillna(0))

# Checking combined data

print("Risk data shape:",risk_data.shape)
print("Risk data missing values:")
print(risk_data.isnull().sum())

# Calculating available inventory

risk_data["Available_Inventory"] = (risk_data["Current_Stock"]+ risk_data["On_Order"])

# Calculating lead time demand

risk_data["Lead_Time_Demand"] = (risk_data["Average_Daily_Forecast"] * risk_data["Lead_Time_Days"])

# Calculating required inventory

risk_data["Required_Inventory"] = (risk_data["Lead_Time_Demand"] + risk_data["Safety_Stock"])

# Calculating stockout gap

risk_data["Stockout_Gap"] = (risk_data["Required_Inventory"] - risk_data["Available_Inventory"])

# Calculating stockout risk percentage

risk_data["Stockout_Risk_Score"] = ((risk_data["Stockout_Gap"] / risk_data["Required_Inventory"]) * 100)

# Handling cases where required inventory is zero

risk_data["Stockout_Risk_Score"] = (risk_data["Stockout_Risk_Score"].fillna(0))

# Limiting stockout score between 0 and 100

risk_data["Stockout_Risk_Score"] = (risk_data["Stockout_Risk_Score"].clip(lower=0, upper=100))

# Creating stockout risk level

risk_data["Stockout_Risk"] = "Low"
risk_data.loc[risk_data["Stockout_Risk_Score"] >= 30,"Stockout_Risk"] = "Medium"
risk_data.loc[risk_data["Stockout_Risk_Score"] >= 60,"Stockout_Risk"] = "High"

# Calculating overstock ratio

risk_data["Overstock_Ratio"] = (risk_data["Current_Stock"]/ risk_data["Forecast_30_Day_Demand"])

# Handling zero forecast demand

risk_data.loc[(risk_data["Forecast_30_Day_Demand"] == 0) &(risk_data["Current_Stock"] > 0),"Overstock_Ratio"] = 999
# Creating overstock risk

risk_data["Overstock_Risk"] = "Low"
risk_data.loc[risk_data["Overstock_Ratio"] > 1,"Overstock_Risk"] = "Medium"
risk_data.loc[risk_data["Overstock_Ratio"] >= 2,"Overstock_Risk"] = "High"

# Creating overstock risk score

risk_data["Overstock_Risk_Score"] = ((risk_data["Overstock_Ratio"] - 1)* 100)

# Limiting overstock score

risk_data["Overstock_Risk_Score"] = (risk_data["Overstock_Risk_Score"].clip(lower=0, upper=100))

# Creating overall risk score

risk_data["Overall_Risk_Score"] = (risk_data["Stockout_Risk_Score"]+ risk_data["Overstock_Risk_Score"]) / 2

# Creating decision grid

risk_data["Recommended_Action"] = "Healthy"

# High stockout + low overstock

risk_data.loc[((risk_data["Stockout_Risk"] == "High") &
            (risk_data["Overstock_Risk"] == "Low")),"Recommended_Action"] = "Reorder Now"


# High overstock + low stockout

risk_data.loc[((risk_data["Overstock_Risk"] == "High") &
            (risk_data["Stockout_Risk"] == "Low")),"Recommended_Action"] = "Markdown / Clear"

# High stockout + high/medium overstock

risk_data.loc[((risk_data["Stockout_Risk"] == "High") &
            (risk_data["Overstock_Risk"].isin(["Medium", "High"]))),"Recommended_Action"] = "Watch / Volatile"

# High overstock + medium/high stockout

risk_data.loc[((risk_data["Overstock_Risk"] == "High") &
            (risk_data["Stockout_Risk"].isin(["Medium", "High"]))),"Recommended_Action"] = "Watch / Volatile"


# Medium stockout

risk_data.loc[risk_data["Stockout_Risk"] == "Medium","Recommended_Action"] = "Watch / Volatile"

# Medium overstock

risk_data.loc[risk_data["Overstock_Risk"] == "Medium","Recommended_Action"] = "Watch / Volatile"

# Calculating shortage units

risk_data["Shortage_Units"] = (risk_data["Stockout_Gap"].clip(lower=0))

# Calculating unit value

risk_data["Unit_Value"] = (risk_data["Inventory_Value"]/ risk_data["Current_Stock"])

# Handling zero stock

risk_data["Unit_Value"] = (risk_data["Unit_Value"].replace([float("inf"), -float("inf")],0).fillna(0))

# Calculating stockout value at stake

risk_data["Stockout_Value_at_Stake"] = (risk_data["Shortage_Units"]* risk_data["Unit_Value"])

# Calculating target inventory for 30 days

risk_data["Target_Inventory_30_Days"] = (risk_data["Forecast_30_Day_Demand"]* 2)

# Calculating excess inventory

risk_data["Excess_Inventory_Units"] = (risk_data["Current_Stock"]- risk_data["Target_Inventory_30_Days"]).clip(lower=0)

# Calculating overstock value at stake

risk_data["Overstock_Value_at_Stake"] = (risk_data["Excess_Inventory_Units"]* risk_data["Unit_Value"])

# Calculating total value at stake

risk_data["Total_Value_at_Stake"] = (risk_data["Stockout_Value_at_Stake"]+ risk_data["Overstock_Value_at_Stake"])

# Creating priority

risk_data["Priority"] = "Low"
risk_data.loc[risk_data["Recommended_Action"].isin(["Reorder Now", "Markdown / Clear"]),"Priority"] = "High"
risk_data.loc[risk_data["Recommended_Action"]== "Watch / Volatile","Priority"] = "Medium"

# Rounding numerical columns

numeric_columns = ["Forecast_8_Week_Demand","Average_Weekly_Forecast","Average_Daily_Forecast","Lead_Time_Demand","Forecast_30_Day_Demand","Available_Inventory","Stockout_Gap",
    "Required_Inventory","Stockout_Risk_Score","Overstock_Ratio","Overstock_Risk_Score","Overall_Risk_Score","Shortage_Units","Unit_Value",
    "Stockout_Value_at_Stake","Target_Inventory_30_Days","Excess_Inventory_Units","Overstock_Value_at_Stake","Total_Value_at_Stake"]

for column in numeric_columns:
    risk_data[column] = risk_data[column].round(2)


# Selecting final columns

risk_output = risk_data[["SKU","Snapshot_Date","Current_Stock","On_Order","Available_Inventory","Lead_Time_Days","Safety_Stock","Reorder_Point",
        "Forecast_8_Week_Demand","Average_Weekly_Forecast","Average_Daily_Forecast","Lead_Time_Demand","Forecast_30_Day_Demand",
        "Stockout_Gap","Stockout_Risk_Score","Stockout_Risk",
        "Overstock_Ratio","Overstock_Risk_Score","Overstock_Risk","Overall_Risk_Score",
        "Recommended_Action","Priority",
        "Shortage_Units","Unit_Value","Stockout_Value_at_Stake",
        "Target_Inventory_30_Days","Excess_Inventory_Units","Overstock_Value_at_Stake",
        "Total_Value_at_Stake"]].copy()

# Sorting by priority and value at stake

priority_order = {"High": 1,"Medium": 2,"Low": 3}

risk_output["Priority_Order"] = (risk_output["Priority"].map(priority_order))
risk_output = (risk_output.sort_values(["Priority_Order","Total_Value_at_Stake"],ascending=[True, False]).drop(columns=["Priority_Order"]))

# Creating processed folder if required

Path("data/processed").mkdir(parents=True,exist_ok=True)

# Saving risk scoring output

risk_output.to_csv("data/processed/sku_risk_scoring.csv",index=False)

# Final Checks

print("Final risk output shape:", risk_output.shape)
print("High stockout risk:",(risk_output["Stockout_Risk"] == "High").sum())
print("Medium stockout risk:",(risk_output["Stockout_Risk"] == "Medium").sum())
print("High overstock risk:",(risk_output["Overstock_Risk"] == "High").sum())
print("Medium overstock risk:",(risk_output["Overstock_Risk"] == "Medium").sum())
print("Recommended actions:")
print(risk_output["Recommended_Action"].value_counts())
print("Total Stockout Value at Stake:",risk_output["Stockout_Value_at_Stake"].sum())
print("Total Overstock Value at Stake:",risk_output["Overstock_Value_at_Stake"].sum())
print("Total Value at Stake:",risk_output["Total_Value_at_Stake"].sum())
print("Risk scoring completed successfully")