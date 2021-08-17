
class Table:
    def __init__(self, name):
        raise NotImplementedError

class Field:
    def __init__(self, name):
        self.name = name
        self._parents = []
        self._children = []

        self._wanted = False
        self._needed = False
        self._available = False

    def set_wanted(self):
        self._wanted = True

    @property
    def descendents(self):
        for c in self._children:
            yield c
            yield from c.descendents

    @property
    def ancestors(self):
        for p in self._parents:
            yield p
            yield from p.ancestors

    @property
    def wanted(self):
        return self._wanted

    @property
    def needed(self):
        if self.wanted:
            return True

        for d in self.descendents:
            if d.wanted:
                return True
        return False

    @property
    def available(self):
        if self.needed:
            return True

        raise NotImplementedError
        for a in self.ancestors:
            if a.needed:
                return True
        return False

    def __str__(self):
        return f"{self.name}:\tWanted? {self.wanted}\tNeeded? {self.needed}"

def add_link(start, end, name = ""):
    start._children.append(end)
    end._parents.append(start)


def make_graph():
    raise NotImplementedError

def read_graph():
    raise NotImplementedError

a = Field("A")
b = Field("B")
add_link(a, b)
b.set_wanted()

print(a)
print([p.name for p in a._parents])
print([c.name for c in a._children])

print(b)
print([p.name for p in b._parents])
print([c.name for c in b._children])

print("done")
