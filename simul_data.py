import pandas as pd

days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
month = []
for m in range(1, 13):
    for day in range(days_in_month[m]):
        month.append(m)


dbs = [
    pd.read_csv("./rain1.csv"),
    pd.read_csv("./rain2.csv"),
    pd.read_csv("./rain3.csv"),
]
rain_db = pd.concat(dbs)
rain_db = rain_db[["일시", "일강수량(mm)"]]
rain_db.columns = ["date", "rain"]
rain_db["month"] = rain_db["date"].str[5:7]
rain_db.pop("date")
rain_db["month"] = pd.to_numeric(rain_db["month"])
rain_db["rain"] = rain_db["rain"].fillna(0)
rain_db["monthly_avg"] = rain_db.groupby("month")["rain"].transform("mean")
rain_db = rain_db[
    (rain_db["rain"] > 0.3) & (rain_db["rain"] < rain_db["monthly_avg"] * 15)
]
rain_db.pop("monthly_avg")

usage = [
    0,
    95280.94118,
    98710.88235,
    97389.88235,
    119147.3529,
    133764,
    137055,
    139043,
    138215,
    122377.3529,
    98859.88235,
    98681.88235,
    96699.94118,
]
