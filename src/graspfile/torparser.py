"""pyparsing parser for GRASP .tor files"""

import pyparsing as pp

LPAREN, RPAREN, COLON, COMMA = map(pp.Suppress, "():,")

identifier = pp.Word(pp.alphas, pp.alphanums + "_")
tor_comment = pp.OneOrMore(pp.dblSlashComment)


def comment_handler(input_string, locn, tokens):
    tokenstr = "\n".join(tokens)
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
