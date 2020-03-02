# sudoku

When I was nearly done with this, I realised that `identical_possibilities` is the general case of `one_possibility`, in which i=1, and `unique_possibilities` is just the general case of `only_instance` in which i=1. In any possible update this will be top of my list to address, along with cleaning up `box_line_intersection`.

# How to use

To solve a particular sudoku, type in the starting values (0 taking the place of no value) into a single line of a document, save with the extension `.sdk` . Should not end with a new line. Then run:

    python sudoku.py <path/to/document.sdk> 

To solve multiple sudokus one after another, simply add more rows to your document. To create a new file with the completed values, run:

    python sudoku.py <path_to_document.sdk> <path/to/output.sdk>
    
    
I included sample_sudoku.sdk which contains 3 sudokus so you can test it.

# The Algorithm

The term subgrid will be used when talking generally about a row, column, or box.

	All possibilities true for all squares which have no value


	while sudoku not completed:
		for square in grid:
			for possibilities in square:
			
				if possibility is revealed in the same row, column or box:
					remove possibility from square.
					return start
					
			if only one possibility:			
				square value = possibility
				return start
				
		for subgrid in grid:
			for possibility not determined in subgrid:
			
				if possibility is only possible in one square in subgrid:
					squares value = possibility
					return start
					
		for i in range(2,9):
			for subgrid in grid:
			
				if there exist i squares with exactly i 
				identical possibilities in subgrid:
					remove these possibilities from all other
					squares in subgrid, return start
					
				if there exist i squares which share i unique
				possibilities not found anywhere else in the subgrid:
					remove all other possibilities from these
					x squares, return start
					
		for subgrid in grid:
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
		brute force a solution
		
