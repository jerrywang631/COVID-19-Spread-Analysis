import pandas as pd
import plotly.express as px
import urllib.request
import json
from data_loader import Tree
from data_computation import (get_total_case_number, get_population, get_case_density, get_average_growth_rate
                              , generate_sample_tree)
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from data_computation import get_total_case_number, get_average_growth_rate
canada_provinces = {
    "Alberta": "AB", "British Columbia": "BC", "Manitoba": "MB", "New Brunswick": "NB",
    "Newfoundland and Labrador": "NL", "Nova Scotia": "NS", "Northwest Territories": "NT",
    "Nunavut": "NU", "Ontario": "ON", "Prince Edward Island": "PE", "Quebec": "QC",
    "Saskatchewan": "SK", "Yukon": "YT"
}

us_states = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}


def generate_map_of_cases_canada(tree: Tree, year: str) -> None:
    data = {"Province": [], "Cases": [], "Code": []}
    for province, code in canada_provinces.items():
        cases = get_total_case_number(tree, f"01-{year}", f"12-{year}", province)
        data["Province"].append(province)
        data["Cases"].append(cases)
        data["Code"].append(code)

    df = pd.DataFrame(data)
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/canada.geojson"
    ) as response:
        geojson = json.load(response)

    fig = px.choropleth(df,
                        geojson=geojson,
                        locations="Province",
                        featureidkey="properties.name",
                        color="Cases",
                        hover_name="Province",
                        color_continuous_scale="Reds",
                        title=f"🇨🇦 COVID-19 Cases in Canada ({year})")
    fig.update_geos(fitbounds="locations", visible=False)
    fig.show()


def generate_map_of_cases_us(tree: Tree, year: str) -> None:
    data = {"State": [], "Cases": [], "Code": []}
    for state, code in us_states.items():
        cases = get_total_case_number(tree, f"01-{year}", f"12-{year}", state)
        data["State"].append(state)
        data["Cases"].append(cases)
        data["Code"].append(code)

    df = pd.DataFrame(data)
    fig = px.choropleth(df,
                        locations="Code",
                        locationmode="USA-states",
                        color="Cases",
                        hover_name="State",
                        color_continuous_scale="Reds",
                        title=f"🇺🇸 COVID-19 Cases in USA ({year})")
    fig.update_geos(scope="usa", showcoastlines=True, coastlinecolor="Black")
    fig.show()


def generate_heat_map_of_case_density_canada(tree: Tree, time: str) -> None:
    data = {"Province": [], "Cases": [], "Population": [], "Density": []}
    for province in canada_provinces:
        cases = get_total_case_number(tree, time, time, province)
        population = get_population(tree, time, province)
        density = get_case_density(tree, time, province)
        data["Province"].append(province)
        data["Cases"].append(cases)
        data["Population"].append(population)
        data["Density"].append(density)

    df = pd.DataFrame(data)
    with urllib.request.urlopen("https://raw.githubusercontent.com/codeforgermany/"
                                "click_that_hood/main/public/data/canada.geojson") as response:
        geojson = json.load(response)

    fig = px.choropleth(df,
                        geojson=geojson,
                        locations="Province",
                        featureidkey="properties.name",
                        color="Density",
                        hover_name="Province",
                        hover_data=["Cases", "Population"],
                        color_continuous_scale="Reds",
                        title=f"🇨🇦 COVID-19 Case Density in Canada ({time})")
    fig.update_geos(fitbounds="locations", visible=False)
    fig.show()


def generate_heat_map_of_case_density_us(tree: Tree, time: str) -> None:
    data = {"State": [], "Cases": [], "Population": [], "Density": [], "Code": []}
    for state, code in us_states.items():
        cases = get_total_case_number(tree, time, time, state)
        population = get_population(tree, time, state)
        density = get_case_density(tree, time, state)
        data["State"].append(state)
        data["Cases"].append(cases)
        data["Population"].append(population)
        data["Density"].append(density)
        data["Code"].append(code)

    df = pd.DataFrame(data)
    fig = px.choropleth(df,
                        locations="Code",
                        locationmode="USA-states",
                        color="Density",
                        hover_name="State",
                        hover_data=["Cases", "Population"],
                        color_continuous_scale="Reds",
                        title=f"🇺🇸 COVID-19 Case Density in USA ({time})")
    fig.update_geos(scope="usa", showcoastlines=True, coastlinecolor="Black")
    fig.show()


def generate_line_chart_of_growth_rate_canada(tree, time_start: str, time_end: str, region: str) -> None:
    """
    Generate the line chart of growth rate during the given time period in the given region in Canada.
    This chart also shows the average growth rate between time_start and time_end.

    The vertical axis is the number of cases, and the horizontal axis is time.
    Each month from time_start to time_end is shown with a point and connected as a line.

    Note that the input 'tree' is the tree that stores all data about Canada.
    The time_start and the time_end are written in MM-YYYY.
    """
    start = datetime.strptime(time_start, "%m-%Y")
    end = datetime.strptime(time_end, "%m-%Y")

    dates = []
    case_numbers = []
    current = start
    while current <= end:
        date_str = current.strftime("%m-%Y")
        dates.append(date_str)

        monthly_case = get_total_case_number(tree, date_str, date_str, region)
        case_numbers.append(monthly_case)

        current += relativedelta(months=1)

    avg_growth = get_average_growth_rate(tree, time_start, time_end, region)

    plt.figure(figsize=(10, 6))
    plt.plot(dates, case_numbers, marker='o', linestyle='-', label='Monthly Cases')
    plt.title(f'COVID-19 Case Growth in {region.capitalize()} ({time_start} to {time_end})')
    plt.xlabel('Month-Year')
    plt.ylabel('Number of Cases')
    plt.xticks(rotation=45)
    plt.grid(True)

    avg_line_y = case_numbers[0] + avg_growth * len(case_numbers)
    plt.axhline(y=avg_line_y, color='red', linestyle='--', label=f'Estimated Avg Growth: {avg_growth} cases/month')

    plt.legend()
    plt.tight_layout()
    plt.legend()
    plt.tight_layout()

    filename = f"{region}_{time_start}_to_{time_end}_growth.png".replace(" ", "_")
    plt.savefig(filename)
    print(f"📊 图像已保存为 {filename}")

    plt.show()


def generate_line_chart_of_growth_rate_us(tree, time_start: str, time_end: str, state: str) -> None:

    start = datetime.strptime(time_start, "%m-%Y")
    end = datetime.strptime(time_end, "%m-%Y")

    dates = []
    case_numbers = []
    current = start
    while current <= end:
        date_str = current.strftime("%m-%Y")
        dates.append(date_str)

        monthly_case = get_total_case_number(tree, date_str, date_str, state)
        case_numbers.append(monthly_case)

        current += relativedelta(months=1)

    avg_growth = get_average_growth_rate(tree, time_start, time_end, state)

    plt.figure(figsize=(10, 6))
    plt.plot(dates, case_numbers, marker='o', linestyle='-', label='Monthly Cases')
    plt.title(f'COVID-19 Case Growth in {state.title()} ({time_start} to {time_end})')
    plt.xlabel('Month-Year')
    plt.ylabel('Number of Cases')
    plt.xticks(rotation=45)
    plt.grid(True)

    avg_line_y = case_numbers[0] + avg_growth * len(case_numbers)
    plt.axhline(y=avg_line_y, color='red', linestyle='--',
                label=f'Estimated Avg Growth: {avg_growth} cases/month')

    plt.legend()
    plt.tight_layout()
    plt.legend()
    plt.tight_layout()

    filename = f"{state}_{time_start}_to_{time_end}_growth.png".replace(" ", "_")
    plt.savefig(filename)
    print(f"📊 图像已保存为 {filename}")

    plt.show()
