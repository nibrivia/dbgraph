class Node:
    def __init__(self, name):
        self.name = name
        self._parents = []
        self._children = []

        self._wanted = False
        self._needed = False
        self._available = False



    def set_wanted(self):
        # raise NotImplementedError
        self._wanted = True
        self.set_needed()

    def set_needed(self):
        # raise NotImplementedError
        self._needed = True
        self.set_available()

    def set_available(self):
        self._available = True

    def check_available(self):
        raise NotImplementedError

    def add_child(self, child):
        self._children.append(child)
        child._parents.append(self)

    def add_parent(self, parent):
        parent.add_child(self)

    def rm_child(self, child):
        self._children.remove(child)
        child._parents.remove(self)

    def rm_parent(self, parent):
        parent.rm_child(self)

    @property
    def descendents(self):
        for d in self.get_descendents(ignore = set()):
            yield d

    @property
    def ancestors(self):
        for a in self.get_ancestors(ignore = set()):
            yield a

    def get_descendents(self, ignore = set()):
        children = []
        for c in self._children:
            if c in ignore:
                continue

            ignore.add(c)
            children.append(c)
            children.extend(c.get_descendents(ignore = ignore))
        return children

    def get_ancestors(self, ignore = set()):
        ancestors = []
        for p in self._parents:
            if p in ignore:
                continue

            ignore.add(p)
            ancestors.append(p)
            ancestors.extend(p.get_ancestors(ignore = ignore))
        return ancestors

    @property
    def wanted(self):
        return self._wanted

    @property
    def needed(self):
        return self._needed or self._wanted


    @property
    def available(self):
        return self._needed or self._wanted or self._available


    def __str__(self):
        return f"{self.name}:\n\tParents\t{[p.name for p in self._parents]}\n\tChilds\t{[c.name for c in self._children]}\n\tWanted?\t{self.wanted}\n\tNeeded?\t{self.needed}\n\tAvail?\t{self.available}"

class Field(Node):
    def set_aggregate_fn(self, fn_name):
        self.aggregate_fn = fn_name

    def set_wanted(self):
        super().set_wanted()
        self._wanted = True
        self.aggregate_fn = None

        if len(self._parents) == 1:
            self._parents[0].set_needed()
        else:
            raise NotImplementedError("This should come back with a user choice")

    def set_needed(self):
        super().set_needed()
        self.set_available()

    def set_available(self):
        if self._available:
            return

        self._available = True

        for c in self._children:
            c.check_available()

    def check_available(self):
        if self._available:
            return

        for p in self._parents:
            if p.available:
                self.set_available()





class ComputedField(Field):
    def __init__(self, nodes, fn_name = "fn"):
        name = f"({fn_name} {' '.join(n.name for n in nodes)})"
        super().__init__(name)
        self._params = nodes

        for n in nodes:
            self.add_parent(n)

    def set_wanted(self):
        super().set_wanted()
        self._wanted = True

        if len(self._parents) > len(self._params):
            raise NotImplementedError("This should come back with a user choice")
        else:
            for p in self._params:
                p.set_needed(p)

    def set_needed(self):
        if self._needed:
            return

        # print(f"  {self.name} -> needed")
        super().set_needed()

        for p in self._parents:
            p.set_needed()

    def check_available(self):
        if self._available:
            return

        # print(f"  {self.name} checking if it's available")

        # Check computation parameters
        params_available = True
        for p in self._params:
            if not p.available:
                params_available = False

        if params_available:
            self.set_available()

        # Check other parents
        for p in self._parents:
            if p in self._params:
                continue
            if p.available:
                self.set_available()




class Union(ComputedField):
    def __init__(self, nodes):
        name = f"(union {' '.join(n.name for n in nodes)})"
        super().__init__(nodes, "union")

        for n in nodes:
            self.add_parent(n)

