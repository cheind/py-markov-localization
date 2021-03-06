import numpy as np
import math

from robots import transforms


class PoseNode:
    """Represents a graph node with positional information.

    A PoseNode may contain children which have positional information themselves. 
    A full graph of PoseNodes thus represents kinematic chains of hierarchical ordered
    elements. A hierarchical representation of position information is often useful 
    in robotics. Most of the objects in this libary inherit PoseNode and are therefore
    compositable in a hierarchical fashion.

    Attributes
    ----------
    name : string
        Name of this node.
    node_parent : PoseNode
        Parent of this node. None if root.
    node_children : dict
        Map of name to PoseNode for each child of this node.
    pose : 1x3 array
        Pose vector of this node with respect to parent frame.
    root_node : PoseNode
        Root of the tree
    transform_to_parent : 3x3 matrix
        Relative 3x3 transformation between this node and its parent.
    transform_from_parent : 3x3 matrix
        Relative 3x3 transformation between this node's parent and this node.
    transform_to_world : 3x3 matrix
        Relative 3x3 transformation between this node and the world frame.
    transform_from_world : 3x3 matrix
        Relative 3x3 transformation between this the world frame and this node.
    """

    def __init__(self, pose=[0,0,0], name=None, parent=None):
        """Create a PoseNode.

        Params
        ------
        name : string, optional
            Name of node. If not provided a unique name is generated
        pose : 1x3 array, optional
            Pose vector of this node representing x, y, phi.
        parent : PoseNode, optional
            Parent of this node. If provided registers this node as child at parent.
        """            
        
        self.name = name
        if self.name is None:
            import uuid            
            self.name = str(uuid.uuid4())

        self.node_parent = None        
        self.node_children = {}
        self.pose = np.asarray(pose, dtype=float)

        if parent is not None:
            parent.add_node(self)

    def add_node(self, node):
        """Add node as child of self.
        
        Params
        ------
        node : PoseNode
            Node to add
        """
        assert not node.name in self.node_children
        self.node_children[node.name] = node
        if node.node_parent is not None:
            node.node_parent.remove_node(node)        
        node.node_parent = self
    
    def remove_node(self, node):
        """Remove child node.

        Params
        ------
        node : PoseNode
            Node to be removed
        """
        del self.node_children[node.name]

    def __getitem__(self, name):
        """Returns a child node by name.

        The name may contain multiple occurances of '.' as path separator. I.e            
            node['a.b.c']
        has the same meaning as writing
            node['a']['b']['c']

        Params
        ------
        name : str
            Name of node

        Returns
        -------
        PoseNode
            PoseNode associated with given name
        """
        path = name.split('.')
        n = self
        for item in path:
            n = n.node_children[item]
        return n

    @property
    def root_node(self):
        n = self
        while n.node_parent is not None:
            n = n.node_parent
        return n

    @property
    def transform_to_parent(self):    
        return transforms.transform_from_pose(self.pose)

    @property
    def transform_from_parent(self):        
        return transforms.rigid_inverse(self.transform_to_parent)

    @property
    def transform_to_world(self):
        t = self.transform_to_parent
        n = self.node_parent
        while n is not None:
            t = np.dot(n.transform_to_parent, t)
            n = n.node_parent
        return t

    @property
    def transform_from_world(self):
        t = self.transform_to_world
        return transforms.rigid_inverse(t)

    def transform_to(self, target):
        """Returns the relative transformation between this node and `target` node."""
        if isinstance(target, PoseNode):
            t1 = self.transform_to_world
            t2 = target.transform_from_world
            return np.dot(t2, t1)
        elif isinstance(target, str):
            raise NotImplementedError

    def transform_from(self, node):
        """Returns the relative transformation between `target` node and this node."""
        t = self.transform_to(node)
        return transforms.rigid_inverse(t)
        
