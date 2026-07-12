import copy

import networkx as nx
from database.DAO import DAO


class Model:
    def __init__(self):
        self._graph = nx.Graph()
        self._directors = []
        self._bestGroup = []
        self._bestGrossIncome = 0.0

    def buildGraph(self, date_from, date_to):
        self._graph.clear()

        self._directors = DAO.getDirectorsInDateRange(date_from, date_to)

        # popolo ogni regista con i film diretti (e relativi generi/incassi) nel range scelto
        for director in self._directors:
            DAO.getMoviesForDirectorInRange(director, date_from, date_to)

        self._graph.add_nodes_from(self._directors)

        for i in range(len(self._directors)):
            for j in range(i + 1, len(self._directors)):
                r1 = self._directors[i]
                r2 = self._directors[j]

                common_genres = r1.get_genres() & r2.get_genres()
                if common_genres:
                    peso = len(common_genres)
                    self._graph.add_edge(r1, r2, weight=peso)




    def getDirectorWithMaxDegree(self):
        """Ritorna (regista, grado) del regista con grado (numero di archi) maggiore."""
        if len(self._graph.nodes) == 0:
            return None, 0

        max_degree = -1
        best_director = None
        for node, degree in self._graph.degree():
            if degree > max_degree:
                max_degree = degree
                best_director = node
        return best_director, max_degree

    def getDirectorWithMaxWeightSum(self):
        """Ritorna (regista, somma pesi) del regista con somma dei pesi degli archi incidenti maggiore."""
        if len(self._graph.nodes) == 0:
            return None, 0

        max_sum = -1
        best_director = None
        for node in self._graph.nodes:
            weight_sum = sum(
                self._graph[node][neighbor]["weight"]
                for neighbor in self._graph.neighbors(node)
            )
            if weight_sum > max_sum:
                max_sum = weight_sum
                best_director = node
        return best_director, max_sum

    def getTop5Edges(self):
        """
        Ritorna i 5 archi di peso maggiore come lista di tuple (r1, r2, peso), ordinati in
        modo decrescente di peso; in caso di parità, ordinamento alfabetico sul nome del
        primo regista e poi del secondo.
        """
        if len(self._graph.edges) == 0:
            return []

        edges_with_weights = [
            (u, v, self._graph[u][v]["weight"])
            for u, v in self._graph.edges
        ]

        edges_sorted = sorted(
            edges_with_weights,
            key=lambda x: (-x[2], x[0].Name, x[1].Name)
        )

        return edges_sorted[:5]

    def getBestGroup(self, starting_director, N):
        """
        Cerco un insieme di esattamente N registi tale che:
        - il primo regista è quello scelto dall'utente (starting_director);
        - ogni regista aggiunto dopo il primo è adiacente ad almeno uno dei registi già
          presenti nel gruppo;
        - non possono comparire nel gruppo due registi collegati da un arco di peso 1;
        - tra tutte le soluzioni ammissibili si massimizza l'incasso complessivo
          (worlwide_gross_income) dei film diretti dai registi selezionati.
        Ritorna (bestGroup, bestGrossIncome).
        """
        if starting_director not in self._graph.nodes:
            return [], 0.0

        self._bestGroup = []
        self._bestGrossIncome = 0.0

        parziale = [starting_director]
        self._ricorsione(parziale, N)

        return self._bestGroup, self._bestGrossIncome

    def _ricorsione(self, parziale, N):
        # condizione di terminazione: parziale è lunga N
        if len(parziale) == N:
            total_gross = self._getTotalGrossIncome(parziale)
            if total_gross > self._bestGrossIncome:
                self._bestGrossIncome = total_gross
                self._bestGroup = copy.deepcopy(parziale)
            return

        for candidate in self._graph.nodes:
            if candidate in parziale:
                # il regista è già stato selezionato, salto
                continue

            # il candidato deve essere adiacente ad almeno un regista già in parziale
            adjacent = any(
                self._graph.has_edge(candidate, existing)
                for existing in parziale
            )
            if not adjacent:
                continue

            # non deve esistere, verso nessun regista già in parziale, un arco di peso 1
            blocked = any(
                self._graph.has_edge(candidate, existing) and
                self._graph[candidate][existing]["weight"] == 1
                for existing in parziale
            )
            if blocked:
                continue

            parziale.append(candidate)
            self._ricorsione(parziale, N)
            parziale.pop()

    def _getTotalGrossIncome(self, directors):
        return sum(d.get_total_gross_income() for d in directors)

    def getNumNodi(self):
        return len(self._graph.nodes)

    def getNumEdges(self):
        return len(self._graph.edges)

    def getAllDirectors(self):
        return self._graph.nodes