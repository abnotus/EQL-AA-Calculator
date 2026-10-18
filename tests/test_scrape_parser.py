# -*- coding: utf-8 -*-
# wiki-sync/scrape_wiki.py's table parsing, against synthetic wikitext (no
# network). Kunark is likely to add AAs as a second table in a section or
# under a new sub-heading, and the parser used to miss both: it read only
# the first table per section, skipped any heading not in its map without
# a word, and let a "|- style=..." row separator swallow the next row.
import importlib.util, io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("scrape_wiki", os.path.join(HERE, "..", "wiki-sync", "scrape_wiki.py"))
scrape = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scrape)


def table(*rows, separator="|-"):
    body = "\n".join(f"{separator}\n| {name} || {ranks} || {costs} || {desc}" for name, ranks, costs, desc in rows)
    return "{| class=\"wikitable\"\n! Name !! Ranks !! Cost !! Description\n" + body + "\n|}"


PAGE = "\n".join([
    "Intro text.",
    "== General AAs ==",
    table(("Adamant Will", "4", "2/4/6/9", "Resist charm."), ("Combat Agility", "3", "2/4/6", "Avoid hits.")),
    "Some prose between tables.",
    table(("Second Table AA", "1", "5", "From a second table.")),
    "=== Kunark ===",
    table(("Kunark General AA", "2", "3/6", "Added under a sub-heading."), separator='|- style="background:#eee"'),
    table(("Styled Row One", "1", "1", "One."), ("Styled Row Two", "1", "2", "Two."), separator='|- style="color:red"'),
    "[[Category:AA]]",
    "== Bard Class AAs ==",
    table(("Jam Fest", "3", "2/4/6", "Songs.")),
    "== Kunark AAs ==",
    table(("Unmapped AA", "1", "1", "Nobody maps this heading.")),
    "== See also ==",
    "No table here.",
])

warnings = []
wiki = scrape.parse_sections(PAGE, warnings)
general = wiki.get("general", {})
print("general:", sorted(general))
print("warnings:", warnings)

for name in ("Adamant Will", "Combat Agility", "Second Table AA"):
    assert name in general, f"FAIL: {name} missing from General"
print("PASS: every table in a section is parsed, not just the first")

assert "Kunark General AA" in general, "FAIL: a sub-heading under General AAs should belong to General"
print("PASS: a sub-heading inherits its parent section's category")

assert "Styled Row One" in general and "Styled Row Two" in general, "FAIL: a styled row separator swallowed a row"
assert general["Styled Row Two"][0]["costs"] == ["2"], general["Styled Row Two"]
print("PASS: a '|- style=...' separator splits rows like a bare '|-'")

assert general["Styled Row Two"][0]["description"] == "Two.", "FAIL: trailing section content leaked into the last row"
assert wiki.get("class:Bard", {}).get("Jam Fest"), "FAIL: class sections should still parse"
assert all("Unmapped AA" not in b for b in wiki.values()), "FAIL: an unmapped section's rows were filed somewhere"
assert len(warnings) == 1 and "Kunark AAs" in warnings[0], f"FAIL: expected one warning for the unmapped table, got {warnings}"
assert "See also" not in " ".join(warnings), "FAIL: a section with no table shouldn't warn"
print("PASS: an unmapped section with a table is reported; one without a table isn't")

print("ALL PASS")
