
class Table:
    def __init__(self, name):
        self.name = name
        self._keys = []
        self.fields = []

    def add_key(self, new_key):
        self._keys.append(new_key)

    def add_field(self, field):
        self.fields.append(field)

    def add_fields(self, fs):
        for f in fs:
            self.add_field(f)

    def __str__(self):
        return f"Table <{self.name}>: {[k.name for k in self._keys]} -> {', '.join(f.name for f in self.fields)} "


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

    def add_child(self, child):
        self._children.append(child)
        child._parents.append(self)

    def add_parent(self, parent):
        parent.add_child(self)

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
        # this actually needs to be a back-and-forth expanding graph
        # maybe this is where the linear algebra comes in?
        raise NotImplementedError

        if self.needed:
            return True

        for a in self.ancestors:
            if a.needed:
                return True
        return False

    def __str__(self):
        return f"{self.name}:\n\tParents\t{[p.name for p in self._parents]}\n\tChilds\t{[c.name for c in self._children]}\n\tWanted?\t{self.wanted}\n\tNeeded?\t{self.needed}"


def make_graph():
    raise NotImplementedError

def read_graph():
    raise NotImplementedError


user_table = Table("users")
user_id = Field("user_id")
user_name = Field("user_name")
user_email = Field("user_email")

user_table.add_key((user_id))
user_table.add_fields([user_id, user_name, user_email])

print(user_table)
print(user_id)
print(user_name)
print(user_email)


print("done")
