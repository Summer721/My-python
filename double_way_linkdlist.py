class SingleNode:
    def __init__(self, value, prev=None, next=None):
        self.value = value
        self.next = next
        self.prev = prev

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class DoblueWayLinkList:
    def __init__(self):
        self.__head = None
        self.__tail = None

    def appendnode(self, value):
        current_node = SingleNode(value)
        prev_node = self.__tail

        if not prev_node:
            self.__head = current_node
        else:
            prev_node.next = current_node
            current_node.prev = prev_node
        self.__tail = current_node

    def iternodes(self, reverse=False):
        current = self.__tail if reverse else self.__head
        while current:
            yield current
            current = current.prev if reverse else current.next

    def pop(self):
        if self.__tail is None:
            raise Exception('None Type Error')
        tail = self.__tail
        prev = tail.prev
        if prev is None:
            self.__head = None
            self.__tail = None
        else:
            prev.next = None
            self.__tail = prev
        return tail.value

    def remove(self, index):
        pass

    def insert(self, index, value):
        if index < 0:
            raise Exception('Error.')
        current = None
        for i, node in enumerate(self.iternodes()):
            if i == index:
                current = node
                break
        if current is None:
            self.appendnode(value)
            return
        prev = current.prev
        newnode = SingleNode(value)

        if prev is None:
            self.__head = newnode
            newnode.next = current
            current.prev = newnode
            return

        prev.next = newnode
        newnode.prev = prev
        newnode.next = current
        current.prev = newnode

    def getitem(self, index):
        if index < 0:
            raise Exception("Less than 0")
        current = None
        for i, v in enumerate(self.iternodes()):
            if i == index:
                current = v
                break
        if current is not None:
            return current


l1 = DoblueWayLinkList()
l1.appendnode(3)
l1.appendnode(4)
l1.appendnode(5)
l1.appendnode(6)
l1.appendnode(7)

l1.insert(3,100)
for i in l1.iternodes():
    print(i)


