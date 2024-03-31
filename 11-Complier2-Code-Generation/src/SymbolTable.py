class SymbolTable:
    """
    The SymbolTable class creates and maintains the correspondence between symbolic labels and numeric addresses.
    """
    def __init__(self):
        """
        Creates a new symbol table.
        """
        self._table = {}
        self._varCount = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def startSubroutine(self):
        """
        Starts a new subroutine scope (i.e. erases all names in the previous subroutine scope.)
        """
        self._subTable = {}
        self._varCount["ARG"] = 0
        self._varCount["VAR"] = 0

    def define(self, name, type, kind):
        """
        Defines a new identifier of a given name, type, and kind and assigns it a running index.
        STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope."""
        kind = kind.upper()
        if kind == "STATIC" or kind == "FIELD":
            self._table[name] = {
                'type': type,
                'kind': kind,
                'index': self.varCount(kind)
            }
        elif kind == "ARG" or kind == "VAR":
            assert self._subTable is not None
            self._subTable[name] = {
                'type': type,
                'kind': kind,
                'index': self.varCount(kind)
            }
        else:
            raise Exception("Invalid kind: {}".format(kind))
        self._varCount[kind] += 1

    def varCount(self, kind):
        """
        Returns the number of variables of the given kind already defined in the current scope.
        """
        return self._varCount[kind]

    def kindOf(self, name):
        """
        Returns the kind of the named identifier in the current scope.
        If the identifier is unknown in the current scope, returns NONE.
        """
        if name in self._table.keys():
            return self._table[name]['kind']
        elif name in self._subTable.keys():
            return self._subTable[name]['kind']
        else:
            return None

    def typeOf(self, name):
        """
        Returns the type of the named identifier in the current scope.
        """
        if name in self._table.keys():
            return self._table[name]['type']
        elif name in self._subTable.keys():
            return self._subTable[name]['type']
        else:
            return None

    def indexOf(self, name):
        """
        Returns the index assigned to named identifier.
        """
        if name in self._table.keys():
            return self._table[name]['index']
        elif name in self._subTable.keys():
            return self._subTable[name]['index']
        else:
            return None