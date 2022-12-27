import argparse
import json
import math
import time

from rich import print

from solver import *
from wordhoard import *
from wordle import *

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s", "--solver", help="Kind of solver", type=str, default=None
)
parser.add_argument("-g", "--guesses", help="Supplied Guesses", default=None)

args = parser.parse_args()

if args.solver not in ['frequency', 'random', 'ir', 'norvig']:
  raise ValueError(f"Unknown solver: {args.solver}")

if args.guesses:
  guesses = args.guesses.split(',')
else:
  guesses = []

feedback = '?????'
args.verbose = True
args.mode = 'easy'
args.top_n = 4500
solver = create_solver(args.solver, Wordle(), WordHoard(), args)
for guess in guesses:
  print(f"Guess: {guess} feedback? >",)
  feedback = sys.stdin.readline().strip().lower()
  solver.update(guess, feedback)
while True and solver.possible_solutions() and feedback != 'ggggg':
  guess = solver.guess()
  print(f"Guess: {guess} feedback? >",)
  feedback = sys.stdin.readline().strip().lower()
  solver.update(guess, feedback)

print(f"Got it in {len(solver.guesses)}! Guesses: {', '.join(solver.guesses)}")
