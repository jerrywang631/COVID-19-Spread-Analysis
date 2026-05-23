import csv
from typing import List, Set


class Tree:
    def __init__(self, root: object, subtrees: List['Tree']) -> None:
        self._root = root
        self._subtrees = subtrees

    def get_root(self) -> object:
        return self._root

    def get_subtrees(self) -> List['Tree']:
        return self._subtrees

    def add_subtree(self, subtree: 'Tree') -> None:
        self._subtrees.append(subtree)

    def find_subtree_by_location(self, location: str) -> 'Tree':
        if isinstance(self._root, str) and self._root.lower() == location.lower():
            return self
        for subtree in self._subtrees:
            result = subtree.find_subtree_by_location(location)
            if result:
                return result
        return None

    def __str__(self) -> str:
        return f"{self._root} -> {[str(st) for st in self._subtrees]}"

    def load_data_canada(self, file_names: Set[str]) -> None:
        for file in file_names:
            if "population" in file:
                self._load_canada_population(file)
            elif "covid19" in file:
                self._load_canada_cases(file)

    def load_data_us(self, file_names: Set[str]) -> None:
        for file in file_names:
            if "population" in file:
                self._load_us_population(file)
            elif "us-counties" in file:
                self._load_us_cases(file)

    def _load_canada_cases(self, file_path: str) -> None:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                province = row['prname'].strip()
                date = row['date'].strip()
                try:
                    cases = int(row['totalcases'])
                except ValueError:
                    continue
                self._insert_data(province, date, cases)

    def _load_canada_population(self, file_path: str) -> None:
        with open(file_path, newline='', encoding='utf-8') as f:
            lines = f.readlines()

        header_line = None
        for line in lines:
            if line.strip().startswith('"Geography"'):
                header_line = line
                break

        if not header_line:
            return

        headers = [h.strip('"') for h in header_line.strip().split(',')]
        date_map = {}
        for col in headers[1:]:
            if col.startswith("Q"):
                quarter, year = col.split()
                if quarter == 'Q1':
                    date_map[col] = f"01-{year}"
                elif quarter == 'Q2':
                    date_map[col] = f"04-{year}"
                elif quarter == 'Q3':
                    date_map[col] = f"07-{year}"
                elif quarter == 'Q4':
                    date_map[col] = f"10-{year}"

        for line in lines:
            if line.strip().startswith('"Geography"') or not line.strip() or line.startswith(',"Persons"'):
                continue
            parts = [p.strip().strip('"') for p in line.strip().split(',')]
            if not parts or not parts[0]:
                continue
            province = parts[0]
            for i, raw_value in enumerate(parts[1:]):
                if i >= len(date_map):
                    break
                date_str = date_map.get(headers[i + 1])
                if not date_str or not raw_value or not raw_value.replace('.', '', 1).isdigit():
                    continue
                population = raw_value
                self._insert_population(province, date_str, population)

    def _load_us_cases(self, file_path: str) -> None:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                state = row['state'].strip()
                date = row['date'].strip()
                try:
                    cases = int(row['cases'])
                except ValueError:
                    continue
                self._insert_data(state, date, cases)

    def _load_us_population(self, file_path: str) -> None:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                state = row['NAME'].strip()
                for key in row:
                    if key.startswith('POPESTIMATE'):
                        year = key.replace('POPESTIMATE', '')
                        if not year.isdigit():
                            continue
                        date = f"07-{year}"  # 设定为7月中旬估计
                        population = row[key].strip()
                        if population and population.isdigit():
                            self._insert_population(state, date, population)

    def _insert_data(self, region: str, date: str, cases: int) -> None:
        try:
            month, year = date.split('-')[1], date.split('-')[0]
            mm_yyyy = f"{month}-{year}"
        except IndexError:
            return

        region_node = self._get_or_create_subtree(region)
        year_node = self._get_or_create_subtree(year, region_node)
        month_node = self._get_or_create_subtree(mm_yyyy, year_node)

        case_node = month_node.get_subtrees()[0] if month_node.get_subtrees() else None
        if case_node:
            case_node._root += cases
        else:
            month_node.add_subtree(Tree(cases, []))

    def _insert_population(self, region: str, date: str, population: str) -> None:
        region_node = self.find_subtree_by_location(region)
        if not region_node:
            return

        year = date.split('-')[1]
        mm_yyyy = date[0:2] + '-' + year

        for year_node in region_node.get_subtrees():
            if year_node.get_root() == year:
                for month_node in year_node.get_subtrees():
                    if month_node.get_root() == mm_yyyy:
                        if month_node.get_subtrees():
                            case_node = month_node.get_subtrees()[0]
                            if not case_node.get_subtrees():
                                case_node.add_subtree(Tree(population, []))
                        return

    def _get_or_create_subtree(self, root_value: object, parent: 'Tree' = None) -> 'Tree':
        search_list = parent.get_subtrees() if parent else self.get_subtrees()
        for subtree in search_list:
            if subtree.get_root() == root_value:
                return subtree
        new_subtree = Tree(root_value, [])
        if parent:
            parent.add_subtree(new_subtree)
        else:
            self.add_subtree(new_subtree)
        return new_subtree
