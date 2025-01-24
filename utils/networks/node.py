import json

class Node:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return f"{self.data}"
    def __repr__(self):
        return f"{self}"
    
    def __eq__(self, value):
        if isinstance(value, Node):
            return self.data == value.data
        return False
    def __hash__(self):
        return hash(self.data)
    
    def to_dict(self):
        return self.data.to_dict()