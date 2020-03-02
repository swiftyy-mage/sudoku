# sudoku

An implementation of the following algorithm.
The term subgrid be used when talking generally about a row, column, or box.

	All possibilities true for all squares which have no value


	while True:
		for square in grid:
			for possibilities in square:
			
				if possibility is revealed in the same row, column or box:
					remove possibility from square.
					return start
					
			if only one possibility:
			
				square value = possibility
				return start
				
		for subgrid (the rows, columns, boxes) in grid:
			for possibility not determined in subgrid:
			
				if possibility is only possible in one square in subgrid:
					squares value = possibility
					return start
					
		for i in range(2,9):
			for subgrid in rows + columns + boxes:
			
				if there exist i squares with exactly i 
				identical possibilities in subgrid:
					remove these possibilities from all other
					squares in subgrid, return start
					
				if there exist i squares which share i unique
				possibilities not found anywhere else in the subgrid:
					remove all other possibilities from these
					x squares, return start
					
		for subgrid in rows + columns:
			for possibilities not yet determined in subgrid:
			
				if this possibility is only found in squares which are
				members of the same box:
					remove this possibility from
					all other squares in this box, return start
					
		for box in boxes:
			for possibilities not yet determined in box:
			
				if this possibility is only found in squares which
				are members of the same row or column:
					remove this possibility from all other squares 
					in this row or column, return start
