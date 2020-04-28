"""pyparsing parser for GRASP .tor files"""

import pprint

import pyparsing as pp

LPAREN, RPAREN, COLON, COMMA = map(pp.Suppress, "():,")

identifier = pp.Word(pp.alphas, pp.alphanums + "_")
tor_comment = pp.OneOrMore(pp.dblSlashComment)


def comment_handler(input_string, locn, tokens):
    tokenstr = "\n".join(tokens)
    print(tokens)
    mod_string = "comment{:d} comment\n(\n{:s}\n)".format(locn, tokenstr)
    mod_def = pp.Dict(pp.Group(identifier.setResultsName("_name") + identifier.setResultsName("_type") + LPAREN + pp.Group(
        pp.OneOrMore(pp.dblSlashComment)).setResultsName("text") + RPAREN))
    return mod_def.parseString(mod_string)


tor_comment.setParseAction(comment_handler)
tor_comment.setResultsName("_name")
tor_comment.setResultsName("_type")

tor_string = pp.dblQuotedString() | pp.Word(pp.alphas, pp.alphanums + "_-.")
number = pp.pyparsing_common.number()

tor_members = pp.Forward()
tor_value = pp.Forward()

tor_struct = pp.Literal("struct").setResultsName("_type") + LPAREN + pp.Dict(tor_members) + RPAREN
tor_sequence = pp.Literal("sequence").setResultsName("_type") + LPAREN + pp.delimitedList(tor_value) + RPAREN
tor_ref = pp.Literal("ref").setResultsName("_type") + LPAREN + identifier + RPAREN
tor_value << (tor_sequence | tor_ref | tor_struct | tor_string | pp.Group(number + identifier) | number)

member_def = pp.Dict(pp.Group(identifier + COLON + tor_value))
tor_members << pp.delimitedList(member_def)

object_def = pp.Group(identifier.setResultsName("_name") + identifier.setResultsName("_type") + pp.Dict(
    LPAREN + pp.Optional(tor_members) + RPAREN))
tor_object = pp.Dict(object_def | tor_comment)
tor_file = pp.Dict(pp.OneOrMore(tor_object)) + pp.stringEnd

if __name__ == "__main__":
    print("\nTest Comments")
    comment_test = """
//DO NOT MODIFY OBJECTS BELOW THIS LINE.
//THESE OBJECTS ARE CREATED AND MANAGED BY THE
//GRAPHICAL USER INTERFACE AND SHOULD NOT BE
//MODIFIED MANUALLY!
"""
    print(comment_test)
    res = tor_comment.parseString(comment_test)
    pprint.pprint(res.asDict())

    print("\nTest Sequences")
    seq_test = """sequence(180.0 GHz,190.0 GHz,200.0 GHz,210.0 GHz,220.0 GHz,230.0 GHz,240.0 GHz,250.0 GHz,
260.0 GHz)
"""
    print(seq_test)
    res = tor_sequence.parseString(seq_test)
    pprint.pprint(res.asList())
    pprint.pprint(res.asDict())

    print("\nTest Members")
    member_test = """x : 0.0 mm, y : 0.0 mm, z : 0.0 mm
"""
    print(member_test)
    res = tor_members.parseString(member_test)
    pprint.pprint(res.asList())
    pprint.pprint(res.asDict())

    print("\n\nTest File String")
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
    print(test_str)
    results = tor_file.parseString(test_str)
    print("\nTest File as List")
    pprint.pprint(results.asList())
    print("\nTest File as Dict")
    pprint.pprint(results.asDict())
