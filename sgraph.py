#! env python3

from collections import defaultdict
from collections import deque


class SGraph:
    """Compute path information for directed graphs with non-negative edge costs."""

    class NoSuchRoute(Exception):
        """Exception thrown by SGraph in route_distance"""
        pass

    # use Johnson's reweighting if we discover wormholes and have negative distances,
    #   else: Floyd–Warshall or Bellman–Ford depending on dist. of graphs
    def __init__(self, graph):
        """Make an SGraph.

        graph - an iterable of edges/arcs with costs as strings, e.g.
                'AB5' => edge from 'A' to 'B' of cost 5
        
        NOTE: edge costs must be non-negative
        """

        self.V = set()  # all vertices
        # optimize: use arrays and map idx <-> names, should we get much larger graphs
        # TODO pre-compute/cache all-pairs shortest paths? [dist for src == dest > 0]
        # self.A = defaultdict(dict)  # shortest-paths, lookup A[from][to] => dist
        self.G = defaultdict(dict)  # the graph, lookup G[from][to] to get direct distance (check for existence!)
                                    #   makes cases 1-5 quick & easy, but memory hog for much larger graphs
        for edge in graph:
            src, dest, cost = edge
            self.V.add(src)
            self.V.add(dest)
            self.G[src][dest] = cost

    def route_distance(self, route):
        """Compute the distance along a given route.
        
        route - an iterable of nodes as strings, e.g. ['A', 'B', 'C']
        """

        dist = 0
        src = route.pop(0)

        if src not in self.G:
            # don't return two diff types/meanings, throw exception instead. same below
            # TODO best impl?
            raise SGraph.NoSuchRoute('NO SUCH ROUTE')

        for city in route:
            if city not in self.G[src]:
                raise SGraph.NoSuchRoute('NO SUCH ROUTE')
            dist += self.G[src][city]
            src = city

        return dist

    def routes_with_criteria(self, src, target, criteria):
        """Return a list of routes that start at src, end at target, and meet the criteria.
        
        criteria - a callable returning True/False, accepting two args: stops, distance
                   stops - number of edges from src node to target node, e.g. 'ABC', if valid, is two stops
                   distance - sum of edge costs from src node to target node, e.g. 'AB' in graph 'AB5' is 5

        Nodes which fail the criteria will not be part of a particular path.
        """

        # BFS
        routes = []
        q = deque()  # <- [ ... ] <-
        stops = 0
        distance = 0  # not true for this app, but it works out in the conditional check
        q.append((src, stops, distance, [src]))

        while q:
            # this city, stops to this city, distance to this city, route to this city
            city, stops, distance, route = q.popleft()
            if target == city and distance:  # no self-loops!
                r = list(route)
                routes.append(r)
            for dest, cost in self.G[city].items():
                if criteria(stops + 1, distance + cost):
                    new_route = list(route)
                    new_route.append(dest)
                    q.append((dest, stops + 1, distance + cost, new_route))
        return routes

    def count_routes_max_distance(self, src, dest, max_distance):
        """Return the number of routes starting at src, ending at dest, with distance < max_distance.

        Convenience wrapper for routes_with_criteria.

        src - source node
        dest - destination node
        max_distance - the maximum sum of edge costs; the criteria is 'strictly less than'
        """

        criteria = lambda stops, distance: distance < max_distance  # inconsistent max, per test cases
        return len(self.routes_with_criteria(src, dest, criteria))

    def count_routes_max_stops(self, src, dest, max_stops):
        """Return the number of routes starting at src, ending at dest, with number of stops <= max_stops.

        Convenience wrapper for routes_with_criteria.

        src - source node
        dest - destination node
        max_stops - the maximum number of stops; the criteria is 'less than or equal to'

        Example: A three node route "ABC' has two stops.
        """

        criteria = lambda stops, distance: stops <= max_stops  # inconsistent max, per test cases
        return len(self.routes_with_criteria(src, dest, criteria))

    def count_routes_exact_stops(self, src, dest, num_stops):
        """Return the number of routes starting at src, ending at dest, with number of stops == max_stops.

        Convenience wrapper for routes_with_criteria.

        src - source node
        dest - destination node
        num_stops - the exact number of stops; the criteria is 'equal to'

        Example: A three node route "ABC' has two stops.
        """

        count = 0
        criteria = lambda stops, distance: stops <= num_stops  # inconsistent max, per test cases
        for route in self.routes_with_criteria(src, dest, criteria):
            if num_stops == len(route) - 1:
                count += 1
        return count

    def shortest_route(self, src, dest):
        """Return the smallest sum of edge costs starting at src, ending at dest (shortest path).

        src - source node
        dest - destination node
        """

        # Dijkstra with unusual start condition to prevent src -> src == 0 distance
        x_in = set()
        a = defaultdict(lambda: float('inf'))
        v = self.V.copy()

        for node, cost in self.G[src].items():
            a[node] = cost
            x_in.add(node)
            v.remove(node)

        while x_in != self.V:
            mn = float('inf')
            new = None
            for x in x_in:
                for node, cost in self.G[x].items():
                    if node in v:
                        if (a[x] + cost) < mn:  # optimize large/dense G with pri. q
                            mn = a[x] + cost
                            new = (x, node, cost)
            if new is None:
                break
            x, node, cost = new
            x_in.add(node)
            v.remove(node)
            a[node] = a[x] + cost
        return a[dest]
