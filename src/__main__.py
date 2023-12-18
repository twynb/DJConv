import formats.djuced
import formats.rekordbox
import argparse

allowed_formats = ["djuced", "rekordbox", "rb"]
parser_functions = {
    "djuced": formats.djuced.parse_db,
    "rekordbox": formats.rekordbox.parse_db,
}
writer_functions = {
    "djuced": formats.djuced.write_db,
    "rekordbox": formats.rekordbox.write_db,
}

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("-o", "--output")
parser.add_argument("-if", "--inputFormat")
parser.add_argument("-of", "--outputFormat")

args = parser.parse_args()
if not args.outputFormat or args.outputFormat not in allowed_formats:
    print("invalid or no output format specified!")
    exit(1)
if not args.inputFormat or args.inputFormat not in allowed_formats:
    print("invalid or no input format specified!")
    exit(1)

print("Parsing original database...")
lib = parser_functions[args.inputFormat](args.input)
print("Writing new database...")
writer_functions[args.outputFormat](args.output, lib)
print("Finished!")
