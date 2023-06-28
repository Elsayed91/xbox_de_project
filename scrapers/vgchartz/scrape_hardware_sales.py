"""
This module retrieves and processes hardware sales data from the https://www.vgchartz.com
website, and then generates a pandas DataFrame containing the processed data. The module
has four functions that perform different tasks.

get_sales_data(url: str) -> dict: This function takes a URL as input and retrieves sales
data from the specified URL. The function fetches the data by making a GET request to the
URL, searches the response text for the relevant data using a regular expression, and then
uses the js2py library to evaluate the JavaScript code to convert the data to a dictionary
object. The function then returns the sales data as a dictionary.

get_sales_dataframe(data: dict, consoles: list[str] = None, start_date: str = None,
end_date: str = None) -> pd.DataFrame: This function takes the sales data (as a
dictionary) and converts it to a pandas DataFrame. The function creates the DataFrame with
the specified column order and then iterates over the sales data to add rows to the
DataFrame. The function also filters the data by console and date, based on the values
provided for the 'consoles', 'start_date', and 'end_date' parameters.

calculate_other_sales(df: pd.DataFrame) -> pd.DataFrame: This function calculates the
sales for the 'Others' region by subtracting the sales from the 'Europe', 'Japan' and
'USA' regions from the sales in the 'Global' region. The function takes a pandas DataFrame
as input, groups the data by console, date, and region, calculates the sales for the
'Others' region, and then returns the processed data as a DataFrame.

main(regions: list[str], consoles: list[str], start_date: Optional[str] = None, end_date:
Optional[str] = None) -> pd.DataFrame: This function ties all the other functions together
and retrieves and processes the hardware sales data for the specified regions and
consoles. The function takes the 'regions', 'consoles', 'start_date', and 'end_date'
parameters as inputs, and returns a pandas DataFrame containing the processed data, with
columns for 'console', 'date', 'sales', and 'region'.
"""
import ast
import os
import re
from typing import Optional

import js2py
import pandas as pd
import requests


def get_sales_data(url: str) -> dict:
    """
    Fetches sales data from a given URL and returns it as a dictionary.

    Args:
        url (str): The URL to fetch the data from.

    Returns:
        dict: A dictionary containing the sales data.
    """
    data = re.search(
        r"StockChart\(({.*?})\);", requests.get(url).text, flags=re.S
    ).group(1)
    data = js2py.eval_js("data = " + data + ";")
    return ast.literal_eval(str(data))


def get_sales_dataframe(
    data: dict, consoles: list[str] = None, start_date: str = None, end_date: str = None
) -> pd.DataFrame:
    """
    Converts sales data to a Pandas DataFrame and filters by console and date.

    Args:
        data (dict): The sales data to convert.
        consoles (list): List of console names to filter by.
        start_date (str): Start date for the filter in 'yyyy-mm-dd' format.
        end_date (str): End date for the filter in 'yyyy-mm-dd' format.

    Returns:
        pd.DataFrame: A DataFrame containing the filtered sales data.
    """
    # Create the DataFrame with the specified column order
    sales_data = []
    for series in data["series"]:
        sales_data.append({"console": series["name"], "sales": series["data"]})

    sales_df = pd.DataFrame(columns=["console", "date", "sales"])
    for data in sales_data:
        console = data["console"]
        if consoles is not None and console not in consoles:
            continue
        for point in data["sales"]:
            date = pd.to_datetime(point["x"], unit="ms")
            if start_date is not None and date < pd.to_datetime(start_date):
                continue
            if end_date is not None and date >= pd.to_datetime(end_date):
                continue
            sales = point["y"]
            data_dict = {"console": console, "date": date, "sales": sales}
            sales_df = pd.concat(
                [sales_df, pd.DataFrame([data_dict])], ignore_index=True
            )

    return sales_df


def calculate_other_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the sales for the 'Others' region by subtracting the sales from the
    'Europe', 'Japan' and 'USA' regions from the sales in the 'Global' region.

    Args:
        df: A pandas DataFrame with columns 'console', 'date', 'sales', and 'region'.

    Returns:
        pd.DataFrame: A DataFrame with columns 'console', 'date', 'region' and 'sales',
        where the sales for the 'Others' region have been calculated.
    """
    df_other = (
        df.groupby(["console", "date", "region"])
        .sales.sum()
        .reset_index()
        .pivot_table(
            index=["console", "date"], columns="region", values="sales", fill_value=0
        )
        .reset_index()
    )

    df_other["Others"] = df_other["Global"] - df_other[["Europe", "Japan", "USA"]].sum(
        axis=1
    )

    df_final = df_other.melt(
        id_vars=["console", "date"], var_name="region", value_name="sales"
    )
    return df_final


def main(
    regions: list[str],
    consoles: list[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> pd.DataFrame:
    """
    Retrieves and processes hardware sales data for the specified regions and consoles.

    Args:
        regions (list[str]): A list of regions to retrieve data for. Valid regions are
        "Global", "USA", "Europe", and "Japan".
        consoles (list[str]): A list of console names to retrieve data for.
        start_date (str, optional): The start date for the data in the format
        "YYYY-MM-DD".
        end_date (str, optional): The end date for the data in the format "YYYY-MM-DD".
    Returns:
        pd.DataFrame: A DataFrame containing the processed hardware sales data, with
        columns for "console", "date", "sales", and "region".
    """
    df = pd.DataFrame(columns=["console", "date", "sales", "region"])
    for region in regions:
        url = f"https://www.vgchartz.com/tools/hw_date.php?reg={region}&ending=Weekly"
        sales_data = get_sales_data(url)
        sales_df = get_sales_dataframe(
            sales_data, consoles, start_date=start_date, end_date=end_date
        )
        sales_df["region"] = region
        df = pd.concat([df, sales_df], ignore_index=True, sort=False)
    df = calculate_other_sales(df)
    return df


def update_console_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Update the content of the 'Console' column in the DataFrame.

    Args:
        df: A pandas DataFrame.

    Returns:
        A pandas DataFrame with updated 'Console' column values.
    """
    console_mapping = {
        "XS": "Xbox Series X",
        "XOne": "Xbox One",
        "X360": "Xbox 360",
    }
    df["console"] = df["console"].replace(console_mapping)
    return df


if __name__ == "__main__":
    consoles = ["XS", "XOne", "X360"]
    regions = ["USA", "Europe", "Japan", "Global"]
    local_path = os.getenv("local_path")
    df = main(regions, consoles)
    df = update_console_names(df)
    df.to_parquet(f"{local_path}vgc_hw_sales.parquet")
