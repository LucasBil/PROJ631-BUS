class Station:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"{self.name}"
    def __repr__(self):
        return f"{self}"
    
    def __eq__(self, value):
        if isinstance(value, Station):
            return self.name == value.name
        elif isinstance(value, str):
            return self.name == value
        return False
    def __hash__(self):
        return hash(self.name)
    
    def to_dict(self):
        return { "name" : self.name }