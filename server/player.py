class Player:
    name: str
    id: int
    color: bool

    def __init__(self, name, id, color):
        self.name = name
        self.id = id
        self.color = color