"""
Types of Items:

- Trash:  low  score
- Gem:    high score, high weight. Hidden in rocks
- Stick:  mid  score, mid weight

- Hammer: no   score, no weight.   Can be used to break rocks
"""


class Item:
    """Base class for all Items. Use Child classes when possible"""

    def __init__(self, name, description, weight, score, id=0):
        self.name        = name
        self.description = description
        self.weight      = weight
        self.score       = score
        self.id          = id

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'weight': self.weight,
            'score': self.score,
        }


class Trash(Item):
    """Item with low score, low-ish weight. Try not to get too much."""

    def __init__(self, weight, score, id):
        super().__init__("Trash", "Low score, low weight. Try not to get too much", weight, score, id)


class Stick(Item):
    """Item with medium score, medium weight. not bad for an ant."""

    def __init__(self, weight, score, id):
        super().__init__("Stick", "Medium score, medium weight. not bad for an ant", weight, score, id)


class Gem(Item):
    """Item with high score, high weight. Covered by a rock."""

    def __init__(self, weight, score, id):
        super().__init__("Gem", "High score, high weight. Covered by a rock.", weight, score, id)
        # Whether the gem is trapped in a rock. Always initialized True
        self.covered = True

    def serialize(self):
        output = super().serialize()
        output['covered'] = self.covered
        return output


class Hammer(Item):
    """Only tool able to break rocks and uncover gems."""

    def __init__(self, id):
        super().__init__("Hammer", "Tool able to break rocks and uncover gems.", 0, 0, id)


def db_to_class(model_info):
    """Function that takes in DB information and returns the correct Item class"""
    if model_info.name == "Trash":
        return Trash(model_info.weight, model_info.score, model_info.id)
    if model_info.name == "Stick":
        return Stick(model_info.weight, model_info.score, model_info.id)
    if model_info.name == "Gem":
        return Gem(model_info.weight, model_info.score, model_info.id)
    if model_info.name == "Hammer":
        return Hammer(model_info.id)
    raise TypeError("Name must be a subclass of an item")
