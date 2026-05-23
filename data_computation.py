from data_loader import Tree
from datetime import datetime


def get_total_case_number(tree: Tree, time_start: str, time_end: str, location: str) -> int:
    """Return the total number of cases in the given location during the given time period.
    Note that time_start and time_end can be the same, which represents a specific month or year.

    >>> canada = generate_sample_tree()
    >>> get_total_case_number(canada, '01-2020', '01-2021', 'alberta')
    670
    """
    # Parse time range
    start = datetime.strptime(time_start, "%m-%Y")
    end = datetime.strptime(time_end, "%m-%Y")

    # Step 1: Find the subtree for the given location
    location_subtree = tree.find_subtree_by_location(location)
    if not location_subtree:
        return 0

    total = 0

    # Step 2: Traverse year -> month (like "01-2020") -> case node
    for year_subtree in location_subtree.get_subtrees():
        for month_subtree in year_subtree.get_subtrees():
            try:
                current = datetime.strptime(month_subtree.get_root(), "%m-%Y")
            except ValueError:
                continue  # skip if format invalid

            if start <= current <= end:
                try:
                    case_node = month_subtree.get_subtrees()[0]
                    total += int(case_node.get_root())
                except (IndexError, AttributeError, ValueError):
                    continue

    return total


def get_case_density(tree: Tree, time: str, location: str) -> float:
    """Return the case density (rounded into two decimal places) in the given at that given time.

    Note: case density is defined as total case number devided by the population.
    The time is written in MM-YYYY.
    >>> canada = generate_sample_tree()
    >>> get_case_density(canada, '01-2020', 'alberta')
    0.01
    """
    # Step 1: Validate time format (MM-YYYY)
    if len(time) != 7 or not (time[:2].isdigit() and time[2] == '-' and time[3:].isdigit()):
        raise ValueError("Invalid time format. Use 'MM-YYYY'.")

    # Step 2: Get total cases for that specific month
    total_cases = get_total_case_number(tree, time, time, location)

    # Step 3: Get population for that specific month
    total_population = get_population(tree, time, location)

    # Step 4: Compute case density
    if total_population == 0:
        return 0.0  # Avoid division by zero

    case_density = total_cases / total_population
    return round(case_density, 2)


def get_average_growth_rate(tree: Tree, time_start: str, time_end: str, location: str) -> float:
    """Return the average growth rate (rounded into two decimal places) in the given location between the given time.
    grow_rate is defined as (total case number in time_end - total case number in time_start) / time duration (in month)

    >>> canada = generate_sample_tree()
    >>> get_average_growth_rate(canada, '01-2020', '01-2021', 'alberta')
    16.67
    """
    cases_start = get_total_case_number(tree, time_start, time_start, location)
    cases_end = get_total_case_number(tree, time_end, time_end, location)

    start_date = datetime.strptime(time_start, "%m-%Y")
    end_date = datetime.strptime(time_end, "%m-%Y")
    duration = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    if duration == 0:
        return 0.0

    growth_rate = (cases_end - cases_start) / duration
    return round(growth_rate, 2)


def get_population(tree: Tree, time: str, location: str) -> int:
    """Return the number of population in the given location during the given year.

    This function is used to calculate the case density.
    The 'time' is written in MM-YYYY.

    >>> canada = generate_sample_tree()
    >>> get_population(canada, '02-2020', 'alberta')
    10005
    """
    # Step 1: Extract year
    year = time[3:]

    # Step 2: Find the subtree for the given location
    location_subtree = None
    for subtree in tree.get_subtrees():
        if subtree.get_root() == location:
            location_subtree = subtree
            break

    if not location_subtree:
        return 0  # If the location does not exist, return 0

    # Step 3: Find the year subtree that matches the year (dynamic year matching)
    for year_subtree in location_subtree.get_subtrees():
        if year_subtree.get_root() == year:  # Match the year dynamically (e.g., '2020', '2021')
            # Step 4: Look for the correct month (MM-YYYY) within this year
            for month_subtree in year_subtree.get_subtrees():
                if month_subtree.get_root() == time:  # Match the time (e.g., '02-2020')
                    # Step 5: Find the case subtree, which holds the population
                    for case_subtree in month_subtree.get_subtrees():
                        if isinstance(case_subtree.get_root(), int):  # Case number node
                            for population_subtree in case_subtree.get_subtrees():
                                if isinstance(population_subtree.get_root(), str):  # Population node
                                    return int(population_subtree.get_root())  # Return the population value

    # If no matching population was found, return 0
    return 0


def generate_sample_tree() -> Tree:
    """Generate a sample tree structure for testing."""
    canada = Tree('canada', [])
    alberta = Tree('alberta', [])

    alberta_2020 = Tree('2020', [])
    alberta_01_2020 = Tree('01-2020', [])
    alberta_02_2020 = Tree('02-2020', [])
    alberta_03_2020 = Tree("03-2020", [])

    alberta_01_2020_case = Tree(100, [])
    alberta_02_2020_case = Tree(120, [])
    alberta_03_2020_case = Tree(150, [])

    alberta_01_2020_population = Tree('10000', [])
    alberta_02_2020_population = Tree('10005', [])
    alberta_03_2020_population = Tree('10001', [])

    alberta_01_2020_case.add_subtree(alberta_01_2020_population)
    alberta_02_2020_case.add_subtree(alberta_02_2020_population)
    alberta_03_2020_case.add_subtree(alberta_03_2020_population)

    alberta_01_2020.add_subtree(alberta_01_2020_case)
    alberta_02_2020.add_subtree(alberta_02_2020_case)
    alberta_03_2020.add_subtree(alberta_03_2020_case)

    alberta_2020.add_subtree(alberta_01_2020)
    alberta_2020.add_subtree(alberta_02_2020)
    alberta_2020.add_subtree(alberta_03_2020)

    alberta_2021 = Tree('2021', [])
    alberta_01_2021 = Tree('01-2021', [])
    alberta_2021.add_subtree(alberta_01_2021)

    alberta_01_2021_case = Tree(300, [])
    alberta_01_2021_population = Tree('10006', [])
    alberta_01_2021_case.add_subtree(alberta_01_2021_population)
    alberta_01_2021.add_subtree(alberta_01_2021_case)

    alberta.add_subtree(alberta_2020)
    alberta.add_subtree(alberta_2021)
    canada.add_subtree(alberta)

    # print(canada)  # TODO 会影响doctest，但是在python console调用的时候就能直观看到这个tree
    return canada


if __name__ == '__main__':
    import doctest
    doctest.testmod()

#     import python_ta
#     python_ta.check_all(config={
#         'max-line-length': 120,
#         'max-nested-blocks': 4
#     })
