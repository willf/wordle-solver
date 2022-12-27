# from collections import Counter


class WordleKnowledge:
    def __init__(self, wordle, wordhoard):
        self.letters = set()
        for word in wordhoard.words:
            for letter in word:
                self.letters.add(letter)
        self.letter_sets = [set(self.letters) for i in range(wordle.size)]
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

    def update_forbidden(self, letter):
        for letter_set in self.letter_sets:
            if letter in letter_set and letter not in self.required_letters:
                letter_set.remove(letter)

    def update(self, guess, feedback):
        """Update the knowledge of the wordle puzzle
        """
        # print(f"[bold blue]{guess}[/bold blue]; {color_feedback(feedback, guess)}")
        for i in range(self.wordle.size):
            if feedback[i] == "g":
                self.update_exact(guess[i], i)
            elif feedback[i] == "y":
                self.update_required(guess[i], i)
            else:
                self.update_forbidden(guess[i])

    def __repr__(self):
        return f"{self.required_letters} {self.letter_sets}"
