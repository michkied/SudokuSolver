import copy
from grid import *


@dataclass
class Guess:
    cell: Cell
    value: int
    grid_before_guess: Grid
    id: int


class SudokuSolver:
    def __init__(self):
        with open('sudoku_input.txt', 'r+') as f:
            sudoku_input = f.read()
        raw_rows = sudoku_input.split('\n')

        try:
            self.grid = Grid(raw_rows)
        except IndexError:
            print(f'\nPROVIDED SUDOKU IS INVALID')
            return

        if not self.grid.is_correct():
            print(f'\nPROVIDED SUDOKU IS INVALID')
            return

        print('INPUT:')
        self.grid.print()

        self.solve()

    def solve(self):
        runs = 1
        guesses = 0
        guess_memory = []

        while True:

            while True:
                grid_before = copy.deepcopy(self.grid)

                self.grid.remove_wrong_possible_values()
                self.grid.remove_conflicting_possible_values()
                self.grid.pick_values()
                self.grid.pick_lone_possible_values()

                if grid_before == self.grid:
                    break

                print(f'\nRun #{runs}')
                self.grid.print()

                runs += 1

            if self.grid.is_correct() and self.grid.is_filled():
                print(f'\n\nSUCCESS! Completed in {runs - 1} run(s) and {guesses} guess(es)')
                self.grid.print()
                return

            no_possible_values = False
            if self.grid.is_correct():

                cell = self.grid.get_first_ambiguous_value()

                if not cell.possible_values:
                    no_possible_values = True
                else:
                    value = min(cell.possible_values)
                    guesses += 1
                    guess = Guess(cell, value, copy.deepcopy(self.grid), guesses)

                    guess_memory.append(guess)

                    cell.value = value
                    self.grid.update_cell(cell)
                    print(f'\nGUESS #{guesses} - Checking if cell #{cell.id+1} could be {value}')
                    self.grid.print(highlight=cell.id)

            if not self.grid.is_correct() or no_possible_values:
                if not guess_memory:
                    print('\n\nFAILURE! Couldn\'t solve this sudoku')
                    self.grid.print(display_ambiguous=True)
                    return

                last_guess = guess_memory[-1]

                print(f'\nGuess #{last_guess.id} was wrong.')

                while not last_guess.cell.possible_values - {last_guess.value}:
                    print(f'Guess #{last_guess.id} is a dead end.')
                    if len(guess_memory) == 1:
                        print('\n\nFAILURE! Couldn\'t solve this sudoku')
                        last_guess.grid_before_guess.print()
                        return
                    guess_memory.pop(-1)
                    last_guess = guess_memory[-1]
                    print(f'Reverting to guess #{last_guess.id}')

                self.grid = last_guess.grid_before_guess
                last_guess.cell.possible_values.remove(last_guess.value)
                value = min(last_guess.cell.possible_values)

                last_guess.cell.value = value

                guesses += 1
                guess = Guess(last_guess.cell, value, copy.deepcopy(self.grid), guesses)
                guess_memory[-1] = guess

                self.grid.update_cell(last_guess.cell)
                print(f'\nGUESS #{guesses} - Checking if cell #{last_guess.cell.id+1} could be {value}')
                self.grid.print(highlight=last_guess.cell.id)


SudokuSolver()
