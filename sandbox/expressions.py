# %%
from atopile import front_end, parse, assertions

# %%
def _build_test(code: str) -> front_end.Instance:
    parse.parser.cache["test"] = parse.parse_text_as_file(code)
    return front_end.lofty.get_instance("test:Test")

# %%
a = _build_test("""
module Test:
    signal a ~ pin 1
    b = 1 + 2
""")

# %%
a.assignments
# %%