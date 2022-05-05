from prettytable import PrettyTable, ALL
import math

from structure import *


class Grid:
    def __init__(self, raw_rows: list[str]):
        self.square_side = int(len(raw_rows) ** 0.5)
        self.numbers = set(range(1, len(raw_rows) + 1))

        cells = []
        i = 0
        for row_id, raw_row in enumerate(raw_rows):
            for column_id, value in enumerate(list(raw_row)):
                square_x = math.ceil((column_id + 1) / self.square_side) - 1
                square_y = math.ceil((row_id + 1) / self.square_side) - 1
                square_id = square_x + square_y * self.square_side

                cell = Cell(
                    value=int(value),
                    id=i,
                    row_id=row_id,
                    column_id=column_id,
                    square_id=square_id,
                    possible_values=self.numbers
                )
                cells.append(cell)
                i += 1

        self.rows: list[CellGroup] = []
        self.columns: list[CellGroup] = []
        self.squares: list[CellGroup] = []
        for i in range(0, len(raw_rows)):
            self.rows.append(CellGroup([], i))
            self.columns.append(CellGroup([], i))
            self.squares.append(CellGroup([], i))

        for cell in cells:
            self.rows[cell.row_id].update_cell(cell)
            self.columns[cell.column_id].update_cell(cell)
            self.squares[cell.square_id].update_cell(cell)

    def __eq__(self, other):
        return (self.rows == other.rows) and (self.columns == other.columns) and (self.squares == other.squares)

    def is_filled(self) -> bool:
        for row in self.rows:
            for cell in row.cells:
                if not cell.value:
                    return False
        return True

    def is_correct(self) -> bool:
        for check in (self.rows, self.columns, self.squares):
            for list_ in check:
                if not list_.is_correct():
                    return False

        return True

    def update_cell(self, cell: Cell):
        self.rows[cell.row_id].update_cell(cell)
        self.columns[cell.column_id].update_cell(cell)
        self.squares[cell.square_id].update_cell(cell)

    def print(self, display_ambiguous: bool = False, highlight: int = None):

        pretty_squares = []
        for i, square in enumerate(self.squares):
            square_rows = []

            for i2, cell in enumerate(square.cells):
                value = str(cell.value)

                if cell.id == highlight:
                    value = f'({value})'

                if display_ambiguous and value == '0':
                    value = str(cell.possible_values).replace(' ', '')

                if i2 % self.square_side != 0:
                    square_rows[-1] += f" {value}"
                else:
                    square_rows.append(value)

            pretty_square = ('\n'.join(square_rows)).replace('0', ' ')
            pretty_squares.append(pretty_square)

        square_grid = list([pretty_squares[i:i + self.square_side] for i in range(0, len(pretty_squares), self.square_side)])

        tab = PrettyTable()
        tab.header = False
        tab.add_rows(square_grid)
        tab.hrules = ALL
        tab.vrules = ALL
        print(tab)

    def remove_wrong_possible_values(self):
        for check in (self.rows, self.columns, self.squares):
            for list_ in check:
                values = list_.get_values()

                for cell in list_.cells:
                    if cell.value == 0:
                        cell.possible_values = cell.possible_values - set(values)

                        if len(cell.possible_values) == 1:
                            cell.value = list(cell.possible_values)[0]

                        self.update_cell(cell)

    def pick_values(self):
        for square in self.squares:
            self.remove_wrong_possible_values()

            possible_values = []
            for cell in square.cells:
                if not cell.value:
                    possible_values += list(cell.possible_values)

            if len(possible_values) <= 1:
                continue

            lone_pos_values = set(filter(lambda _: possible_values.count(_) == 1, possible_values))
            for cell in square.cells:

                if cell.value:
                    continue

                for value in cell.possible_values:
                    if value in lone_pos_values:
                        cell.value = value
                        self.update_cell(cell)
                        break

    def remove_conflicting_possible_values(self):
        for num in self.numbers:
            for square_id, square in enumerate(self.squares):
                all_missing_values = self.numbers - set(map(lambda cell: cell.value, square.cells))
                if num not in all_missing_values:
                    continue

                matching_cells = list(
                    filter(
                        lambda cell: num in cell.possible_values if not cell.value else False,
                        square.cells
                    )
                )

                matching_rows = []
                matching_columns = []

                for cell in matching_cells:
                    matching_rows.append(cell.row_id)
                    matching_columns.append(cell.column_id)

                def update_grid(line):
                    for cell in line:
                        if cell.value:
                            continue

                        if cell.square_id != square_id:
                            cell.possible_values -= {num}

                        self.update_cell(cell)

                if len(set(matching_rows)) == 1:
                    update_grid(self.rows[matching_rows[0]].cells)

                if len(set(matching_columns)) == 1:
                    update_grid(self.columns[matching_columns[0]].cells)

    def get_first_ambiguous_value(self):
        for row in self.rows:
            for cell in row.cells:
                if not cell.value:
                    return cell
