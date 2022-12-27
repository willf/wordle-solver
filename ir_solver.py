# from solver import *
import itertools
import math
import random
from functools import cache

from solver import Solver
from wordle_knowledge import WordleKnowledge


@cache
def all_possible_feedbacks(size):
    """Return a list of all possible feedbacks for a given size"""
    return ["".join(p) for p in itertools.product("byg", repeat=size)]


class InfoTheoreticSolver(Solver):

  def __init__(self, wordle, wordhoard=None, verbose=False, easy_mode=True, top_n=4500):
    super().__init__(wordle, wordhoard, verbose)
    self.easy_mode = easy_mode
    self.top_n = top_n
    # First, we limit our possible solutions to _common_ words
    most_frequent = self.wordhoard.most_frequent_words(self.top_n)
    self.possible_solutions_list = set(most_frequent)

    self.state = WordleKnowledge(wordle, self.wordhoard)

  # guessing 'fishy' and the word is 'doggy' -> feedback '.....'

  def collect_wordgroups_by_feedback(self, guess):
    word_feedbacks = [(possible_solution, self.wordle.feedback(guess, possible_solution)) for possible_solution in self.possible_solutions_list]
    return itertools.groupby(word_feedbacks, lambda x: x[1])

  def wordgroup_entropy(self, wordgroups):
    sizes = [len(list(g)) for _, g in wordgroups]
    total = sum(sizes)
    return sum(size / total * math.log2(1/(size / total)) for size in sizes)

  def guess_entropy(self, guess):
    return self.wordgroup_entropy(self.collect_wordgroups_by_feedback(guess))


  def update(self, guess, feedback):
        """Update the knowledge of the wordle puzzle
        """
        # call the super method
        super().update(guess, feedback)
        self.state.update(guess, feedback)
        self.possible_solutions_list = [
            word
            for word in self.possible_solutions_list
            if self.state.is_consistent(word) and word != guess
        ]

  def possible_solutions(self):
    return self.possible_solutions_list

  def guess(self):
      # return best by entropy
      print("considering entropies...")
      entropies = [self.guess_entropy(g) for g in self.possible_solutions_list]
      zipped = zip(self.possible_solutions_list, entropies)
      sorted_zipped = sorted(zipped, key=lambda x: x[1], reverse=True)
      best_guess, best_entropy = sorted_zipped[0]
      print(f"Best guess: {best_guess} with entropy {best_entropy}")
      return best_guess
