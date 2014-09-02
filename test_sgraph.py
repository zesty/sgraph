#! env python3

import unittest
import sgraph


class TestSgraph(unittest.TestCase):
    
    def setUp(self):
        graph = []
        with open('graph') as f:  # one per line FIXME fixture?
            for edge in f.readlines():
                src, dest, *cost = list(edge.strip())
                cost = int(''.join(cost))  # bc maybe size >= 10; FIXME multi-char cities needs diff input format
                graph.append((src, dest, cost))
        self.sgl = sgraph.SGraph(graph)

    def test01(self):
        self.assertEqual(9, self.sgl.route_distance(['A', 'B', 'C']))

    def test02(self):
        self.assertEqual(5, self.sgl.route_distance(['A', 'D']))

    def test03(self):
        self.assertEqual(13, self.sgl.route_distance(['A', 'D', 'C']))

    def test04(self):
        self.assertEqual(22, self.sgl.route_distance(['A', 'E', 'B', 'C', 'D']))

    def test05(self):
        self.assertRaises(sgraph.SGraph.NoSuchRoute, self.sgl.route_distance, ['A', 'E', 'D'])
        try:
            x = self.sgl.route_distance(['A', 'E', 'D'])
            print(str(x))  # never
        except sgraph.SGraph.NoSuchRoute as e:
            self.assertEqual('NO SUCH ROUTE', str(e))

    def test06(self):
        self.assertEqual(2, self.sgl.count_routes_max_stops('C', 'C', 3))

    def test07(self):
        self.assertEqual(3, self.sgl.count_routes_exact_stops('A', 'C', 4))

    def test08(self):
        self.assertEqual(9, self.sgl.shortest_route('A', 'C'))

    def test09(self):
        self.assertEqual(9, self.sgl.shortest_route('B', 'B'))

    def test10(self):
        self.assertEqual(7, self.sgl.count_routes_max_distance('C', 'C', 30))

    def test11(self):
        self.assertEqual(float('inf'), self.sgl.shortest_route('A', 'A'))


if __name__ == '__main__':
    unittest.main()
