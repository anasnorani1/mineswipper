import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize empty board
        self.board = [[False for _ in range(width)] for _ in range(height)]

        # Randomly add mines
        while len(self.mines) < mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.board[i][j] = True
                self.mines.add((i, j))

        self.mines_found = set()

    def print(self):
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                print("|X" if self.board[i][j] else "| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        count = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count

    def won(self):
        return self.mines_found == self.mines


class Sentence():
    """
    A logical statement about the game: a set of cells with a count of how many are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return isinstance(other, Sentence) and self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        return set(self.cells) if len(self.cells) == self.count and self.count != 0 else set()

    def known_safes(self):
        return set(self.cells) if self.count == 0 else set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    AI to play Minesweeper
    """

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # Step 1: Mark the cell as a move made and safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Step 2: Get neighbors (adjacent cells that aren't already known to be safe or mines)
        neighbors = set()
        i, j = cell
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if (di, dj) == (0, 0):
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbor = (ni, nj)
                    if neighbor in self.mines:
                        count -= 1
                    elif neighbor not in self.safes:
                        neighbors.add(neighbor)

        # Step 3: Add new sentence to knowledge base
        new_sentence = Sentence(neighbors, count)
        if new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)

        # Step 4: Update knowledge
        self.update_knowledge()

    def update_knowledge(self):
        updated = True
        while updated:
            updated = False
            safes = set()
            mines = set()

            for sentence in self.knowledge:
                safes |= sentence.known_safes()
                mines |= sentence.known_mines()

            if safes:
                updated = True
                for cell in safes:
                    self.mark_safe(cell)

            if mines:
                updated = True
                for cell in mines:
                    self.mark_mine(cell)

            # Subset inference: if S1 ⊆ S2, then infer S2 - S1 = C2 - C1
            new_inferences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 == s2 or not s1.cells or not s2.cells:
                        continue
                    if s1.cells.issubset(s2.cells):
                        diff_cells = s2.cells - s1.cells
                        diff_count = s2.count - s1.count
                        new_sentence = Sentence(diff_cells, diff_count)
                        if new_sentence not in self.knowledge and new_sentence not in new_inferences:
                            new_inferences.append(new_sentence)
                            updated = True

            self.knowledge.extend(new_inferences)
            self.knowledge = [s for s in self.knowledge if s.cells]

    def make_safe_move(self):
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        choices = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        return random.choice(choices) if choices else None
