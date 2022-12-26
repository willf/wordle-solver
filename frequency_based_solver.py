# from solver import *
from collections import Counter

from solver import Solver


class WordleKnowledge:
    def __init__(self, wordle, wordhoard):
        self.counter = Counter()
        for word in wordhoard.words:
            for letter in word:
                self.counter[letter] += 1
        letters = sorted(self.counter.keys())
        self.letter_sets = [set(letters) for i in range(wordle.size)]
        self.required_letters = set()
        self.wordle = wordle
        self.wordhoard = wordhoard

    def is_consistent(self, word):
        for i in range(self.wordle.size):
            letter = word[i]
            letter_set = self.letter_sets[i]
            found = letter in letter_set
            if not found:
                return False
        return all(letter in word for letter in self.required_letters)

    def update_exact(self, letter, position):
        self.required_letters.add(letter)
        self.letter_sets[position] = set(letter)

    def update_required(self, letter, position):
        self.required_letters.add(letter)
        if letter in self.letter_sets[position]:
            self.letter_sets[position].remove(letter)

    def update_forbidden(self, letter, position):
        for letter_set in self.letter_sets:
            if letter in letter_set and letter not in self.required_letters:
                letter_set.remove(letter)

    def __repr__(self):
        return f"{self.required_letters} {self.letter_sets}"

class FrequencyBasedSolver(Solver):

  def __init__(self, wordle, wordhoard=None, verbose=False):
    super().__init__(wordle, wordhoard, verbose)
    self.possible_solutions_list = set(self.wordhoard.words)
    self.state = WordleKnowledge(wordle, self.wordhoard)

  def update_knowledge(self, guess, feedback):
        """Update the knowledge of the wordle puzzle
        """
        # print(f"[bold blue]{guess}[/bold blue]; {color_feedback(feedback, guess)}")
        for i in range(self.wordle.size):
            if feedback[i] == "g":
                self.state.update_exact(guess[i], i)
            elif feedback[i] == "y":
                self.state.update_required(guess[i], i)
            else:
                self.state.update_forbidden(guess[i], i)
        self.possible_solutions_list = [
            word
            for word in self.possible_solutions_list
            if self.state.is_consistent(word) and word != guess
        ]
        # print(f"{len(self.possible_solutions_list)} possible solutions")

  def possible_solutions(self):
    return self.possible_solutions_list

  def guess(self):
      return self.wordhoard.most_frequent_word(self.possible_solutions_list)
