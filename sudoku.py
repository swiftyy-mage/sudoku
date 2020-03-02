from itertools import product, combinations, chain
from functools import reduce
import argparse, pathlib, sys

class Grid:
    def __init__(self, input_grid):

        '''
        When talking generally about a row, column, or box, we will call it a
        subgrid.
        Defines the starting values of the Grid object by instantiating a Square
        object for every position on the 9x9 grid of the sudoku and adding these
        Square objects to the attribute self.grid_tuple, a tuple of every Square
        object read left to right, top to bottom.
        Also defines an attribute for every subgrid. Assigns a tuple
        to each of these attributes, and defines the tuple such that the correct
        Square objects will be members.
        Finally, defines tuples self.rows, self.columns, self.boxes, which are 
        defined such that for each, every corresponding subgrid will be a 
        member. Counting the subgrids left to right, top to bottom.

        '''

        self.input_grid = input_grid

        for row, col in product(range(9), repeat=2):
            setattr(
                self,
                f"cart_{str(col)}_{str(row)}",
                Square(col, row, self.input_grid[row * 9 + col]),
            )

        self.grid_tuple = tuple(
            getattr(self, f"cart_{str(col)}_{str(row)}")
            for col, row in product(range(9), repeat=2)
        )

        for i in range(9):
            setattr(
                self,
                f"row_{i}",
                tuple(square for square in self.grid_tuple if square.row == i),
            )
            setattr(
                self,
                f"col_{i}",
                tuple(square for square in self.grid_tuple if square.col == i),
            )
            setattr(
                self,
                f"box_{i}",
                tuple(square for square in self.grid_tuple if square.box == i),
            )

        self.rows = tuple(getattr(self, f"row_{i}") for i in range(9))
        self.cols = tuple(getattr(self, f"col_{i}") for i in range(9))
        self.boxes = tuple(getattr(self, f"box_{i}") for i in range(9))

    def initial_checks(self):

        '''
        Makes sure that before a sudoku is allowed to undergo self.advanced_checks,
        the following conditions are met, to prevent errors:

            - There is no Square with any possibility which has already been revealed
            in an adjacent subgrid.

            - There is no Square with only one possibility, yet no value.

            - There is no subgrid such that a possibility is only possible in one
            Square in that subgrid, with that Square having no value.

        If these conditions are found not to be met for some reason, the methods called
        will fix the reason and return True, causing self.initial_checks to return True
        causing the entire process to start from the beginning. When conditions are
        found to be met, returns False and the next stage can begin.

        '''

        for square in (s for s in self.grid_tuple if s.value == 0):

            if self.adjacent_elimination(square):
                return True

        for square in (s for s in self.grid_tuple if s.value == 0):

            if self.one_possibility(square):
                return True

        for subgrid in self.rows + self.cols + self.boxes:

            if self.only_instance(subgrid):
                return True

        return False

    def adjacent_elimination(self, square):

        '''
        For possibilities in Square, if this possibility is already revealed in
        another Square in an adjacent subgrid, remove this possibility from Square
        and return True.

        '''

        row_values = tuple(s.value for s in getattr(self, f"row_{square.row}"))
        col_values = tuple(s.value for s in getattr(self, f"col_{square.col}"))
        box_values = tuple(s.value for s in getattr(self, f"box_{square.box}"))

        check_rows = lambda x: x in row_values
        check_cols = lambda x: x in col_values
        check_boxes = lambda x: x in box_values

        filtered_rows = list(filter(check_rows, square.poss))
        filtered_cols = list(filter(check_cols, square.poss))
        filtered_boxes = list(filter(check_boxes, square.poss))

        if 0 < len(filtered_rows) + len(filtered_boxes) + len(filtered_cols):
            square.poss = [
                poss
                for poss in square.poss
                if (
                    (poss not in filtered_rows)
                    and (poss not in filtered_cols)
                    and (poss not in filtered_boxes)
                )
            ]
            return True

        else:
            return False

    def one_possibility(self, square):

        '''
        If there exists only one possibility in Square, then assign this possibility
        to the Square's value and return True. Else, return False.

        '''

        if len(square.poss) == 1:
            square.value = square.poss[0]
            return True

        else:
            return False

    def only_instance(self, subgrid):

        '''
        For those possibilities not yet determined in a subgrid, if that possibility
        is only valid for one Square, then to the Squares value and possibilities,
        assign this possibility and return True. Else, return False.
        '''

        not_determined = tuple(
            i for i in range(1, 10) if all(i != square.value for square in subgrid)
        )

        for possibility in not_determined:
            possible_in = tuple(
                square for square in subgrid if possibility in square.poss
            )
            if len(possible_in) == 1:
                possible_in[0].poss = [possibility]
                possible_in[0].value = possibility
                return True

        return False

    def advanced_checks(self):

        '''
        If the sudoku is still not solved, these checks might be able to solve it
        without needing to brute force it. If one of these checks removes a
        possibility or possibilities from a Square of Squares, they return True, 
        causing this method to return True, causing the entire loop to start at the
        beginning at self.initial_checks. If all checks are completed and nothing is
        found, return False and the brute forcing method will solve the sudoku.
        '''

        for i, subgrid in product(range(2, 9), self.rows + self.cols + self.boxes):

            if self.identical_possibilities(subgrid, i):
                return True

        for i, subgrid in product(range(2, 9), self.rows + self.cols + self.boxes):

            if self.unique_possibilities(subgrid, i):
                return True

        for subgrid in self.rows + self.cols:

            if self.box_line_intersection(subgrid, True):
                return True

        for subgrid in self.boxes:

            if self.box_line_intersection(subgrid, False):
                return True

        return False

    def identical_possibilities(self, subgrid, i):

        '''
        If there exist i Squares in subgrid, which have i possibilities which are
        identical to each other, remove these possibilities from every other Square
        in the subgrid, return True. Else, return False.

        '''

        not_determined = tuple(square for square in subgrid if square.value == 0)

        if len(not_determined) <= i:
            return False

        check_these = tuple(
            square for square in not_determined if len(square.poss) == i
        )

        if len(check_these) < i:
            return False

        square_combs = combinations(check_these, i)
        poss_equality = lambda x: all(x[0].poss == y.poss for y in x[1:])
        identical_poss = tuple(filter(poss_equality, square_combs))

        if len(identical_poss) == 0:
            return False

        subgrid_poss_copy = tuple(square.poss.copy() for square in not_determined)

        for equal_squares in identical_poss:
            removable_poss = equal_squares[0].poss
            poss_square_grid = (
                (remove_from, remove_this)
                for (remove_from, remove_this) in product(
                    not_determined, removable_poss
                )
                if (
                    (remove_this in remove_from.poss)
                    and (remove_from not in equal_squares)
                )
            )

            for remove_from, remove_this in poss_square_grid:
                remove_from.poss.remove(remove_this)

        return subgrid_poss_copy != tuple(square.poss for square in not_determined)

    def unique_possibilities(self, subgrid, i):

        '''
        If there exist i Squares in subgrid which share i possibilities not found in
        any other Square in subgrid, then remove all other possibilities from the i 
        Squares, return True. Else, return False.
        '''

        not_determined = tuple(square for square in subgrid if square.value == 0)

        if len(not_determined) <= i:
            return False

        subgrid_poss_copy = tuple(square.poss.copy() for square in not_determined)

        square_combs = combinations(not_determined, i)
        intersection = lambda x, y: x & y
        shared_poss = tuple(
            (
                sorted(list(reduce(intersection, (set(s.poss) for s in squares)))),
                squares,
            )
            for squares in square_combs
        )

        for (intersecting_poss, squares) in shared_poss:
            check_squares = tuple(
                square for square in not_determined if square not in squares
            )
            check_poss = sorted(
                tuple(
                    set(
                        chain.from_iterable(square.poss for square in check_squares)
                    )
                )
            )

            poss_combs = combinations(intersecting_poss, i)

            for poss in poss_combs:
                if all(p not in check_poss for p in poss):
                    for square in squares:
                        square.poss = sorted(list(poss))

        return subgrid_poss_copy != tuple(square.poss for square in not_determined)

    def box_line_intersection(self, subgrid, is_line):

        '''
        If subgrid is a row or column:
        For those possibilities not yet determined in subgrid, if all Squares in which
        this possibility is possible are members of the same box, then remove this
        possibility from all other Squares in that box, return True. Else, return False

        If subgrid is a box.
        For those possibilities not yet determined in subgrid, if all Squares in which
        this possibility are possible are members of the same row or column, then
        remove this possibility from all other Squares in this row or column, return
        True. Else, return False

        '''

        grid_poss_copy = tuple(square.poss.copy() for square in self.grid_tuple)

        not_determined = tuple(
            i for i in range(1, 10) if all(i != square.value for square in subgrid)
        )

        for possibility in not_determined:
            possible_in = tuple(
                square for square in subgrid if possibility in square.poss
            )

            if len(possible_in) < 2:
                continue

            if is_line and all(
                possible_in[0].box == square.box for square in possible_in[1:]
            ):
                remove_from = tuple(
                    square
                    for square in getattr(self, f"box_{possible_in[0].box}")
                    if (possibility in square.poss) and (square not in subgrid)
                )

                for square in remove_from:
                    square.poss.remove(possibility)

            if not is_line and all(
                possible_in[0].row == square.row for square in possible_in[1:]
            ):
                remove_from = tuple(
                    square
                    for square in getattr(self, f"row_{possible_in[0].row}")
                    if (possibility in square.poss) and (square not in subgrid)
                )

                for square in remove_from:
                    square.poss.remove(possibility)

            if not is_line and all(
                possible_in[0].col == square.col for square in possible_in[1:]
            ):
                remove_from = tuple(
                    square
                    for square in getattr(self, f"col_{possible_in[0].col}")
                    if (possibility in square.poss) and (square not in subgrid)
                )

                for square in remove_from:
                    square.poss.remove(possibility)

        return grid_poss_copy != tuple(square.poss for square in self.grid_tuple)

    def brute_force(self):

        '''
        Copied from Professor Thorsten Altenkirch.
        https://www.youtube.com/watch?v=G_UYXzGuqvM&t=106s

        '''

        for square in tuple(s for s in self.grid_tuple if s.value == 0):
            for poss in range(1, 10):

                if poss not in tuple(
                    s.value
                    for s in getattr(self, f"row_{square.row}")
                    + getattr(self, f"col_{square.col}")
                    + getattr(self, f"box_{square.box}")
                ):
                    square.value = poss
                    self.brute_force()
                    square.value = 0

            return

        self.solution = tuple(s.value for s in self.grid_tuple)

    def board_full(self):
        return all(square.value != 0 for square in self.grid_tuple)

    def __str__(self):

        '''
        Defines the printable string representation.
        '''

        return f"\n\n		  {self.cart_0_0.value}  |  {self.cart_1_0.value}\
  |  {self.cart_2_0.value}  |  {self.cart_3_0.value}  |  {self.cart_4_0.value}\
  |  {self.cart_5_0.value}  |  {self.cart_6_0.value}  |  {self.cart_7_0.value}\
  |  {self.cart_8_0.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_1.value}  |  {self.cart_1_1.value}  |  {self.cart_2_1.value}\
  |  {self.cart_3_1.value}  |  {self.cart_4_1.value}  |  {self.cart_5_1.value}\
  |  {self.cart_6_1.value}  |  {self.cart_7_1.value}  |  {self.cart_8_1.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_2.value}  |  {self.cart_1_2.value}  |  {self.cart_2_2.value}\
  |  {self.cart_3_2.value}  |  {self.cart_4_2.value}  |  {self.cart_5_2.value}\
  |  {self.cart_6_2.value}  |  {self.cart_7_2.value}  |  {self.cart_8_2.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_3.value}  |  {self.cart_1_3.value}  |  {self.cart_2_3.value}\
  |  {self.cart_3_3.value}  |  {self.cart_4_3.value}  |  {self.cart_5_3.value}\
  |  {self.cart_6_3.value}  |  {self.cart_7_3.value}  |  {self.cart_8_3.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_4.value}  |  {self.cart_1_4.value}  |  {self.cart_2_4.value}\
  |  {self.cart_3_4.value}  |  {self.cart_4_4.value}  |  {self.cart_5_4.value}\
  |  {self.cart_6_4.value}  |  {self.cart_7_4.value}  |  {self.cart_8_4.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_5.value}  |  {self.cart_1_5.value}  |  {self.cart_2_5.value}\
  |  {self.cart_3_5.value}  |  {self.cart_4_5.value}  |  {self.cart_5_5.value}\
  |  {self.cart_6_5.value}  |  {self.cart_7_5.value}  |  {self.cart_8_5.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_6.value}  |  {self.cart_1_6.value}  |  {self.cart_2_6.value}\
  |  {self.cart_3_6.value}  |  {self.cart_4_6.value}  |  {self.cart_5_6.value}\
  |  {self.cart_6_6.value}  |  {self.cart_7_6.value}  |  {self.cart_8_6.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_7.value}  |  {self.cart_1_7.value}  |  {self.cart_2_7.value}\
  |  {self.cart_3_7.value}  |  {self.cart_4_7.value}  |  {self.cart_5_7.value}\
  |  {self.cart_6_7.value}  |  {self.cart_7_7.value}  |  {self.cart_8_7.value}  \n\
		-----|-----|-----|-----|-----|-----|-----|-----|-----\n\
		  {self.cart_0_8.value}  |  {self.cart_1_8.value}  |  {self.cart_2_8.value}\
  |  {self.cart_3_8.value}  |  {self.cart_4_8.value}  |  {self.cart_5_8.value}\
  |  {self.cart_6_8.value}  |  {self.cart_7_8.value}  |  {self.cart_8_8.value}  \n\n"


class Square:
    def __init__(self, col, row, value):

        '''
        Uses row, col to determine self.row, self.col, and self.box. Uses
        value to determine self.value and self.poss.

        '''

        self.row = row
        self.col = col
        box_classifier = {
            (0, 0): 0,
            (1, 0): 0,
            (2, 0): 0,
            (0, 1): 0,
            (1, 1): 0,
            (2, 1): 0,
            (0, 2): 0,
            (1, 2): 0,
            (2, 2): 0,
            (3, 0): 1,
            (4, 0): 1,
            (5, 0): 1,
            (3, 1): 1,
            (4, 1): 1,
            (5, 1): 1,
            (3, 2): 1,
            (4, 2): 1,
            (5, 2): 1,
            (6, 0): 2,
            (7, 0): 2,
            (8, 0): 2,
            (6, 1): 2,
            (7, 1): 2,
            (8, 1): 2,
            (6, 2): 2,
            (7, 2): 2,
            (8, 2): 2,
            (0, 3): 3,
            (1, 3): 3,
            (2, 3): 3,
            (0, 4): 3,
            (1, 4): 3,
            (2, 4): 3,
            (0, 5): 3,
            (1, 5): 3,
            (2, 5): 3,
            (3, 3): 4,
            (4, 3): 4,
            (5, 3): 4,
            (3, 4): 4,
            (4, 4): 4,
            (5, 4): 4,
            (3, 5): 4,
            (4, 5): 4,
            (5, 5): 4,
            (6, 3): 5,
            (7, 3): 5,
            (8, 3): 5,
            (6, 4): 5,
            (7, 4): 5,
            (8, 4): 5,
            (6, 5): 5,
            (7, 5): 5,
            (8, 5): 5,
            (0, 6): 6,
            (1, 6): 6,
            (2, 6): 6,
            (0, 7): 6,
            (1, 7): 6,
            (2, 7): 6,
            (0, 8): 6,
            (1, 8): 6,
            (2, 8): 6,
            (3, 6): 7,
            (4, 6): 7,
            (5, 6): 7,
            (3, 7): 7,
            (4, 7): 7,
            (5, 7): 7,
            (3, 8): 7,
            (4, 8): 7,
            (5, 8): 7,
            (6, 6): 8,
            (7, 6): 8,
            (8, 6): 8,
            (6, 7): 8,
            (7, 7): 8,
            (8, 7): 8,
            (6, 8): 8,
            (7, 8): 8,
            (8, 8): 8,
        }

        self.box = box_classifier[(col, row)]

        if value == 0:
            self.value = 0
            self.poss = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        else:
            self.value = value
            self.poss = [value]


def _parse_args(parser, args=None):

    parser.add_argument(
        "in_path",
        help="A valid path to a .sdk file containing the unsolved grids.",
        nargs="?",
    )
    parser.add_argument(
        "out_path",
        help="A valid path to a .sdk file containing the solved grids",
        nargs="?",
    )
    return parser.parse_args(args)


def main():

    parser = argparse.ArgumentParser()
    args = _parse_args(parser)

    if args.in_path:
        input_path = pathlib.Path(str(args.in_path))
        if not input_path.exists():
            print("Not a valid input path")
            sys.exit(1)
        if not input_path.suffix == ".sdk":
            print("Input is not a .sdk file.")
            sys.exit(1)
    else:
        print("Please enter a valid path containing the unsolved sudokus.")
        sys.exit(1)

    if args.out_path:
        output_path = pathlib.Path(args.out_path)
        if output_path.exists():
            print("This file already exists")
            sys.exit(1)
        if not output_path.suffix == ".sdk":
            print("Output is not a .sdk file.")
            sys.exit(1)

    # Allows the solver to tell the user which level of checking was 
    # required to solve the sudoku.
    explanation = {
        (True, False, False): "initial_checks",
        (True, True, False): "initial_checks and advanced_checks",
        (True, True, True): "initial_checks, advanced_checks and brute_force",
        (True, False, True): "initial_checks and brute_force",
    }

    with input_path.open("r") as reader:
        unsolved_strings = reader.readlines()

    grid_list = []

    for i, input_string in enumerate(unsolved_strings):

        input_grid = tuple(char for char in input_string if char != "\n")

        if any(char not in "0123456789" for char in input_grid):
            print(f"Not all characters in sudoku {i} are integers.")
            sys.exit(1)

        elif len(input_grid) != 81:
            print(f"Sudoku {i} does not have 81 characters.")
            sys.exit(1)

        input_grid = tuple(int(char) for char in input_grid)
        grid_list.append(input_grid)

    for i, input_grid in enumerate(grid_list):

        # Before attempting to solve the sudoku, no checking has occurred, 
        # so all the below values are False. If one of the below is ever
        # successful in removing a possibility from a Square, determining
        # a value, or finishing the solution, the appropriate variable is
        # set to True.
        initial_checks, advanced_checks, brute_force = False, False, False
        grid = Grid(input_grid)

        # If a check is successful, returns the loop to the starting position
        # in order to "clean up". For instance, after self.identical_possibilities
        # removes two possibilities from a Square, that Square may be left with
        # only one possibility left.
        while not grid.board_full():

            if grid.initial_checks():
                initial_checks = True
                continue

            elif grid.advanced_checks():
                advanced_checks = True
                continue

            else:
                # If both self.initial_checks and self.advanced_checks return False,
                # a recursive brute force algorithm is used to solve the remainder of
                # the sudoku.
                grid.brute_force()
                brute_force = True
                for j, square in enumerate(grid.grid_tuple):
                    square.value = grid.solution[j]
                continue
        else:
            print(
                f"\
solved sudoku {i} using {explanation[initial_checks, advanced_checks, brute_force]}."
            )
            print(grid)

            if args.out_path:

                with output_path.open("a") as writer:
                    for square in grid.grid_tuple:
                        writer.write(str(square.value))
                    writer.write("\n")


if __name__ == "__main__":
    main()
