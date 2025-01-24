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
            "src": self.src.to_dict(),
            "dest": self.dest.to_dict(),
            "other": {
                "start": self.weight[0].strftime('%H:%M'),
                "end": self.weight[1].strftime('%H:%M'),
                "line": self.weight[3]
            }
        }