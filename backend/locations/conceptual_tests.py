"""Practice-graph routing checks. Run with: python -m unittest locations.conceptual_tests"""

import unittest
from unittest.mock import patch

from . import graph


class ConceptualGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.practice_graph = graph.load_practice_graph()

    def setUp(self):
        self.graph_patch = patch("locations.graph.get_graph", return_value=self.practice_graph)
        self.graph_patch.start()
        self.addCleanup(self.graph_patch.stop)

    def test_same_node_is_not_a_trip(self):
        self.assertIsNone(graph.find_route("node-a", "node-a"))

    def test_node_b_to_d_is_the_reverse_of_d_to_b(self):
        forward = graph.find_route("node-b", "node-d")
        reverse = graph.find_route("node-d", "node-b")
        self.assertEqual(forward["nodeIds"], list(reversed(reverse["nodeIds"])))

    def test_construction_is_skipped_for_a_to_b(self):
        route = graph.find_route("node-a", "node-b")
        self.assertEqual(route["nodeIds"], ["node-a", "node-c", "node-b"])

    def test_multiple_construction_edges_are_skipped_for_e_to_h(self):
        route = graph.find_route("node-e", "node-h")
        self.assertEqual(route["nodeIds"], ["node-e", "node-b", "node-c", "node-a", "node-h"])

    def test_y_is_unreachable_because_construction_blocks_every_route(self):
        self.assertIsNone(graph.find_route("node-e", "node-y"))
        self.assertTrue(graph.construction_blocks_route("node-e", "node-y"))

    def test_z_is_unreachable_even_when_construction_is_ignored(self):
        self.assertIsNone(graph.find_route("node-a", "node-z"))
        self.assertFalse(graph.construction_blocks_route("node-a", "node-z"))


if __name__ == "__main__":
    unittest.main()
