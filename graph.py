from fields import Node, Field, Union, ComputedField



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

    def set_needed(self):
        if self._needed:
            return


        # print(f"  {self.name} -> needed")
        super().set_needed()

        # At least one key is already needed
        if not any(k.needed for k in self._keys):
            # Set all our keys to needed
            # TODO support multiple keys more cleanly
            for k in self._keys:
                k.set_needed()


        for f in self.fields:
            f.set_available()

    def set_available(self):
        if self._available:
            return

        # print(f"  {self.name} -> available")
        super().set_available()

        for c in self._children:
            c.check_available()


    def check_available(self):
        if self._available:
            return

        #print(f"  {self.name} checking if it's available")
        for k in self._keys:
            if k.available:
                self.set_available()



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
        if fn_name in self.fns:
            field = self.fns.get(fn_name)(fields)
        else:
            field = ComputedField(fields, fn_name)

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

    def to_csv(self):
        csv_string = "tablename, column, global_name, is_table_key, is_computed\n"
        for t in self.tables.values():
            seen_keys = set()
            for f in t._keys:
                seen_keys.add(f.name)
                csv_string += f"{t.name}, {f.name}, {f.name}, TRUE, {f.is_computed}\n"

            for f in t.fields:
                if f.name in seen_keys:
                    continue
                csv_string += f"{t.name}, {f.name}, {f.name}, FALSE, {f.is_computed}\n"

        return csv_string

    def __str__(self):
        db_string = ""
        seen_fields = set()
        for t in self.tables.values():
            if t.wanted:
                db_string += "\033[31m"
            elif t.needed:
                db_string += "\033[33m"
            elif t.available:
                db_string += "\033[32m"
            db_string += f"[{t.name}]\033[0m\n"

            for tf in t.fields:
                seen_fields.add(tf.name)
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

        fields = set(f for f in self.fields)
        fields = fields.difference(seen_fields)
        db_string += "[computed fields]\n"
        for f_name in fields:
            f = self.fields[f_name]
            db_string += "  "

            if f.wanted:
                db_string += "\033[31m"
            elif f.needed:
                db_string += "\033[33m"
            elif f.available:
                db_string += "\033[32m"

            db_string += f"  "

            db_string += f"{f.name} \t"

            db_string += "\033[0m\n"
        return db_string


if __name__ == "__main__":
    db = Database()
    db.add_table("users", ["user_id", "user_first", "user_last", "user_email"], ["user_id", "user_email"])
    db.add_computed_node("paste", ["user_first", "user_last"])
    db.add_table("lessons", ["lesson_id", "course_id", "lesson_name"], ["lesson_id"])
    db.add_table("courses", ["course_id", "course_name"], ["course_id"])
    user_and_lesson = db.add_computed_node("union", ["user_id", "lesson_id"])
    db.add_table("lesson_state", [user_and_lesson, "lesson_state"], [user_and_lesson])

    db.add_table("lesson_data", ["lesson_id", "n_viewed", "n_finished"], ["lesson_id"])
    db.add_computed_node("/", ["n_finished", "n_viewed"])



    db.get_plan_for_fields(["n_viewed"])

    print()
    # print(db.to_csv())
    print("done")
