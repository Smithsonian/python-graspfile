"""A class to hold a parsed GRASP Tor File in a collection of objects"""

import graspfile.torparser
from collections import OrderedDict

_debug_ = True


class GraspTorValue:
    """A container for values from GraspTorMember objects"""

    def __init__(self, tor_value=None):
        self.value = None
        self.unit = None
        if tor_value:
            self.fill(tor_value)

    def fill(self, tor_value):
        if _debug_:
            print("GraspTorValue.fill received: {:}".format(tor_value))

        try:
            if len(tor_value[0]) > 1:
                self.value = tor_value[0][0]
                self.unit = tor_value[0][1]
            else:
                self.value = tor_value[0]
        except TypeError:
            self.value = tor_value[0]


class GraspTorMember:
    """A container for the member parameter of an GraspTorObject """

    def __init__(self, tor_member=None):
        self.name = None
        self._value = None
        if tor_member:
            self.fill(tor_member)

    def fill(self, tor_member):
        if _debug_:
            print("GraspTorMember.fill received: {:}".format(tor_member))

        self.name = tor_member[0]
        if tor_member._type == "struct":
            self._value = GraspTorStruct(tor_member[1:])
            self._type = "struct"
        elif tor_member._type == "ref":
            self._value = GraspTorRef(tor_member[1:])
            self._type = "ref"
        elif tor_member._type == "sequence":
            self._value = GraspTorSequence(tor_member[1:])
            self._type = "sequence"
        else:
            self._value = GraspTorValue(tor_member[1:])
            self._type = "value"

    @property
    def value(self):
        """Short circuit through torValue to supply tV.value if it is a simple value"""
        if self._type == "value":
            return self._value.value
        else:
            return self._value

    @value.setter
    def value(self, new_val):
        if self._type == "value":
            if isinstance(new_val, GraspTorValue):
                self._value = new_val
            else:
                self._value.value = new_val
        else:
            self._value = new_val

    @property
    def unit(self):
        """Short circuit through torValue to supply tV.unit if appropriate, else retun None"""
        if self._type == "value":
            return self._value.unit
        else:
            return None

    @unit.setter
    def unit(self, new_unit):
        if self._type == "value":
            self._value.unit = new_unit
        else:
            pass

    def __getitem__(self, key):
        return self.value[key].value

    def __setitem__(self, key, newValue):
        self.value[key].value = newValue


class GraspTorRef:
    """A container for a value that is a reference to another GraspTorObject"""

    def __init__(self, tor_ref=None):
        self.ref = None
        if tor_ref:
            self.fill(tor_ref)

    def fill(self, tor_ref):
        if _debug_:
            print("GraspTorRef.fill received: {:}".format(tor_ref))
        self.ref = tor_ref[1]


class GraspTorSequence(list):
    """A container for a value that is a sequence of GraspTorValues"""
    def __init__(self, tor_seq=None):
        super().__init__()
        if tor_seq:
            self.fill(tor_seq)

    def fill(self, tor_seq):
        if _debug_:
            print("GraspTorSequence.fill received: {:}".format(tor_seq))

        for t in tor_seq[1:]:
            self.append(GraspTorValue(t))


class GraspTorStruct(OrderedDict):
    """A container for a GraspTorStruct, that has a number of members.  Members are
    stored as an OrderedDict."""
    def __init__(self, tor_struct=None):
        OrderedDict.__init__(self)
        if tor_struct:
            self.fill(tor_struct)
        else:
            pass

    def fill(self, tor_struct):
        """Fill the GraspTorObject using the pyparsing results"""
        if _debug_:
            print("GraspTorStruct.fill received: {:}".format(tor_struct))

        for t in tor_struct[1:]:
            self[t[0]] = GraspTorMember(t)


class GraspTorComment:
    """A container for comments from a GraspTorFile"""
    def __init__(self, tor_comment=None):
        self.name = None
        self.text = None
        self.location = None
        if tor_comment:
            self.fill(tor_comment)

    def fill(self, tor_comment):
        if _debug_:
            print("GraspTorComment.fill received: {:}".format(tor_comment))
        self.name = tor_comment.name
        self.location = int(tor_comment.name.lstrip("comment"))
        self.text = tor_comment.text


class GraspTorObject(OrderedDict):
    """A container for a GraspTorObject, that has a name, a type and a number of members.  Members are
    stored as an OrderedDict."""

    def __init__(self, tor_obj=None):
        OrderedDict.__init__(self)
        self._name = None
        self._type = None

        if isinstance(tor_obj, str):
            self.read_str(tor_obj)
        elif isinstance(tor_obj, GraspTorParser.ParseResults):
            self.fill(tor_obj)
        else:
            pass

    def read_str(self, tor_str):
        """Read the contents of the string into a torObject and then process the results"""
        res = GraspTorParser.torObjects.parseString(tor_str)
        self.fill(res)

    def fill(self, tor_obj):
        """Fill the GraspTorObject using the pyparsing results"""
        if _debug_:
            print("GraspTorObject.fill received: {:}".format(tor_obj))

        self._name = tor_obj._name
        self._type = tor_obj._type
        for r in tor_obj[2:]:
            self[r[0]] = GraspTorMember(r)


class GraspTorFile(OrderedDict):
    """A container for objects read from a tor file.  Subclasses OrderedDict to provide a dict of torObjects
     keyed by name, and sorted by insertion order"""

    def __init__(self, fileLike=None):
        """Create a TorFile object, and if fileLike is specified, read the file"""
        OrderedDict.__init__(self)
        self._parser = GraspTorParser.torFile
        if fileLike:
            self.read(fileLike)

    def read(self, fileLike):
        """Read a list of torObjects and torComments from a fileLike object.  We use pyparsing.ParserElement's parseFile
        method, which can take either a file-like object or a filename to open.  If you wish to parse an existing string
        object, used StringIO to supply a file-like object containing the string."""
        # Parse the file
        res = self._parser.parseFile(fileLike)

        # Turn the parse results into objects
        self.fill(res)

    def fill(self, torFile):
        """Fill the GraspTorFile using the parser results in torFile"""
        for r in torFile:
            if r._type == "comment":
                self[r._name] = GraspTorComment(r)
            else:
                self[r._name] = GraspTorObject(r)


if __name__ == "__main__":
    import StringIO

    testFile = StringIO.StringIO(GraspTorParser.test_str)

    gtf = GraspTorFile(testFile)

    print(gtf)
