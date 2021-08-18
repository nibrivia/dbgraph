from graph import Node

class Field(Node):
    def set_wanted(self):
        # print(f"  {self.name} -> wanted")
        super().set_wanted()
        self._wanted = True

        if len(self._parents) == 1:
            self._parents[0].set_needed()



    def set_needed(self):
        # print(f"  {self.name} -> needed")
        super().set_needed()
        self.set_available()

    def set_available(self):
        if self._available:
            return

        # print(f"  {self.name} -> available")
        #super().set_available()
        self._available = True

        for c in self._children:
            c.check_available()

    def check_available(self):
        if self._available:
            return

        # print(f"  {self.name} checking if it's available")
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

