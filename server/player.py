class Player:
    name: str
    id: int
    color: str
    role: str

    def __init__(self, name: str, id: int, color: str, role: str):
        self.name = name
        self.id = id
        self.color = color
        self.role = role

    def __str__(self):
        return "{n} ({i}): {c}/{r}".format(n = self.name, i = self.id, c = self.color, r = self.role)
    
    def toDict(self):
        """
        Player data to dictionary
        
        Returns:
            [Dict] -- player representation
        """
        r = {
            "name" : self.name,
            "id" : self.id,
            "color" : self.color,
            "role" : self.role
        }

        return r