import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        #print(self.domains.keys())
        
        for key,item in self.domains.items():
            for i in item.copy():
                if key.length != len(i):
                    self.domains[key].remove(i)
        
        #print(self.crossword.overlaps)
        #print(self.crossword.overlaps[Variable(4, 1, 'across', 4), Variable(0, 1, 'down', 5)])        
        #raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        if self.crossword.overlaps[x,y] is None:
            return False
        
        l = []                      #a list of variables to be removed as we cannot remove variable during iteration 
        for word1 in self.domains[x]:
            for word2 in self.domains[y]:
                #print(word1,word2)
                if word1[self.crossword.overlaps[x,y][0]] == word2[self.crossword.overlaps[x,y][1]]:
                    #print(word1,word2)
                    break
            else:        
                l.append(word1)
                revised = True
        #print(l)
        for word in l:
            #print(l)
            #print(self.domains[x])
            #print(word)
            self.domains[x].remove(word)
            
        #print(self.domains)
        return revised
       
        raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []
        if arcs is None:
            
            for v1 in self.domains.keys():
                for v2 in self.domains.keys():
                    if v1!=v2:
                        queue.append((v1,v2))
                        

        else:
            for i in arcs:
                queue.append(i)
        
        while(len(queue) != 0):
            (x,y) = queue[0]
            #print(x,y)
            queue.remove((x,y))
            #print(x,y)
            #print(self.domains[x])
            if self.revise(x,y):
                if (len(self.domains[x])==0):
                    
                    return False
                for z in (self.crossword.neighbors(x) - {y}):
                    #print(self.crossword.neighbors(x) - {y})
                    queue.append((z,x))
                    #print(z)

        #print(self.domains)
        return True
        #print(queue)

        #raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        #print(assignment,"assignment")
        for variable in self.domains.keys():
        #    print(variable)
        #print(assignment)
            if variable not in assignment.keys():
                return False
            
            elif (assignment[variable]) is None:
                return False
        return True

        raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        vals = []
        for key,value in assignment.items():
            if value in vals:
                return False
            
            vals.append(value)
            if key.length != len(value):
                return False
            
            for variable in self.crossword.neighbors(key):
                overlap = self.crossword.overlaps[key, variable]
                
                if variable in assignment:
                    if assignment[variable][overlap[1]] != value[overlap[0]]:
                        return False
            
            
        return True

        raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        
        order = {}
        for variable in self.domains[var]:
            
            if variable in assignment:
                continue
            
            
            else:
                value = 0
                for neighbor in self.crossword.neighbors(var):
                
                    (x,y) = self.crossword.overlaps[var, neighbor]
                    
                    for v2 in self.domains[neighbor]:
                        #print(variable,"variable")
                        #print(v2,"v2")
                        #print(self.domains[neighbor][v2])
                        
                        if variable[x] != v2[y]:
                            value = value+1 
                        #    print(value)
            order[variable] = value
        #print(order)

        order_list = (sorted(order.items(), key = lambda x:x[1]))
        l = []
        for i in order_list:
            l.append(i[0])
        return l
        raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        count = 0
        for variable in self.domains.keys():
            if variable in assignment:
                continue
                
            else:
                degree = len(list(self.crossword.neighbors(variable)))
                #print(degree,"degree")
                if degree> count:
                    unassigned_var = variable
                    count = degree
                elif degree == count:
                    #print(len(self.domains[variable]),variable)
                    #print(len(self.domains[unassigned_var]),unassigned_var)
                    mrv = len(list(self.domains[variable]))          
                    if mrv< len(list(self.domains[unassigned_var])):
                        unassigned_var = variable
                    #rint(unassigned_var)
        return unassigned_var
        
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #print(assignment)
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                #print(result)
                if result is not None:
                    
                    return result
            
            assignment.pop(var)
        return None            

        #raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
