import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

class Graph:
    def __init__(self, nodes=[], edges=[]):
        self.nodes = nodes
        self.edges = edges

    def getNodes(self):
        return self.nodes
    def getNode(self, data):
        for node in self.nodes:
            if node.data == data:
                return node
        return None
    
    def getEdges(self):
        return self.edges
    def getEdge(self, src, dest):
        for edge in self.edges:
            if edge.src == src and edge.dest == dest:
                return edge
        return None
    
    def errorDataEdges(self):
        for edge in self.edges:
            if edge.src not in self.nodes or edge.dest not in self.nodes:
                return True
            if edge.weight[0] > edge.weight[1]:
                return True
        return False

    def show(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.nodes)
        for edge in self.edges:
            G.add_edge(edge.src, edge.dest, hour_start=edge.weight[0], hour_end=edge.weight[1])

        # Récupérer les poids pour les afficher
        nx.draw(G, with_labels=True, font_weight='bold')

        # Create empty file if not exists
        if not os.path.exists("static/assets/map.png"):
            os.makedirs("static/assets", exist_ok=True)
            with open("map.png", "w") as f:
                pass

        try:
            plt.savefig("static/assets/map.png")
        except:
            pass

    def shortest(self, src, dest, datetime):
        def getWeight(args):
            return 1 # weight
        return self.djikstra(src, dest, datetime, getWeight)
    
    def fastest(self, src, dest, datetime): # algo djikstra
        def getWeight(args):
            return (args[0].weight[1] - args[1]).total_seconds() # waiting + trajet
        return self.djikstra(src, dest, datetime, getWeight)

    def djikstra(self, src, dest, datetime, lambda_weight):
        current_node = src
        nodes_toVisited = list(filter(lambda node: node != src, self.nodes))
        visited = [src]
        distances = {}
        for node in self.nodes:
            distances[node] = None if node != src else []
            
        while len(nodes_toVisited) > 0:
            seconds_to_add = sum([edge.weight[2] for edge in distances[current_node]])
            current_time = datetime + timedelta(seconds=seconds_to_add)

            edges = list(filter(lambda edge: edge.weight[0] >= current_time, self.edges)) # remove edges that are not available
            edges_of_node_src = list(filter(lambda edge: edge.src == current_node, edges))
            for edge in edges_of_node_src:
                edge.weight[2] = lambda_weight([edge, current_time])
            
            for node in self.nodes:
                edges_of_node_dest = list(filter(lambda edge: edge.dest == node, edges_of_node_src))
                if len(edges_of_node_dest) == 0:
                    continue

                min_edge = min(edges_of_node_dest, key=lambda edge: edge.weight[2])
                if distances[node] is None:
                    distances[node] = distances[current_node] + [min_edge]
                else:
                    total_weight_current = sum([edge.weight[2] for edge in distances[current_node]]) + min_edge.weight[2]
                    total_weight_node = sum([edge.weight[2] for edge in distances[node]])
                    if total_weight_current < total_weight_node:
                        distances[node] = distances[current_node] + [min_edge]
                
            to_visited_weight = {}
            for node in nodes_toVisited:
                if distances[node] is None:
                    continue
                to_visited_weight[node] = sum([edge.weight[2] for edge in distances[node]])

            current_node = min(to_visited_weight, key=lambda node: to_visited_weight[node])
            visited += [current_node]
            nodes_toVisited.remove(current_node)
        
        return (
            [edge.src for edge in distances[dest]], # nodes
            distances[dest] # edges
        )