
import numpy as np

from robots.grid import Grid
from robots.planning.astar import GridGraph
from robots.planning.astar import astar

def test_gridgraph():

    mask = np.zeros((10,10))
    mask[5, 5] = 1.
    grid = Grid(mask, [0,0], [10,10])
    graph = GridGraph(grid, lambda a,b: 1., lambda a,b: 0.)

    np.testing.assert_allclose(graph.neighbors([0,0]), [[1, 0], [0, 1]])
    np.testing.assert_allclose(graph.neighbors([9,9]), [[9, 8], [8, 9]])
    np.testing.assert_allclose(graph.neighbors([5,4]), [[5, 3], [6,4], [4,4]])

def test_astar():

    mask = np.array([
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ])
    grid = Grid(mask, [0,0], [6,5])
    graph = GridGraph(grid, lambda a,b: 1., lambda a,b: 0.)

    path = astar((0, 0), (4, 4), graph)
    np.testing.assert_allclose(path, [
        [0, 0],
        [0, 1],
        [0, 2],
        [0, 3],
        [0, 4],
        [1, 4],
        [2, 4],
        [3, 4],
        [4, 4]
    ]) # note, cells are [col, row] as points are [x, y]

    """
    import matplotlib.pyplot as plt
    from robots.draw import Drawer
    
    fig, ax = plt.subplots()
    ax.set_xlim([-10, 10])
    ax.set_ylim([-10, 10])
    ax.set_aspect('equal')

    d = Drawer()
    d.draw_grid(grid, ax)
    d.draw_points(np.array([[0,4],[0,4]]) + [[0.5],[0.5]], ax, fc='r')
    lines = np.asarray(path).T + [[0.5],[0.5]]
    d.draw_lines(lines.reshape(1,2,-1), ax)

    plt.show()
    """

def test_astar_nopath():

    mask = np.array([
        [0, 1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0]
    ])
    grid = Grid(mask, [0,0], [6,5])
    graph = GridGraph(grid, lambda a,b: 1., lambda a,b: 0.)

    def heuristic(node, goal):
        return 0.

    path = astar((0, 0), (2, 0), graph)
    np.testing.assert_allclose(path, [])