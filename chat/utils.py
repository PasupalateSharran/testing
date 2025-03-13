import random

superhero_names = [
    "Iron Man", "Spider-Man", "Black Widow", "Captain Marvel",
    "Thor", "Hulk", "Doctor Strange", "Wolverine", "Deadpool", "Black Panther"
]

def assign_superhero_name():
    return random.choice(superhero_names)
