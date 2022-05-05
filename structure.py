from dataclasses import dataclass


@dataclass
class Cell:
    value: int
    id: int
    row_id: int
    column_id: int
    square_id: int
    possible_values: set[int]


@dataclass
class CellGroup:
    cells: list[Cell]
    id: int

    def is_correct(self) -> bool:
        values = self.get_values()
        if len(values) != len(set(values)):
            return False
        return True

    def update_cell(self, new_cell: Cell):
        for i, cell in enumerate(self.cells):
            if cell.id == new_cell.id:
                self.cells[i] = new_cell
                return
        self.cells.append(new_cell)

    def get_values(self) -> list[int]:
        return list(filter(lambda value: bool(value), map(lambda cell: cell.value, self.cells)))
