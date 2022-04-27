import math
import copy
from prettytable import PrettyTable, ALL


class SudokuSolver:
    def __init__(self):
        with open('sudoku_input.txt', 'r+') as f:
            sudoku_input = f.read()

        rows = sudoku_input.split('\n')

        self.grid = []
        self.numbers = set(range(1, len(rows) + 1))

        for row in rows:
            self.grid.append([int(value) for value in row])

        self.square_side = int(len(self.grid) ** 0.5)

        n = 0
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                square_x = math.ceil((x + 1) / self.square_side) - 1
                square_y = math.ceil((y + 1) / self.square_side) - 1

                row[x] = {
                    'value': cell,
                    'id': n,
                    'column': x,
                    'row': y,
                    'square_id': square_x + square_y * self.square_side
                }

                if cell == 0:
                    row[x]['possible_values'] = self.numbers

                n += 1

        print('INPUT:')
        self.print_sudoku()

        self.solve()

    def solve(self):
        runs = 1
        guesses = 0
        last_guess = {
            'cell': {'id': 0},
            'value': 0
        }
        while True:
            while True:
                grid_before = copy.deepcopy(self.grid)

                self.remove_wrong_possible_values()
                self.pick_lone_possible_values()
                self.remove_conflicting_possible_values()

                if grid_before == self.grid:
                    break

                print(f'\nRun #{runs}')
                self.print_sudoku()

                runs += 1

            if not self.is_correct():
                if guesses == 0:
                    print('\n\nFAILED! Given sudoku is not solvable!')
                    self.print_sudoku()
                    return

                self.grid = grid_memory
                last_cell = last_guess['cell']
                cell = self.grid[last_cell['row']][last_cell['column']]
                cell['possible_values'] -= {last_guess['value']}
                self.grid[cell['row']][cell['column']] = cell
                print(f'\nGuess #{guesses} was wrong')

            if self.is_correct():
                if self.is_completed():
                    print(f'\n\nSUCCESS! Completed in {runs - 1} run(s) and {guesses} guess(es)')
                    self.print_sudoku()
                    return

                guesses += 1
                print(f'\n\n\nGuess #{guesses}')
                grid_memory = copy.deepcopy(self.grid)

                ambiguous_cells = []
                for row in self.grid:
                    for cell in row:
                        if cell['value'] == 0:
                            ambiguous_cells.append(cell)

                cell = list(filter(
                    lambda cell: (cell['id'] > last_guess['cell']['id']) or (
                        len(list(filter(lambda _: _ > last_guess['value'], cell['possible_values']))) > 0
                    ),
                    ambiguous_cells
                ))[0]

                if cell != last_guess['cell']:
                    last_guess['value'] = 0

                try:
                    new_cell_value = min(cell['possible_values'])
                except ValueError:
                    return print('FAILED! Couldn\'t solve this sudoku')
                cell['value'] = new_cell_value
                self.grid[cell['row']][cell['column']] = cell

                last_guess['cell'] = cell
                last_guess['value'] = new_cell_value
                print(f'Checking if cell #{cell["id"]+1} could be {new_cell_value}')

    def print_sudoku(self, *, display_ambiguous=False):
        squares = self.generate_checks()[2]
        for i, square in enumerate(squares):
            square_rows = []

            for i2, cell in enumerate(square):
                value = str(cell['value'])
                if display_ambiguous and value == '0':
                    value = str(cell['possible_values']).replace(' ', '')

                if i2 % self.square_side != 0:
                    square_rows[-1] += f" {value}"
                else:
                    square_rows.append(value)

            pretty_square = ('\n'.join(square_rows)).replace('0', ' ')
            squares[i] = pretty_square

        square_grid = list([squares[i:i + self.square_side] for i in range(0, len(squares), self.square_side)])

        tab = PrettyTable()
        tab.header = False
        tab.add_rows(square_grid)
        tab.hrules = ALL
        tab.vrules = ALL
        print(tab)

    def generate_checks(self):
        rows = self.grid

        columns = []
        squares = []
        for _ in self.grid:
            columns.append([])
            squares.append([])

        for y, row in enumerate(rows):
            square_y = math.ceil((y + 1) / self.square_side) - 1

            for x, cell in enumerate(row):
                columns[x].append(cell)

                square_x = math.ceil((x + 1) / self.square_side) - 1
                squares[square_x + square_y * self.square_side].append(cell)

        return rows, columns, squares

    def remove_wrong_possible_values(self):
        for i in range(0, 3):
            check = self.generate_checks()[i]
            for line in check:
                values = list(
                    filter(lambda cell: cell != 0,
                           map(lambda cell: cell['value'], line)
                           )
                )

                for cell in line:
                    if cell['value'] == 0:
                        cell['possible_values'] = cell['possible_values'] - set(values)

                        if len(cell['possible_values']) == 1:
                            cell['value'] = list(cell['possible_values'])[0]

                        self.grid[cell['row']][cell['column']] = cell

    def pick_lone_possible_values(self):
        for line in self.generate_checks()[2]:
            self.remove_wrong_possible_values()

            possible_values = []
            cell_count = 0
            for cell in line:
                if cell['value'] == 0:
                    cell_count += 1
                    possible_values += list(cell['possible_values'])

            if cell_count <= 1:
                continue

            lone_pos_values = set(filter(lambda _: possible_values.count(_) == 1, possible_values))
            for cell in line:

                if cell['value'] != 0:
                    continue

                for value in cell['possible_values']:

                    if value in lone_pos_values:
                        cell['value'] = value

                        self.grid[cell['row']][cell['column']] = cell
                        break

    def remove_conflicting_possible_values(self):
        for num in self.numbers:
            rows, columns, squares = self.generate_checks()
            for square_id, square in enumerate(squares):
                all_missing_values = self.numbers - set(map(lambda cell: cell['value'], square))
                if num not in all_missing_values:
                    continue

                matching_cells = list(filter(lambda cell: num in cell['possible_values'] if cell['value'] == 0 else False, square))

                matching_rows = []
                matching_columns = []

                for cell in matching_cells:
                    matching_rows.append(cell['row'])
                    matching_columns.append(cell['column'])

                def update_grid(line):
                    for cell in line:
                        if cell['value'] != 0:
                            continue

                        if cell['square_id'] != square_id:
                            cell['possible_values'] -= {num}

                        self.grid[cell['row']][cell['column']] = cell

                if len(set(matching_rows)) == 1:
                    update_grid(rows[matching_rows[0]])
                if len(set(matching_columns)) == 1:
                    update_grid(columns[matching_columns[0]])

    def is_correct(self):
        checks = self.generate_checks()
        for check in checks:
            for line in check:
                values = list(filter(lambda _: _ != 0, map(lambda cell: cell['value'], line)))
                if len(set(values)) != len(values):
                    return False

        return True

    def is_completed(self):
        for row in self.grid:
            for cell in row:
                if cell['value'] == 0:
                    return False

        return True


SudokuSolver()
