from utils.networks.node import Node

class Edge:
    def __init__(self, src:Node, dest:Node, weight=1):
        self.src = src
        self.dest = dest
        self.weight = weight
    
    def __str__(self):
        return f"({self.src}, {self.dest}, {self.weight})"
    def __repr__(self):
        return f"({self.src}, {self.dest}, {self.weight})"
    
    def to_dict(self):
        return {
            "src": self.src,
            "dest": self.dest,
            "weight": self.weight
        }