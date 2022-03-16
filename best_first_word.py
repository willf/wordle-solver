from solver import *
from wordhoard import *
from wordle import *
from datetime import datetime
from rich.progress import Progress

wordhoard = WordHoard()
words = sorted(wordhoard.words_with_frequency(1000000))

puzzles = [puzzle.strip() for puzzle in open(SOLUTION_FILE).read().splitlines()]
# puzzles = puzzles[:10]

with Progress() as progress:
    task = progress.add_task("Investigating...", total=len(words))
    estimated_seconds = len(words) * 30  # 30 seconds per word
    progress.console.print(
        f"[bold red]{len(words)}[/bold red] words to investigate over [bold red]{len(puzzles)}[/bold red] puzzles"
    )
    progress.console.print(
        f"[bold red]{estimated_seconds/3600.0:.4}[/bold red] hours to finish (around {datetime.fromtimestamp(time.time() + estimated_seconds)})"
    )
    for word in words:
        progress.console.print(f"Working on word {word}")
        start_time = time.time()
        solutions = []
        for puzzle in puzzles:
            solutions.append(
                Solver(
                    Wordle(size=5, target=puzzle.strip(), wordhoard=wordhoard),
                    verbose=False,
                    wordhoard=wordhoard,
                ).solve(guesses=[word])
            )
        statistics = stats(solutions, start_time, include_solutions=False)
        statistics["first_guess"] = word
        with open(f"/tmp/{word}.json", "w") as f:
            f.write(json.dumps(statistics))
        progress.console.print(
            f"{word} failure rate: {statistics['failure_rate']:.2%} after {statistics['elapsed_time']:.2f} seconds"
        )
        progress.advance(task)
exit(0)
