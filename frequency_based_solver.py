# from solver import *
from collections import Counter

from solver import Solver
from wordle_knowledge import WordleKnowledge


class FrequencyBasedSolver(Solver):

  def __init__(self, wordle, wordhoard=None, verbose=False):
    super().__init__(wordle, wordhoard, verbose)
    self.possible_solutions_list = set(self.wordhoard.words)
    self.state = WordleKnowledge(wordle, self.wordhoard)

  def update(self, guess, feedback):
        """Update the knowledge of the wordle puzzle
        """
        # call the super method
        super().update(guess, feedback)
        # print(f"[bold blue]{guess}[/bold blue]; {color_feedback(feedback, guess)}")
        self.state.update(guess, feedback)
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
