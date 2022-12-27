# from solver import *

from ir_solver import InfoTheoreticSolver


class NorvigSolver(InfoTheoreticSolver):
    def __init__(self, wordle, wordhoard, verbose=False, mode="ir", top_n=4500):
        super().__init__(wordle, wordhoard, verbose, mode, top_n)
        self.possible_solutions_list = self.possible_solutions_list | set(['handy', 'swift', 'glove', 'crump'])
        self.initial_guesses = ['handy', 'swift', 'glove', 'crump']

    def guess(self):
        if len(self.possible_solutions()) == 1:
            return list(self.possible_solutions())[0]
        if len(self.guesses) < len(self.initial_guesses):
            return self.initial_guesses[len(self.guesses)]
        else:
            return super().guess()
