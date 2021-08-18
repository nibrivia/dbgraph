

class Node:
    def __init__(self, name):
        self.name = name
        self._parents = []
        self._children = []

        self._wanted = False
        self._needed = False
        self._available = False


    def update_status(self):
        something_changed = False
        if self._wanted:
            if not self._needed:
                self._needed = True
                something_changed = True

        if self._needed:
            if not self._available:
                self._available = True
                something_changed = True

        return something_changed

    def set_wanted(self):
        self._wanted = True
        self.update_status()

    def set_needed(self):
        self._needed = True
        self.update_status()

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
        self.update_status()
        if self._needed:
            return True

        for d in self.descendents:
            if d.wanted:
                return True
        return False

    @property
    def available(self):
        self.update_status()
        if self._available:
            return True

        # this actually needs to be a back-and-forth expanding graph
        # maybe this is where the linear algebra comes in?
        # raise NotImplementedError

        if self.needed:
            return True

        available = False
        for a in self._parents:
            if a.needed:
                return True
        return False

    def __str__(self):
        return f"{self.name}:\n\tParents\t{[p.name for p in self._parents]}\n\tChilds\t{[c.name for c in self._children]}\n\tWanted?\t{self.wanted}\n\tNeeded?\t{self.needed}\n\tAvail?\t{self.available}"




class Field(Node):
    pass



class ComputedField(Node):
    def __init__(self, nodes):
        name = f"(computed {' '.join(n.name for n in nodes)})"
        super().__init__(name)

        for n in nodes:
            self.add_parent(n)



class Union(Field):
    def __init__(self, nodes):
        name = f"(union {' '.join(n.name for n in nodes)})"
        super().__init__(name)

        for n in nodes:
            self.add_parent(n)




class Table(Node):
    def __init__(self, name):
        super().__init__(name)
        self._lock = False
        self._keys = []
        self.fields = []

    def add_key(self, new_key):
        self._lock = True
        self._keys.append(new_key)
        new_key.add_child(self)

    def add_field(self, field):
        assert not self._lock, "Table has already been locked"
        self.fields.append(field)
        self.add_child(field)

    def add_fields(self, fs):
        for f in fs:
            self.add_field(f)

    def __str__(self):
        return f"Table <{self.name}>:\t{[k.name for k in self._keys]} -> {', '.join(f.name for f in self.fields)}"




class Database:
    def __init__(self):
        self.tables = dict()
        self.fields = dict()
        self.fns = dict(union = Union)
        pass

    def __get_field_or_create(self, field_name):
        # Create if it doesn't exist
        if field_name not in self.fields:
            self.fields[field_name] = Field(field_name)

        return self.fields[field_name]

    def get_field(self, field_name):
        return self.fields[field_name]

    def add_computed_node(self, fn_name, field_names):
        fields = [self.get_field(n) for n in field_names]
        fieldClass = self.fns.get(fn_name, ComputedField)
        field = fieldClass(fields)

        for f in fields:
            f.add_child(field)

        self.fields[field.name] = field
        return field.name

    def add_table(self, tablename, field_names, key_names):
        for k in key_names:
            assert k in field_names, f"Error in creating table <{tablename}>: key name <{k}> not in fields <{field_names}>"

        table = Table(tablename)
        fields = [self.__get_field_or_create(fn) for fn in field_names]

        table.add_fields(fields)
        for f in fields:
            if f.name in key_names:
                table.add_key(f)

        self.tables[tablename] = table

    def get_plan_for_fields(self, fields):
        for f in fields:
            self.get_field(f).set_wanted()

        print(self)

    def __str__(self):
        db_string = ""
        for t in self.tables.values():
            db_string += f"[{t.name}]\n"
            for tf in t.fields:
                db_string += "  "

                if tf.wanted:
                    db_string += "\033[31m"
                elif tf.needed:
                    db_string += "\033[33m"
                elif tf.available:
                    db_string += "\033[32m"

                if tf in t._keys:
                    db_string += f"> "
                else:
                    db_string += f"  "

                db_string += f"{tf.name} \t"

                db_string += "\033[0m\n"

            db_string += "\n"
        return db_string


if __name__ == "__main__":
    db = Database()
    db.add_table("users", ["user_id", "user_first", "user_last", "user_email"], ["user_id", "user_email"])
    db.add_computed_node("paste", ["user_first", "user_last"])
    db.add_table("lessons", ["lesson_id", "course_id", "lesson_name"], ["lesson_id"])
    db.add_table("courses", ["course_id", "course_name"], ["course_id"])
    user_and_lesson = db.add_computed_node("union", ["user_id", "lesson_id"])
    db.add_table("lesson_state", [user_and_lesson, "lesson_state"], [user_and_lesson])

    db.get_plan_for_fields(["course_name"])

    print("done")
