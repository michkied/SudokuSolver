import math
from prettytable import PrettyTable, ALL

with open('sudoku_input.txt', 'r+') as f:
    sudoku_input = f.read()

grid = []
rows = sudoku_input.split('\n')
for row in rows:
    grid.append([int(value) for value in row])

numbers = set(range(1, len(rows)+1))

index = {}

n = 0
for y, row in enumerate(grid):
    for x, cell in enumerate(row):
        row[x] = {
            'value': cell,
            'id': n
        }

        if cell == 0:
            row[x]['possible_values'] = numbers

        index[n] = (y, x)

        n += 1

square_side = int(len(grid) ** 0.5)


def generate_checks():
    rows = grid

    columns = []
    squares = []
    for _ in grid:
        columns.append([])
        squares.append([])

    for y, row in enumerate(rows):
        square_y = math.ceil((y + 1) / square_side) - 1

        for x, cell in enumerate(row):
            columns[x].append(cell)

            square_x = math.ceil((x + 1) / square_side) - 1
            squares[square_x + square_y * square_side].append(cell)

    return rows, columns, squares


def remove_wrong_values(check):
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

                y, x = index[cell['id']][0], \
                       index[cell['id']][1]
                grid[y][x] = cell


def pick_lone_possible_values(check):
    for line in check:
        remove_wrong_values(generate_checks()[0])
        remove_wrong_values(generate_checks()[1])
        remove_wrong_values(generate_checks()[2])

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

                    y, x = index[cell['id']][0], \
                           index[cell['id']][1]
                    grid[y][x] = cell

                    break


def print_sudoku():
    squares = generate_checks()[2]
    for i, square in enumerate(squares):
        square_rows = []

        for i2, cell in enumerate(square):
            if i2 % square_side != 0:
                square_rows[-1] += f" {str(cell['value'])}"
            else:
                square_rows.append(str(cell['value']))

        pretty_square = ('\n'.join(square_rows)).replace('0', ' ')
        squares[i] = pretty_square

    square_grid = list([squares[i:i + square_side] for i in range(0, len(squares), square_side)])

    tab = PrettyTable()
    tab.header = False
    tab.add_rows(square_grid)
    tab.hrules = ALL
    tab.vrules = ALL
    print(tab)


def run():
    print('INPUT:')
    print_sudoku()

    num = 1
    while True:
        grid_before = str(grid)

        remove_wrong_values(generate_checks()[0])
        remove_wrong_values(generate_checks()[1])
        remove_wrong_values(generate_checks()[2])

        pick_lone_possible_values(generate_checks()[2])

        if grid_before == str(grid):
            break

        print(f'\nRun #{num}')
        print_sudoku()

        num += 1

    for row in grid:
        for cell in row:
            if cell['value'] == 0:
                print('\n\nFAILED! Following cells are ambiguous:')
                for row in grid:
                    print(list(map(lambda _: _['value'] if _['value'] != 0 else _['possible_values'], row)))
                return

    print(f'\n\nSUCCESS! Completed in {num - 1} run(s)')
    print_sudoku()


if __name__ == "__main__":
    run()
