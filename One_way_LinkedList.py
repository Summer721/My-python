class SingleNode:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class LinkList:
    def __init__(self):
        self._head = None
        self._tail = None
        self.nodes = []

    def appendnode(self, value):
        node = SingleNode(value)
        prov = self._tail
        if not prov:
            self._head = node
        else:
            prov.next = node

        self.nodes.append(node)
        self._tail = node

    def iternode(self):
        current = self._head
        while current:
            yield current
            current = current.next



link = LinkList()
link.appendnode(3)
link.appendnode(4)
link.appendnode(5)
print(link.nodes)

for i in link.iternode():
    print(i)
