# -*- coding: utf-8 -*-
# wiki-sync/common.py's data_integrity_problems, against synthetic
# data.src.js files: an AA the line parser can't see (written across two
# lines) would ship with no share-code id, and two names that slugify to
# the same key would share saves and an id. The build fails on either.
import importlib.util, io, os, sys, tempfile
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("common", os.path.join(HERE, "..", "wiki-sync", "common.py"))
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

HEADER = 'const CLASS_LIST = ["Bard"];\nconst AA_DATA = {\n'


def problems_for(body):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "data.src.js"
        path.write_text(HEADER + body + "};\n", encoding="utf-8")
        return common.data_integrity_problems(path)


clean = '''  general: [
    { name: "Adamant Will", ranks: 1, costs: ["1"], levelReq: "1", description: "x" },
    { name: "Combat Agility", ranks: 1, costs: ["1"], levelReq: "1", description: "x" }
  ],
  archetype: [],
  special: [],
  classes: {
    "Bard": [
      { name: "Jam Fest", ranks: 1, costs: ["1"], levelReq: "1", description: "x" }
    ]
  }
'''
assert problems_for(clean) == [], problems_for(clean)
print("PASS: a well-formed file has no problems")

multi_line = clean.replace(
    '{ name: "Combat Agility", ranks: 1,',
    '{\n      name: "Combat Agility", ranks: 1,')
found = problems_for(multi_line)
print("multi-line entry:", found)
assert len(found) == 1 and "Combat Agility" in found[0], found
print("PASS: an entry the line parser can't see is reported")

collision = clean.replace('"Combat Agility"', '"Adamant-Will"')
found = problems_for(collision)
print("slug collision:", found)
assert len(found) == 1 and "general::adamant-will" in found[0], found
print("PASS: two names sharing a slug are reported")

print("ALL PASS")
