"""A class to hold a parsed GRASP Tor File in a collection of objects"""

from collections import OrderedDict

import graspfile.torparser as torparser

_debug_ = False

# trick for py2/3 compatibility
if 'basestring' not in globals():
    basestring = str

"""List of acceptable GraspTorObject types"""
grasp_object_types = [""]


class GraspTorValue:
    """A container for values from GraspTorMember objects"""

    def __init__(self, tor_value="_None"):
        """Container for values within GraspTorMember, GraspTorStruct, and GraspTorSequence objects.

        Args:
            tor_value: a `pyparsing.ParseResults` object from a tor_value tokentcOK.
        """
        #: str: The value as a string
        self.value = None

        #: str: The unit of the value as a string
        self.unit = None

        if tor_value != "_None":
            self.fill(tor_value)

    def __repr__(self):
        """Return a useful string representation of the GraspTorValue object.

        Returns:
            string representation of GraspTorValue in format suitable for use in a .tor file."""
        if self.unit:
            return repr(self.value) + " " + self.unit
        else:
            if isinstance(self.value, basestring):
                return self.value
            else:
                return repr(self.value)

    def fill(self, tor_value):
        """Fills the GraspTorValue object from output by the parser.

        Args:
            tor_value: a `pyparsing.ParseResults` class output by the torparser module.
        """
        if _debug_:
            print("GraspTorValue.fill received: {:}".format(tor_value))

        try:
            if isinstance(tor_value, basestring):
                self.value = tor_value
            else:
                if len(tor_value) > 1:
                    self.value = tor_value[0]
                    self.unit = tor_value[1]
                else:
                    self.value = tor_value[0]
        except TypeError:
            if _debug_:
                print("TypeError caught for tor_value = {:}".format(tor_value))
            self.value = tor_value


class GraspTorMember:
    """A container for the member parameter of an GraspTorObject """

    def __init__(self, tor_member=None):
        self.name = None

        self._type = None

        self._value = None
        if tor_member:
            self.fill(tor_member)

    def __repr__(self):
        """Return a useful string representation of the GraspTorMember object."""
        return self._value.__repr__()

    def fill(self, tor_member):
        if _debug_:
            print("GraspTorMember.fill received: {:}".format(tor_member))

        self.name = tor_member[0]
        if len(tor_member) > 2:
            self._type = tor_member[1]
        else:
            self._type = "value"

        if self._type == "struct":
            self._value = GraspTorStruct(tor_member[1:])
        elif self._type == "ref":
            self._value = GraspTorRef(tor_member[1:])
        elif self._type == "sequence":
            self._value = GraspTorSequence(tor_member[1:])
        else:
            self._value = GraspTorValue(tor_member[1])

    @property
    def type(self):
        """Return the type of the GraspTorMember"""
        return self._type

    @property
    def value(self):
        """Short circuit through tor_value to supply tV.value if it is a simple value"""
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
        """Short circuit through tor_value to supply tV.unit if appropriate, else return None"""
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

    def __setitem__(self, key, new_value):
        self.value[key].value = new_value


class GraspTorRef:
    """A container for a value that is a reference to another GraspTorObject"""

    def __init__(self, tor_ref=None):

        #: str: Reference to another GraspTorObject
        self.ref = None
        if tor_ref:
            self.fill(tor_ref)

    def __repr__(self):
        """Return a useful string representation of the GraspTorRef object."""
        return "ref({:s})".format(self.ref)

    def fill(self, tor_ref):
        if _debug_:
            print("GraspTorRef.fill received: {:}".format(tor_ref))
        self.ref = tor_ref[1]


class GraspTorSequence(list):
    """A container for a value that is a sequence of GraspTorValues."""

    def __init__(self, tor_seq=None):
        super(GraspTorSequence, self).__init__()
        if tor_seq:
            self.fill(tor_seq)

    def __repr__(self):
        """Return a useful string representation of the GraspTorSequence object."""
        outstring = "sequence("
        for v in self:
            outstring += (repr(v)) + ","
        outstring = outstring[:-1] + ")"

        return outstring

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

    def __repr__(self):
        """Return a useful string representation of the GraspTorSequence object."""
        outstring = "struct("
        for v in iter(self.keys()):
            outstring += v + ": " + repr(self[v]) + ", "
        outstring = outstring[:-2] + ")"

        return outstring

    def fill(self, tor_struct):
        """Fill the GraspTorObject using the pyparsing results"""
        if _debug_:
            print("GraspTorStruct.fill received: {:}".format(tor_struct))

        for t in tor_struct[1:]:
            self[t[0]] = GraspTorMember(t)


class GraspTorComment:
    """A container for comments from a GraspTorFile"""

    def __init__(self, tor_comment=None):
        #: str: Name of comment object
        self.name = None

        #: str: The type of the object
        self._type = "comment"

        #: str: Test of the comment object
        self.text = None

        #: int: Line number that the comment appears in.
        self.location = None
        if tor_comment:
            self.fill(tor_comment)

    def __repr__(self):
        """Return the comment as // prefixed lines"""
        return "\n".join(self.text)

    def fill(self, tor_comment):
        if _debug_:
            print("GraspTorComment.fill received: {:}".format(tor_comment))
            print("with name: {:}".format(tor_comment[0]))
        self.name = tor_comment[0]
        self.location = int(self.name.lstrip("comment"))
        self.text = tor_comment[2]

    @property
    def type(self):
        """Return the type of the comment object as "commment"."""
        return self._type


class GraspTorObject(OrderedDict):
    """A container for a GraspTorObject, that has a name, a type and a number of members.  Members are
    stored as an OrderedDict."""

    def __init__(self, tor_obj=None):
        OrderedDict.__init__(self)
        self._name = None
        self._type = None

        if isinstance(tor_obj, str):
            self.read_str(tor_obj)
        elif isinstance(tor_obj, torparser.pp.ParseResults):
            self.fill(tor_obj)
        else:
            pass

    def __repr__(self):
        """Return a useful string representation of the GraspTorObject object."""
        if self.type == "comment":
            outstring = repr(self["comment"]) + "\n"
        else:
            memberstrings = []
            for k in iter(self.keys()):
                memberstrings.append(k + "   : " + repr(self[k]))

            memberstring = ",\n  ".join(memberstrings)

            outstring = """{:}  {:}
(
  {:}
)
    """.format(self._name, self._type, memberstring)

        return outstring

    def read_str(self, tor_str):
        """Read the contents of the string into a tor_object and then process the results"""
        res = torparser.tor_object.parseString(tor_str)
        self.fill(res)

    def fill(self, tor_obj):
        """Fill the GraspTorObject using the pyparsing results"""
        if _debug_:
            print("GraspTorObject.fill received: {:}".format(tor_obj))
            print("Type:", type(tor_obj))

        self._name = tor_obj[0]
        self._type = tor_obj[1]
        for r in tor_obj[2:]:
            if self._type == "comment":
                self["comment"] = GraspTorComment(tor_obj)
            else:
                self[r[0]] = GraspTorMember(r)

    @property
    def name(self):
        """Return the name of the GraspTorObject"""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set the name of the GraspTorObject"""
        self._name = new_name

    @property
    def type(self):
        """Return the type of the GraspTorObject"""
        return self._type

    @type.setter
    def type(self, new_type):
        """Set the type of the GraspTorObject. Checks that type is sane"""
        # if new_type in grasp_object_types:
        #     self._type = new_type
        # else:
        #     raise ValueError("Unknown type for a GraspTorObject")
        self._type = new_type


class GraspTorFile(OrderedDict):
    """A container for objects read from a tor file.  Subclasses OrderedDict to provide a dict of torObjects
     keyed by name, and sorted by insertion order"""

    def __init__(self, file_like=None):
        """Create a TorFile object, and if fileLike is specified, read the file"""
        OrderedDict.__init__(self)
        self._parser = torparser.tor_file
        if file_like:
            self.read(file_like)

    def __repr__(self):
        """Return a GRASP readable string for the GraspTorFile object"""
        outstring = ""
        for k in iter(self.keys()):
            outstring += repr(self[k]) + "\n"

        return outstring

    def read(self, file_like):
        """Read a list of torObjects and torComments from a fileLike object.  We use pyparsing.ParserElement's parseFile
        method, which can take either a file-like object or a filename to open.  If you wish to parse an existing string
        object, used StringIO to supply a file-like object containing the string."""
        # Parse the file
        res = self._parser.parseFile(file_like)

        # Turn the parse results into objects
        self.fill(res)

    def fill(self, tor_file):
        """Fill the GraspTorFile using the parser results in tor_file"""
        for r in tor_file:
            temp = GraspTorObject(r)
            self[temp.name] = temp
