import sys
import time
import random
from collections import deque

# Classe pour représenter un graphe avec noms explicatifs et commentaires améliorés
def create_graph_from_file(filename):
    """
    Crée un graphe à partir d'un fichier d'entrée.
    Le fichier doit contenir une matrice de capacité et éventuellement une matrice de coûts.
    """
    try:
        with open(filename, 'r') as f:
            num_nodes = int(f.readline().strip())

            capacity = []
            for _ in range(num_nodes):
                line = f.readline().strip()
                if not line:
                    raise ValueError("Ligne vide rencontrée dans le fichier.")
                capacity.append(list(map(int, line.split())))

            # Lecture des coûts (si présents)
            cost = []
            for _ in range(num_nodes):
                line = f.readline().strip()
                if not line:
                    break
                cost.append(list(map(int, line.split())))

            # Validation des matrices
            if len(capacity) != num_nodes or any(len(row) != num_nodes for row in capacity):
                raise ValueError("La matrice des capacités n'est pas carrée ou invalide.")
            if cost and (len(cost) != num_nodes or any(len(row) != num_nodes for row in cost)):
                raise ValueError("La matrice des coûts n'est pas carrée ou invalide.")

            return num_nodes, capacity, cost if cost else None
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        sys.exit(1)

# Fonction pour afficher une matrice avec une mise en page claire
def display_matrix(matrix, title):
    """
    Affiche une matrice avec un titre.
    """
    print(f"\n{title}:")
    for row in matrix:
        print(' '.join(map(str, row)))

# Fonction pour générer un graphe aléatoire avec connexité garantie
def generate_random_graph(num_nodes):
    """
    Génère un graphe aléatoire connexe avec des capacités et des coûts.
    """
    capacity = [[0 if i == j else (random.randint(1, 100) if random.random() < 0.5 else 0) for j in range(num_nodes)] for i in range(num_nodes)]
    cost = [[0 if capacity[i][j] == 0 else random.randint(1, 100) for j in range(num_nodes)] for i in range(num_nodes)]

    # Garantie de connexité avec un DFS
    def is_connected():
        visited = [False] * num_nodes
        stack = [0]
        visited[0] = True

        while stack:
            node = stack.pop()
            for neighbor, cap in enumerate(capacity[node]):
                if cap > 0 and not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(neighbor)

        return all(visited)

    while not is_connected():
        capacity = [[0 if i == j else (random.randint(1, 100) if random.random() < 0.5 else 0) for j in range(num_nodes)] for i in range(num_nodes)]

    return capacity, cost

# Parcours en largeur (BFS) pour Ford-Fulkerson avec commentaires

def bfs(capacity, residual_graph, source, sink, parent):
    """
    Parcours en largeur pour trouver un chemin augmentant.
    """
    visited = [False] * len(capacity)
    queue = deque([source])
    visited[source] = True

    while queue:
        u = queue.popleft()

        for v, capacity_uv in enumerate(residual_graph[u]):
            if not visited[v] and capacity_uv > 0:
                queue.append(v)
                visited[v] = True
                parent[v] = u

                if v == sink:
                    return True

    return False

# Algorithme de Ford-Fulkerson avec noms de variables explicatifs
def ford_fulkerson(num_nodes, capacity, source, sink):
    """
    Implémentation de l'algorithme Ford-Fulkerson pour calculer le flot maximal.
    """
    residual_graph = [row[:] for row in capacity]
    parent = [-1] * num_nodes
    max_flow = 0

    while bfs(capacity, residual_graph, source, sink, parent):
        path_flow = float('Inf')
        v = sink

        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual_graph[u][v])
            v = parent[v]

        v = sink
        while v != source:
            u = parent[v]
            residual_graph[u][v] -= path_flow
            residual_graph[v][u] += path_flow
            v = parent[v]

        max_flow += path_flow

    return max_flow

# Algorithme pousser-réétiqueter avec noms améliorés et commentaires
def push_relabel(num_nodes, capacity, source, sink):
    """
    Implémentation de l'algorithme Push-Relabel pour le flot maximal.
    """
    height = [0] * num_nodes
    excess = [0] * num_nodes
    flow = [[0] * num_nodes for _ in range(num_nodes)]

    def push(u, v):
        send = min(excess[u], capacity[u][v] - flow[u][v])
        flow[u][v] += send
        flow[v][u] -= send
        excess[u] -= send
        excess[v] += send

    def relabel(u):
        min_height = float('Inf')
        for v in range(num_nodes):
            if capacity[u][v] - flow[u][v] > 0:
                min_height = min(min_height, height[v])
        height[u] = min_height + 1

    def discharge(u):
        while excess[u] > 0:
            for v in range(num_nodes):
                if capacity[u][v] - flow[u][v] > 0 and height[u] == height[v] + 1:
                    push(u, v)
                    break
            else:
                relabel(u)

    height[source] = num_nodes
    for v in range(num_nodes):
        if capacity[source][v] > 0:
            flow[source][v] = capacity[source][v]
            flow[v][source] = -capacity[source][v]
            excess[v] = capacity[source][v]
            excess[source] -= capacity[source][v]

    active = [i for i in range(num_nodes) if i != source and i != sink and excess[i] > 0]

    while active:
        u = active.pop(0)
        discharge(u)
        if excess[u] > 0:
            active.append(u)

    return sum(flow[source][v] for v in range(num_nodes))

# Algorithme de Bellman pour le flot à coût minimal avec messages clairs
def bellman_min_cost_flow(num_nodes, capacity, cost, source, sink, flow_value):
    """
    Implémentation de l'algorithme Bellman-Ford pour le flot à coût minimal.
    """
    residual_capacity = [row[:] for row in capacity]
    residual_cost = [row[:] for row in cost]
    flow = 0
    total_cost = 0

    while flow < flow_value:
        dist = [float('Inf')] * num_nodes
        parent = [-1] * num_nodes
        dist[source] = 0

        for _ in range(num_nodes - 1):
            for u in range(num_nodes):
                for v in range(num_nodes):
                    if residual_capacity[u][v] > 0 and dist[v] > dist[u] + residual_cost[u][v]:
                        dist[v] = dist[u] + residual_cost[u][v]
                        parent[v] = u

        # Détection de cycles négatifs
        for u in range(num_nodes):
            for v in range(num_nodes):
                if residual_capacity[u][v] > 0 and dist[v] > dist[u] + residual_cost[u][v]:
                    raise ValueError("Cycle de coûts négatifs détecté.")

        if dist[sink] == float('Inf'):
            break

        path_flow = float('Inf')
        v = sink
        while v != source:
            u = parent[v]
            path_flow = min(path_flow, residual_capacity[u][v])
            v = parent[v]

        flow += path_flow
        total_cost += path_flow * dist[sink]

        v = sink
        while v != source:
            u = parent[v]
            residual_capacity[u][v] -= path_flow
            residual_capacity[v][u] += path_flow
            residual_cost[v][u] = -residual_cost[u][v]
            v = parent[v]

    return flow, total_cost

# Programme principal avec messages utilisateur plus explicites
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 flot_max.py <filename> or 'random' for generated graph")
        sys.exit(1)

    input_type = sys.argv[1]

    if input_type == "random":
        num_nodes = int(input("Entrez le nombre de sommets: "))
        capacity, cost = generate_random_graph(num_nodes)
        display_matrix(capacity, "Matrice des Capacités")
    else:
        filename = input_type
        num_nodes, capacity, cost = create_graph_from_file(filename)

    display_matrix(capacity, "Matrice des Capacités")
    if cost:
        display_matrix(cost, "Matrice des Coûts")

    source = 0
    sink = num_nodes - 1

    print("\nChoisissez un algorithme:")
    print("1. Ford-Fulkerson")
    print("2. Pousser-Réétiqueter")
    print("3. Flot à Coût Minimal avec Bellman")
    choice = int(input("Entrez votre choix (1, 2 ou 3): "))

    try:
        if choice == 1:
            max_flow = ford_fulkerson(num_nodes, capacity, source, sink)
            print(f"Flot maximal avec Ford-Fulkerson: {max_flow}")
        elif choice == 2:
            max_flow = push_relabel(num_nodes, capacity, source, sink)
            print(f"Flot maximal avec Pousser-Réétiqueter: {max_flow}")
        elif choice == 3:
            if cost:
                flow_value = ford_fulkerson(num_nodes, capacity, source, sink) // 2
                flow, total_cost = bellman_min_cost_flow(num_nodes, capacity, cost, source, sink, flow_value)
                print(f"Flot à coût minimal: {flow}, Coût total: {total_cost}")
            else:
                print("La matrice des coûts n'est pas disponible pour cet algorithme.")
        else:
            print("Choix invalide.")
    except ValueError as e:
        print(f"Erreur : {e}")
