# GraspTorParser.py
# 
# pyparsing parser for GRASP .tor files

from pyparsing import *
import pprint

tor_bnf = """
file
    ( object )
    ( dblSlashComment )
object type
    ( members ) 
    ()
dblSlashComment
    string
members 
    name : struct
    name : ref
    name : sequence
    name : value
    members , name : value 
sequence 
    sequence( members )
    sequence()
struct
    struct( members )
    struct()
ref
    ref( name )
    ref()
name
    string
type
    string
value 
    string
    number
    number string
"""

LPAREN, RPAREN, COLON, COMMA = map(Suppress, "():,")

identifier = Word(alphas, alphanums + "_")
torComment = OneOrMore(dblSlashComment)

def commentHandler(inputString, locn, tokens):
    tokenstr = "\n".join(tokens)
    modString = "comment{:d} comment\n(\n{:s}\n)".format(locn, tokenstr)
    modDef = Dict(Group(identifier.setResultsName("_name") + identifier.setResultsName("_type") + LPAREN + Group(OneOrMore(dblSlashComment)).setResultsName("text") + RPAREN))
    return modDef.parseString(modString)

torComment.setParseAction(commentHandler)
torComment.setResultsName("_name")
torComment.setResultsName("_type")

torString = dblQuotedString().setParseAction(removeQuotes)
number = pyparsing_common.number()

torMembers = Forward()
torValue = Forward()

torStruct = Literal("struct").setResultsName("_type") + LPAREN + Dict(torMembers) + RPAREN
torSequence = Literal("sequence").setResultsName("_type") + LPAREN + delimitedList( torValue ) + RPAREN
torRef = Literal("ref").setResultsName("_type") + LPAREN + identifier + RPAREN
torValue << (torSequence | torRef | torStruct | torString | Group(number + identifier) | number )

memberDef = Dict(Group(identifier + COLON + torValue))
torMembers << delimitedList(memberDef)

objectDef = Group(identifier.setResultsName("_name") + identifier.setResultsName("_type") + Dict(LPAREN + Optional(torMembers) + RPAREN))
torObject = Dict(objectDef | torComment)
torFile = Dict(OneOrMore(torObject)) + stringEnd

test_str = """Primary_coor  coor_sys  
(
  origin           : struct(x : 0.0 mm, y : 0.0 mm, z : 0.0 mm)
)
 
Primary_M1  reflector  
(
  coor_sys         : ref(Primary_coor),
  surface          : ref(Primary_Surface),
  rim              : ref(Primary_Rim),
  centre_hole_radius : 175.0 mm
)

Primary_Surface  paraboloid  
(
  focal_length     : 2520.0 mm,
  vertex           : struct(x: 0.0 mm, y: 0.0 mm, z: 0.0 mm)
)

Primary_Rim  elliptical_rim  
(
  centre           : struct(x: 0.0 mm, y: 0.0 mm),
  half_axis        : struct(x: 3000.0 mm, y: 3000.0 mm)
)
 
Subreflector_M2  reflector  
(
  coor_sys         : ref(Secondary_coor),
  surface          : ref(Secondary_Surface),
  rim              : ref(Secondary_Rim),
  centre_hole_radius : 0.0 mm
)
 
Secondary_coor  coor_sys  
(
  origin           : struct(x: 0.0 mm, y: 0.0 mm, z: 2520.0 mm),
  y_axis           : struct(x: 0.0, y: -1.0, z: 0.0),
  base             : ref(Primary_coor)
)
 
Secondary_Surface  hyperboloid  
(
  vertex_distance  : 4702.053 mm,
  foci_distance    : 4992.927 mm
)

//DO NOT MODIFY OBJECTS BELOW THIS LINE.
//THESE OBJECTS ARE CREATED AND MANAGED BY THE
//GRAPHICAL USER INTERFACE AND SHOULD NOT BE
//MODIFIED MANUALLY!

Secondary_Rim  elliptical_rim  
(
  centre           : struct(x: 0.0 mm, y: 0.0 mm),
  half_axis        : struct(x: 175.0 mm, y: 175.0 mm)
)
 
Frequencies  frequency  
(
  frequency_list   : sequence(180.0 GHz,190.0 GHz,200.0 GHz,210.0 GHz,220.0 GHz,230.0 GHz,240.0 GHz,250.0 GHz,
260.0 GHz)
)"""

if __name__ == "__main__":
    print("\nTest Comments")
    commentTest = """
//DO NOT MODIFY OBJECTS BELOW THIS LINE.
//THESE OBJECTS ARE CREATED AND MANAGED BY THE
//GRAPHICAL USER INTERFACE AND SHOULD NOT BE
//MODIFIED MANUALLY!
"""
    print(commentTest)
    res = torComment.parseString(commentTest)
    pprint.pprint(res.asDict())
    
    print("\nTest Sequences")
    seqTest = """sequence(180.0 GHz,190.0 GHz,200.0 GHz,210.0 GHz,220.0 GHz,230.0 GHz,240.0 GHz,250.0 GHz,
260.0 GHz)
"""
    print(seqTest)
    res = torSequence.parseString(seqTest)
    pprint.pprint(res.asList())
    pprint.pprint(res.asDict())
    
    print("\nTest Members")
    memberTest = """x : 0.0 mm, y : 0.0 mm, z : 0.0 mm
"""
    print(memberTest)
    res = torMembers.parseString(memberTest)
    pprint.pprint(res.asList())
    pprint.pprint(res.asDict())
    
    print("\n\nTest File String")
    print(test_str)
    results = torFile.parseString(test_str)
    print("\nTest File as List")
    pprint.pprint(results.asList())
    print("\nTest File as Dict")
    pprint.pprint(results.asDict())
    