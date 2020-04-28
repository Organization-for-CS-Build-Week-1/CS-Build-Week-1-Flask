"""
Types of Items:

- Trash:  low  score
- Gem:    high score, high weight. Hidden in rocks
- Stick:  mid  score, mid weight

- Hammer: no   score, no weight.   Can be used to break rocks
"""
from random import randint


class Item:
    """Base class for all Items. Use Child classes when possible"""

    def __init__(self, name, description, id=0, weight=None, score=None):
        self.name        = name
        self.description = description
        self.id          = id

        if weight == None and score == None:
            self.weight = 1
            self.score  = 1
        elif weight == None:
            self.weight = 1
        elif score == None:
            self.score  = 1
        else:
            self.weight = weight
            self.score  = score

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
            'score': self.score,
        }

    def __repr__(self):
        return (
            f"{{\n"
            f"\t\tid: {self.id},\n"
            f"\t\tname: {self.name},\n"
            f"\t\tdescription: {self.description},\n"
            f"\t\tweight: {self.weight},\n"
            f"\t\tscore: {self.score},\n"
            f"\t}}\n"
        )


class Trash(Item):
    """Item with low score, low-ish weight. Try not to get too much."""

    def __init__(self, id, weight = None, score = None):
        if weight == None and score == None:
            self.weight = randint(10, 30)
            self.score  = randint(1, 10) * 100
        elif weight == None:
            self.weight = randint(10, 30)
        elif score == None:
            self.score  = randint(1, 10) * 100
        else:
            self.weight = weight
            self.score  = score

        super().__init__("Trash", "Low score, low weight. Try not to get too much", id, self.weight, self.score)


class Stick(Item):
    """Item with medium score, medium weight. not bad for an ant."""

    def __init__(self, id, weight=None, score=None):
        if weight == None and score == None:
            self.weight = randint(30, 70)
            self.score  = randint(10, 25) * 100
        elif weight == None:
            self.weight = randint(30, 70)
        elif score == None:
            self.score  = randint(10, 25) * 100
        else:
            self.weight = weight
            self.score  = score

        super().__init__("Stick", "Medium score, medium weight. not bad for an ant", id, self.weight, self.score)


class Gem(Item):
    """Item with high score, high weight. Covered by a rock."""

    def __init__(self, id, weight=None, score=None):
        if weight == None and score == None:
            self.weight = randint(50, 100)
            self.score  = randint(50, 100) * 100
        elif weight == None:
            self.weight = randint(10, 100)
        elif score == None:
            self.score  = randint(50, 100) * 100
        else:
            self.weight = weight
            self.score  = score

        super().__init__("Gem", "High score, high weight. Covered by a rock.", id, self.weight, self.score)


class Hammer(Item):
    """Only tool able to break rocks and uncover gems."""

    def __init__(self, id, weight=None, score=None):
        if weight == None and score == None:
            self.weight = randint(50, 100)
            self.score  = randint(25, 50) * 100
        elif weight == None:
            self.weight = randint(50, 100)
        elif score == None:
            self.score  = randint(25, 50) * 100
        else:
            self.weight = weight
            self.score  = score

        super().__init__("Hammer", "Tool able to break rocks and uncover gems.", id, self.weight, self.score)


def db_to_class(model_info):
    """Function that takes in DB information and returns the correct Item class"""
    if model_info.name == "Trash":
        return Trash(model_info.id, model_info.weight, model_info.score)
    if model_info.name == "Stick":
        return Stick(model_info.id, model_info.weight, model_info.score)
    if model_info.name == "Gem":
        return Gem(model_info.id, model_info.weight, model_info.score)
    if model_info.name == "Hammer":
        return Hammer(model_info.id, model_info.weight, model_info.score)
    raise TypeError("Name must be a subclass of an item")
