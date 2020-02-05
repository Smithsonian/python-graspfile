# torparser.py
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
tor_comment = OneOrMore(dblSlashComment)


def comment_handler(input_string, locn, tokens):
    tokenstr = "\n".join(tokens)
    mod_string = "comment{:d} comment\n(\n{:s}\n)".format(locn, tokenstr)
    mod_def = Dict(Group(identifier.setResultsName("_name") + identifier.setResultsName("_type") + LPAREN + Group(
        OneOrMore(dblSlashComment)).setResultsName("text") + RPAREN))
    return mod_def.parseString(mod_string)


tor_comment.setParseAction(comment_handler)
tor_comment.setResultsName("_name")
tor_comment.setResultsName("_type")

tor_string = dblQuotedString().setParseAction(removeQuotes)
number = pyparsing_common.number()

tor_members = Forward()
tor_value = Forward()

tor_struct = Literal("struct").setResultsName("_type") + LPAREN + Dict(tor_members) + RPAREN
tor_sequence = Literal("sequence").setResultsName("_type") + LPAREN + delimitedList(tor_value) + RPAREN
tor_ref = Literal("ref").setResultsName("_type") + LPAREN + identifier + RPAREN
tor_value << (tor_sequence | tor_ref | tor_struct | tor_string | Group(number + identifier) | number)

member_def = Dict(Group(identifier + COLON + tor_value))
tor_members << delimitedList(member_def)

object_def = Group(identifier.setResultsName("_name") + identifier.setResultsName("_type") + Dict(
    LPAREN + Optional(tor_members) + RPAREN))
tor_object = Dict(object_def | tor_comment)
tor_file = Dict(OneOrMore(tor_object)) + stringEnd

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
    res = tor_comment.parseString(commentTest)
    pprint.pprint(res.asDict())

    print("\nTest Sequences")
    seqTest = """sequence(180.0 GHz,190.0 GHz,200.0 GHz,210.0 GHz,220.0 GHz,230.0 GHz,240.0 GHz,250.0 GHz,
260.0 GHz)
"""
    print(seqTest)
    res = tor_sequence.parseString(seqTest)
    pprint.pprint(res.asList())
    pprint.pprint(res.asDict())

    print("\nTest Members")
    memberTest = """x : 0.0 mm, y : 0.0 mm, z : 0.0 mm
"""
    print(memberTest)
    res = tor_members.parseString(member_test)
    pprint.pprint(res.asList())
    pprint.pprint(res.asDict())

    print("\n\nTest File String")
    print(test_str)
    results = tor_file.parseString(test_str)
    print("\nTest File as List")
    pprint.pprint(results.asList())
    print("\nTest File as Dict")
    pprint.pprint(results.asDict())
