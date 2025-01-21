import networkx as nx
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, nodes=[], edges=[]):
        self.nodes = nodes
        self.edges = edges

    def show(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.nodes)
        for edge in self.edges:
            time = edge.weight[1] - edge.weight[0]
            G.add_edge(edge.src, edge.dest, weight=time.total_seconds())

        # Récupérer les poids pour les afficher
        edge_labels = nx.get_edge_attributes(G, 'weight')
        pos = nx.spring_layout(G)
        nx.draw(G, with_labels=True, font_weight='bold')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        plt.show()