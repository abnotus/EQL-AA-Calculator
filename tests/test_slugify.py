# -*- coding: utf-8 -*-
# slugify (wiki-sync/common.py) only stripped the straight apostrophe
# (U+0027), not the curly "smart apostrophe" (U+2019) a wiki CMS's
# auto-formatting commonly substitutes for one. Untouched, that character
# falls into slugify's [^a-z0-9]+ catch-all and becomes a literal "-"
# instead of vanishing - so the same logical name (e.g. "Osi's Coif")
# slugifies differently depending only on which apostrophe glyph the wiki
# page happens to use that day. A future resync landing on the "wrong"
# glyph would compute a new slug for an AA whose id was assigned under the
# old one, orphaning that id exactly like a real rename (see
# test_assign_aa_ids.py's header) - except unlike a real rename, nothing
# about the AA actually changed, so no one would think to look for this.
#
# src/keys.js's own slugify must stay byte-for-byte equivalent by hand
# (this file's docstring explains why the two can't share code) - this
# only exercises the Python side; the JS side has no live data to trigger
# it against yet, so its correctness here rests on reading the two
# functions side by side rather than a browser test.
import sys, importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "wiki-sync"))
spec = importlib.util.spec_from_file_location("common", REPO / "wiki-sync" / "common.py")
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)

straight = common.slugify("Osi's Coif")
curly = common.slugify("Osi’s Coif")
print(f"straight apostrophe: {straight!r}")
print(f"curly apostrophe:    {curly!r}")
assert straight == "osis-coif", f"FAIL: unexpected baseline slug for the straight apostrophe - got {straight!r}"
assert curly == straight, (
    f"FAIL: a curly apostrophe must slugify identically to a straight one, "
    f"got {curly!r} vs {straight!r}"
)
print("PASS: curly and straight apostrophes slugify identically")

# A left single quotation mark (U+2018) is the same character class, even
# though a possessive apostrophe is realistically always the right-hand
# form (U+2019) - both are stripped the same way as the straight quote.
left_curly = common.slugify("Osi‘s Coif")
assert left_curly == straight, f"FAIL: a left curly quote should also strip cleanly - got {left_curly!r}"
print("PASS: the left curly quotation mark strips the same way")

print("ALL PASS")
