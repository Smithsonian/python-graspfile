# A class to hold a parsed GRASP Tor File in a collection of objects
#
# Paul Grimes, 2018
#
# The data from the Tor file will be parsed by a pyparsing parser defined in GraspTorParser
# and stored in a GraspTorFile class derived from collections.OrderedDict, containing
# GraspTorObjects and Comments.

import GraspTorParser
from collections import OrderedDict

_debug_ = True

class GraspTorValue:
    """A container for values from GraspTorMember objects"""
    def __init__(self, torValue=None):
        self.value = None
        self.unit = None
        if torValue:
            self.fill(torValue)
    def fill(self, torValue):
        if _debug_:
            print("GraspTorValue.fill received: {:}".format(torValue))
            
        try:
            if len(torValue[0]) > 1:
                self.value = torValue[0][0]
                self.unit = torValue[0][1]
            else:
                self.value = torValue[0]
        except TypeError:
            self.value = torValue[0]

class GraspTorMember:
    """A container for the member parameter of an GraspTorObject """
    def __init__(self, torMember=None):
        self.name = None
        self._value = None
        if torMember:
            self.fill(torMember)
            
    def fill(self, torMember):
        if _debug_:
            print("GraspTorMember.fill received: {:}".format(torMember))
    
        self.name = torMember[0]
        if torMember._type == "struct":
            self._value = GraspTorStruct(torMember[1:])
            self._type = "struct"
        elif torMember._type == "ref":
            self._value = GraspTorRef(torMember[1:])
            self._type = "ref"
        elif torMember._type == "sequence":
            self._value = GraspTorSequence(torMember[1:])
            self._type = "sequence"
        else:
            self._value = GraspTorValue(torMember[1:])
            self._type = "value"
            
    @property
    def value(self):
        """Short circuit through torValue to supply tV.value if it is a simple value"""
        if self._type == "value":
            return self._value.value
        else:
            return self._value
            
    @value.setter
    def value(self, newVal):
        if self._type == "value":
            if isinstance(newVal, GraspTorValue):
                self._value = newVal
            else:
                self._value.value = newVal
        else:
            self._value = newVal
            
    @property
    def unit(self):
        """Short circuit through torValue to supply tV.unit if appropriate, else retun None"""
        if self._type == "value":
            return self._value.unit
        else:
            return None
    @unit.setter        
    def unit(self, newUnit):
        if self._type == "value":
                self._value.unit = newUnit
        else:
            pass
                
    def __getitem__(self, key):
        return self.value[key].value
        
    def __setitem__(self, key, newValue):
        self.value[key].value = newValue
        
        
class GraspTorRef:
    """A container for a value that is a reference to another GraspTorObject"""
    def __init__(self, torRef=None):
        self.ref = None
        if torRef:
            self.fill(torRef)
            
    def fill(self, torRef):
        if _debug_:
            print("GraspTorRef.fill received: {:}".format(torRef))
        self.ref = torRef[1]
        

class GraspTorSequence(list):
    """A container for a value that is a sequence of GraspTorValues"""
    def __init__(self, torSeq=None):
        if torSeq:
            self.fill(torSeq)
            
    def fill(self, torSeq):
        if _debug_:
            print("GraspTorSequence.fill received: {:}".format(torSeq))

        for t in torSeq[1:]:
            self.append(GraspTorValue(t))
            
            
class GraspTorStruct(OrderedDict):
    """A container for a GraspTorStruct, that has a number of members.  Members are
    stored as an OrderedDict."""
    def __init__(self, torStruct=None):
        OrderedDict.__init__(self)
        if torStruct:
            self.fill(torStruct)
        else:
            pass
        
    def fill(self, torStruct):
        """Fill the GraspTorObject using the pyparsing results"""
        if _debug_:
            print("GraspTorStruct.fill received: {:}".format(torStruct))

        for t in torStruct[1:]:
            self[t[0]] = GraspTorMember(t)
            

class GraspTorComment:
    """A container for comments from a GraspTorFile"""
    def __init__(self, torComment=None):
        self.name = None
        self.text = None
        self.location = None
        if torComment:
            self.fill(torComment)
            
    def fill(self, torComment):
        if _debug_:
            print("GraspTorComment.fill received: {:}".format(torComment))
        self.name = torComment._name
        self.location = int(torComment._name.lstrip("comment"))
        self.text = torComment.text

        
class GraspTorObject(OrderedDict):
    """A container for a GraspTorObject, that has a name, a type and a number of members.  Members are
    stored as an OrderedDict."""
    def __init__(self, torObj=None):
        OrderedDict.__init__(self)
        if isinstance(torObj, str):
            self.readStr(torObj)
        elif isinstance(torObj, GraspTorParser.ParseResults):
            self.fill(torObj)
        else:
            pass
            
    def readStr(self, torStr):
        """Read the contents of the string into a torObject and then process the results"""
        res = GraspTorParser.torObjects.parseString(torStr)
        self.fill(res)
        
    def fill(self, torObj):
        """Fill the GraspTorObject using the pyparsing results"""
        if _debug_:
            print("GraspTorObject.fill received: {:}".format(torObj))
        
        self._name = torObj._name
        self._type = torObj._type
        for r in torObj[2:]:
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
