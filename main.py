from data_loader import Tree
from data_visualization import (
    generate_map_of_cases_canada, generate_map_of_cases_us,
    generate_heat_map_of_case_density_canada, generate_heat_map_of_case_density_us,
    generate_line_chart_of_growth_rate_canada, generate_line_chart_of_growth_rate_us
)

file_names_canada = {'population_canada.csv', 'covid19_canada.csv'}
file_names_us = {'population_us.csv', 'us-counties-2020.csv', 'us-counties-2021.csv', 'us-counties-2022.csv'}

canada_tree = Tree(None, [])
us_tree = Tree(None, [])

canada_tree.load_data_canada(file_names_canada)
us_tree.load_data_us(file_names_us)

print("Welcome to the COVID-19 Data Analysis Program!")
while True:
    print("\nPlease select an option:")
    print("1. Calculate total case number")
    print("2. Calculate case density")
    print("3. Calculate pandemic growth rate")
    print("4. Exit")

    choice = input("Enter the number for your choice (1-4): ").strip()
    if choice not in {"1", "2", "3", "4"}:
        print("Invalid choice, please enter a number from 1 to 4.")
        continue

    country = input("Enter the country (Canada or US): ").strip().lower()
    if country not in {'canada', 'us'}:
        print("Invalid country input. Please enter 'Canada' or 'US'.")
        continue

    if choice == '1':
        year = input("Enter the year of data you want to visualize (from 2020-2022): ").strip()
        if year not in {"2020", "2021", "2022"}:
            print("Invalid year. Please enter 2020, 2021, or 2022.")
            continue

        if country == 'canada':
            generate_map_of_cases_canada(canada_tree, year)
        else:
            generate_map_of_cases_us(us_tree, year)

    elif choice == '2':
        time = input("Enter the month you want to visualize in the form of MM-YYYY (from 01-2020 to 12-2022): ").strip()
        if not (len(time) == 7 and time[:2].isdigit() and time[2] == '-' and time[3:].isdigit()):
            print("Invalid time format. Please enter in MM-YYYY format.")
            continue

        if country == 'canada':
            generate_heat_map_of_case_density_canada(canada_tree, time)
        else:
            generate_heat_map_of_case_density_us(us_tree, time)

    elif choice == '3':
        region = input("Enter the province/state/region in the country: ").strip()
        time_start = input("Enter the start time in the form of MM-YYYY (from 01-2020 to 12-2022): ").strip()
        time_end = input("Enter the end time in the form of MM-YYYY (from 01-2020 to 12-2022): ").strip()

        if not (len(time_start) == 7 and time_start[:2].isdigit() and time_start[2] == '-'
                and time_start[3:].isdigit()):
            print("Invalid start time format. Please enter in MM-YYYY format.")
            continue

        if not (len(time_end) == 7 and time_end[:2].isdigit() and time_end[2] == '-' and time_end[3:].isdigit()):
            print("Invalid end time format. Please enter in MM-YYYY format.")
            continue

        if country == 'canada':
            generate_line_chart_of_growth_rate_canada(canada_tree, time_start, time_end, region)
        else:
            generate_line_chart_of_growth_rate_us(us_tree, time_start, time_end, region)

    elif choice == '4':
        print("Thank you for using the COVID-19 Data Analysis Program. Goodbye!")
        break
