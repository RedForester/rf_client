from typing import Optional, Generator, List, Iterator, Callable, Dict
from rf_api_client.models.nodes_api_models import NodeTreeDto, NodeTreeBodyDto


SearchFunction = Callable[['NodeWrapper'], bool]


class NodeBodyWrapper(NodeTreeBodyDto):
    children: List['NodeWrapper']


class NodeWrapper(NodeTreeDto):
    """
    This class extend simple NodeTreeDto model to add properties and methods to traverse and search in given node tree.

    It is not recommended to create instances of this class manually due to internal tree lookup mechanism
    """

    # Crude private field implementation - https://github.com/samuelcolvin/pydantic/issues/655#issuecomment-585374936
    class __NodeInternalStorage:
        def __init__(self):
            self.node_index: Dict[str, 'NodeWrapper'] = None

    __slots__ = ('_internal_',)
    _internal_: __NodeInternalStorage

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, '_internal_', self.__NodeInternalStorage())

    body: NodeBodyWrapper

    @property
    def is_link(self):
        return self.id != self.body.id

    @property
    def parent_node(self):
        return self._internal_.node_index[self.parent]

    def get_all_descendants(self) -> Generator['NodeWrapper', None, None]:
        """
        Will yield nodes from the current branch in depth-first order
        """
        def dive(current: 'NodeWrapper'):
            yield current

            for node in current.body.children:
                yield from dive(node)

        return dive(self)

    def find(self, function: SearchFunction) -> Optional['NodeWrapper']:
        """
        Will find first node from current branch matched by search function
        """
        for node in self.get_all_descendants():
            if function(node):
                return node

    def find_all(self, function: SearchFunction) -> Iterator['NodeWrapper']:
        """
        Will find all nodes in current branch matched by search function
        """
        return filter(function, self.get_all_descendants())

    def find_ancestors(self, function: Optional[SearchFunction] = None) -> Generator['NodeWrapper', None, None]:
        """
        Will yield ancestor nodes from closest to farthest matched by search function if provided.
        If search function is omitted, will yield all ancestor nodes
        """
        current = self._internal_.node_index.get(self.parent)
        while current is not None:
            if function is None or function(current):
                yield current

            current = self._internal_.node_index.get(current.parent)

    def find_closest_ancestor(self, function: Optional[SearchFunction] = None) -> Optional['NodeWrapper']:
        """
        Return closest ancestor matched by search function if provided.
        If search function is omitted, will return closest ancestor (equal to `.parent_node` getter)
        """
        return next(self.find_ancestors(function), None)

    def get_siblings(self):
        """
        Return all nodes from the same level as current node (including current)
        """
        return self.parent_node.body.children


NodeBodyWrapper.update_forward_refs()


class TreeWrapper:
    """ Represent nodes tree. Every node will be wrapped by `NodeWrapper` """

    def __init__(self, tree: NodeTreeDto):
        self.root = NodeWrapper(**tree.dict(by_alias=True))
        self.node_index = {c.id: c for c in self.root.get_all_descendants()}

        for n in self.root.get_all_descendants():
            # noinspection PyProtectedMember
            n._internal_.node_index = self.node_index

    def find_by_id(self, id_: str) -> Optional[NodeWrapper]:
        """
        Return wrapped node by id
        """
        return self.node_index.get(id_)

    # todo create node
    # todo update node
    # todo delete node
    # todo new parent
    # todo move
    # todo copy
