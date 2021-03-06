# Wordle Solver and CLI Player

A Python-based [Wordle](https://www.powerlanguage.co.uk/wordle/) solver and CLI player

This was created using Python 3.9.7.

SPOILER ALERT: the `data` directory contains spoilers for upcoming Wordle games. View at your own risk 😅.

The only requirement, I think is for the [rich](https://pypi.org/project/rich/) libary, and that's just for the CLI.

To play a game:

```bash
python cli -h
usage: cli.py [-h] [-n NUMBER]

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        Archived Wordle game
```

You can play against archived games, or choose a random word by not
specifying `-n` at all.

To use the solver:

```bash
echo 'badly' | python solver.py
```

To select a start word, use the `-g` flag:

```base
echo 'badly' | python solver.py -g 'adieu' -v
```

To use Peter Norvig's [four guesses](https://github.com/norvig/pytudes/blob/main/ipynb/Wordle.ipynb), use the `--norvig` flag.

See `python solver.py -h` for more.

etc.

You can write your own Solver by subclassing `Solver`. The only required method is `guess`. I'm
sure you'll write a better solver than I did. But I'm spent enough time on this already. :clock1: :vampire:
