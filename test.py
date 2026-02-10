import expand
import datetime


def test_ansible():

    class TestProbe(expand.CompatibilityProbe):
        def is_compatible(self) -> bool:
            return False

        def get_error_message(self) -> str:
            return "N/A"

    class TestProbe2(expand.CompatibilityProbe):
        def is_compatible(self) -> bool:
            return True

        def get_error_message(self) -> str:
            return "N/A"

    probes = [
        TestProbe(),
        TestProbe2(),
        TestProbe2(),
        TestProbe2(),
        TestProbe(),
    ]

    assert len(expand.get_failing_probes(probes)) == 2

    for i in expand.get_failing_probes(probes):
        if not isinstance(i, TestProbe):
            assert False


def test_urls():
    content = "https://google.com/yourmom \n\n dropbox: ssh://htop:pass"
    assert expand.filter_str_for_urls(content) == {"https://google.com/yourmom"}
    content = "\t\thttps://www.parasite.me\n\t\n dropbox: ssh://htop:pass"
    assert expand.filter_str_for_urls(content) == {"https://www.parasite.me"}

    content = """

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis gravida mi, non pulvinar augue. Quisque lacinia fermentum augue in euismod. Suspendisse nec hendrerit mi. Cras a leo a dui viverra imperdiet. Donec at ex tincidunt, placerat tellus ac, fringilla velit. Morbi scelerisque sapien sit amet scelerisque elementum. Nullam ultrices pharetra pretium. Suspendisse ex libero, vestibulum in lectus id, scelerisque condimentum dui. Vestibulum quis quam dui. Ut sit amet dictum lorem. Maecenas iaculis dolor a lacinia mollis. Phasellus mattis hendrerit nisl, vel aliquam magna luctus eget. Aenean lacinia congue laoreet. Nam nec gravida tellus, non eleifend felis. Sed volutpat non odio nec luctus.

Duis ac sapien diam. Sed molestie ornare feugiat. Phasellus convallis viverra ipsum, a venenatis leo egestas a. Suspendisse elementum purus enim, eget finibus justo pellentesque sit amet. In luctus posuere lorem, et eleifend ante lobortis ut. Etiam cursus mi lobortis nunc tempus luctus. Morbi at convallis orci, quis interdum lorem. Maecenas luctus eleifend dui, et pulvinar turpis tincidunt quis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Aenean posuere turpis eget dui consequat interdum. Vivamus sed semper massa. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In ullamcorper, nibh ut lacinia malesuada, risus justo feugiat odio, porttitor aliquam sem elit id leo. Sed non molestie erat, sed consectetur ante.

https://cdimage.kali.org/kali-weekly/kali-linux-2024-W19-installer-amd64.iso Suspendisse id magna a sem semper viverra http://google.com ac a odio. Nunc pellentesque nunc sit amet eros porttitor, ut cursus turpis porttitor. Fusce luctus neque in vulputate lacinia. Fusce tellus nisl, molestie vulputate mauris sed, iaculis tempor libero. Fusce tempor dictum arcu, in ullamcorper lorem luctus pulvinar. Quisque mattis semper nibh, eget pretium purus viverra vel. Vivamus eget pretium elit. Nam vel accumsan sapien. Pellentesque suscipit pharetra hendrerit. Ut rhoncus velit ligula, id fermentum erat molestie et. Curabitur eu suscipit massa, eget congue nisi. Maecenas in risus vitae erat convallis dapibus. Nulla eu nulla arcu. Praesent euismod urna eu nisl tincidunt efficitur. Vivamus cursus turpis ligula, eget rhoncus leo porta eget. Duis placerat nunc non laoreet dapibus.

Donec at venenatis neque. Integer odio velit, semper at hendrerit vel, blandit eget ligula. Donec ultrices augue at cursus faucibus. Praesent laoreet lectus ut eros aliquam, in dapibus lacus pulvinar. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ac fringilla purus. Morbi nec condimentum lorem. Donec egestas rhoncus mattis. In urna enim, malesuada vel dictum vel, suscipit et velit. Phasellus ullamcorper, est sed eleifend pharetra, turpis eros imperdiet urna, sit amet aliquam turpis lorem ut urna. Nullam vulputate enim nec nibh pharetra finibus. Praesent vel libero non massa feugiat venenatis https://robotics.net/yoursite?query=%20yourmom .

Maecenas https://cdimage.kali.org/kali-weekly/kali-linux-2024-W19-installer-amd64.iso non bibendum nulla, non placerat dolor. Curabitur molestie non libero in maximus. Aliquam dignissim arcu eget est lacinia, non imperdiet risus pellentesque. Cras a massa mattis, vehicula leo ut, sodales mi. Nulla arcu lorem, laoreet in nisi id, sollicitudin pellentesque erat. Mauris congue orci ipsum, sit amet ultrices lacus bibendum non. Cras odio massa, laoreet ac odio iaculis, malesuada congue magna. Ut lobortis sed velit vitae porttitor. Fusce tincidunt pellentesque lorem, id faucibus nisi ullamcorper quis. Quisque venenatis, magna vel ultricies luctus, quam purus placerat sapien, sit amet semper massa sem ut risus. Fusce eu velit ligula. Etiam ornare mattis dui, et faucibus augue feugiat vitae. Nulla arcu leo, posuere nec augue vitae, consequat euismod enim. Cras vitae dui tortor. Fusce tortor ligula, porttitor sit amet purus https://cdimage.kali.org/kali-weekly/kali-linux-2024-W19-installer-amd64.iso sed, condimentum imperdiet nisi.
"""
    assert expand.filter_str_for_urls(content) == {"http://google.com", "https://robotics.net/yoursite?query=%20yourmom", "https://cdimage.kali.org/kali-weekly/kali-linux-2024-W19-installer-amd64.iso"}

    content="download: (\"https://robotics.net/yoursite?query=%20yourmom\")"
    assert expand.filter_str_for_urls(content) == {"https://robotics.net/yoursite?query=%20yourmom"}


def test_columns():
    data = ["data1", "data2", "data3", "data4"]
    assert expand.get_formatted_columns(data, 20) == [("data1", 0), ("data2", 5), ("data3", 10), ("data4", 15)]
    assert expand.get_formatted_columns(data, 28) == [("data1", 0), ("data2", 7), ("data3", 14), ("data4", 21)]
    assert expand.get_formatted_columns(data, 8) == [("da", 0), ("da", 2), ("da", 4), ("da", 6)]
    assert expand.get_formatted_columns(data, 4) == [("d", 0), ("d", 1), ("d", 2), ("d", 3)]
    assert expand.get_formatted_columns(data, 3) == []
    assert expand.get_formatted_columns(data, 0) == []
    assert expand.get_formatted_columns(data, -1231) == []

    assert expand.get_formatted_columns(data, 20, [5, 5, -1, -1]) == [("data1", 0), ("data2", 5), ("data3", 10), ("data4", 15)]
    assert expand.get_formatted_columns(data, 20, [1, 1, -1, -1]) == [("d", 0), ("d", 1), ("data3", 2), ("data4", 11)]


def test_filter_choices():
    from expand import filter_choices

    names = ["firefox", "Chrome", "git", "GIMP", "vlc"]

    # Empty query returns all indices
    assert filter_choices(names, "") == [0, 1, 2, 3, 4]

    # Single match
    assert filter_choices(names, "firefox") == [0]

    # Multiple matches (case-insensitive 'gi' matches 'git' and 'GIMP')
    assert filter_choices(names, "gi") == [2, 3]

    # No matches
    assert filter_choices(names, "zzz") == []

    # Case insensitivity
    assert filter_choices(names, "CHROME") == [1]
    assert filter_choices(names, "gimp") == [3]

    # Special characters in query
    assert filter_choices(["c++", "c#", "go"], "+") == [0]
    assert filter_choices(["c++", "c#", "go"], "#") == [1]

    # Empty names list
    assert filter_choices([], "anything") == []
    assert filter_choices([], "") == []


def test_filter_visible_choices():
    """Test that filter_choices correctly narrows a list of names,
    mirroring the integration in get_visible_choices."""
    from expand import filter_choices

    # Simulate names that would come from visible choices
    names = ["firefox", "git", "GIMP", "vlc", "Chrome"]

    # No filter: all returned
    assert filter_choices(names, "") == [0, 1, 2, 3, 4]

    # Filter narrows to matching items
    matching = filter_choices(names, "gi")
    assert matching == [1, 2]  # git, GIMP

    # Filtered list keeps only matched entries
    filtered = [names[i] for i in matching]
    assert filtered == ["git", "GIMP"]

    # Single match
    assert [names[i] for i in filter_choices(names, "fire")] == ["firefox"]

    # No match produces empty list
    assert filter_choices(names, "zzz") == []
    assert [names[i] for i in filter_choices(names, "zzz")] == []

    # Case insensitive
    assert [names[i] for i in filter_choices(names, "chrome")] == ["Chrome"]


def test_line_buffer():
    from expand.line_buffer import LineBuffer

    # Basic append and total_lines
    buf = LineBuffer()
    assert buf.total_lines() == 0
    buf.append("line 0")
    buf.append("line 1")
    buf.append("line 2")
    assert buf.total_lines() == 3

    # get_visible with varying heights and offsets
    assert buf.get_visible(3, 0) == ["line 0", "line 1", "line 2"]
    assert buf.get_visible(2, 0) == ["line 0", "line 1"]
    assert buf.get_visible(2, 1) == ["line 1", "line 2"]
    assert buf.get_visible(5, 0) == ["line 0", "line 1", "line 2"]  # height > total returns what's available
    assert buf.get_visible(2, 2) == ["line 2"]  # offset near end
    assert buf.get_visible(2, 3) == []  # offset past end
    assert buf.get_visible(0, 0) == []  # zero height

    # is_at_bottom boundary conditions
    assert buf.is_at_bottom(3, 0) is True   # exactly fits
    assert buf.is_at_bottom(2, 1) is True   # offset + height == total
    assert buf.is_at_bottom(2, 0) is False  # can scroll more
    assert buf.is_at_bottom(5, 0) is True   # height exceeds total
    assert buf.is_at_bottom(1, 2) is True   # last line visible

    # Capacity overflow drops oldest lines
    small = LineBuffer(max_lines=3)
    for i in range(5):
        small.append(f"line {i}")
    assert small.total_lines() == 3
    assert small.get_visible(3, 0) == ["line 2", "line 3", "line 4"]

    # auto_scroll default
    assert LineBuffer().auto_scroll is True


def test_line_buffer_scroll():
    from expand.line_buffer import LineBuffer

    # Populate a buffer with 20 lines
    buf = LineBuffer()
    for i in range(20):
        buf.append(f"line {i}")

    height = 5

    # Initial view from top (scroll_offset=0)
    assert buf.get_visible(height, 0) == ["line 0", "line 1", "line 2", "line 3", "line 4"]

    # Scroll down by 1
    assert buf.get_visible(height, 1) == ["line 1", "line 2", "line 3", "line 4", "line 5"]

    # Scroll down by several
    assert buf.get_visible(height, 10) == ["line 10", "line 11", "line 12", "line 13", "line 14"]

    # Scroll up by 1 from offset 10
    assert buf.get_visible(height, 9) == ["line 9", "line 10", "line 11", "line 12", "line 13"]

    # Page down (rows - 3 = height): from offset 0, jump by 5
    offset = 0
    offset += height
    assert buf.get_visible(height, offset) == ["line 5", "line 6", "line 7", "line 8", "line 9"]

    # Page up: from offset 10, jump back by 5
    offset = 10
    offset = max(0, offset - height)
    assert buf.get_visible(height, offset) == ["line 5", "line 6", "line 7", "line 8", "line 9"]

    # Page up from near top doesn't go negative
    offset = 2
    offset = max(0, offset - height)
    assert offset == 0
    assert buf.get_visible(height, offset) == ["line 0", "line 1", "line 2", "line 3", "line 4"]

    # Home: scroll to top
    offset = 15
    offset = 0
    assert buf.get_visible(height, offset) == ["line 0", "line 1", "line 2", "line 3", "line 4"]

    # End: scroll to bottom
    offset = max(0, buf.total_lines() - height)
    assert offset == 15
    assert buf.get_visible(height, offset) == ["line 15", "line 16", "line 17", "line 18", "line 19"]
    assert buf.is_at_bottom(height, offset) is True

    # Verify is_at_bottom is False when not at bottom
    assert buf.is_at_bottom(height, 0) is False
    assert buf.is_at_bottom(height, 14) is False

    # Verify is_at_bottom is True at/past bottom
    assert buf.is_at_bottom(height, 15) is True
    assert buf.is_at_bottom(height, 16) is True

    # Scroll past end returns partial results
    assert buf.get_visible(height, 18) == ["line 18", "line 19"]
    assert buf.get_visible(height, 20) == []


def test_strip_ansi():
    from expand import strip_ansi

    # Plain text unchanged
    assert strip_ansi("hello world") == "hello world"

    # Strips color codes
    assert strip_ansi("\x1b[31mred text\x1b[0m") == "red text"

    # Strips multiple codes in one string
    assert strip_ansi("\x1b[1m\x1b[32mBold Green\x1b[0m normal") == "Bold Green normal"

    # Handles empty string
    assert strip_ansi("") == ""

    # Strips codes with multiple parameters (e.g., 38;5;196 for 256-color)
    assert strip_ansi("\x1b[38;5;196mcolored\x1b[0m") == "colored"


def test_select_all_visible():
    from expand.curses_cli import curses_cli, package_select

    # We only need the method, not a real curses instance.
    # select_all_visible doesn't use self, so pass None.
    cli = object.__new__(curses_cli)

    # Helper: create a fake visible_choices list [(orig_idx, stub), ...]
    def make_visible(orig_indices):
        return [(i, None) for i in orig_indices]

    # Empty visible list → selections unchanged
    sel = {package_select(0, 5)}
    result = cli.select_all_visible([], 0, sel)
    assert result == {package_select(0, 5)}

    # None selected → all get added
    visible = make_visible([0, 1, 2])
    result = cli.select_all_visible(visible, 0, set())
    assert result == {package_select(0, 0), package_select(0, 1), package_select(0, 2)}

    # Some selected → all get added (fills gaps)
    sel = {package_select(0, 0)}
    result = cli.select_all_visible(visible, 0, sel)
    assert result == {package_select(0, 0), package_select(0, 1), package_select(0, 2)}

    # All selected → all get removed (full toggle-off)
    sel = {package_select(0, 0), package_select(0, 1), package_select(0, 2)}
    result = cli.select_all_visible(visible, 0, sel)
    assert result == set()

    # Selections from a different category are not touched
    other_cat = {package_select(1, 0), package_select(1, 3)}
    sel = other_cat.copy()
    result = cli.select_all_visible(visible, 0, sel)
    # Should add category 0 items but keep category 1 items
    assert result == {package_select(0, 0), package_select(0, 1), package_select(0, 2),
                      package_select(1, 0), package_select(1, 3)}

    # Now toggle off category 0 — category 1 items should remain
    result2 = cli.select_all_visible(visible, 0, result)
    assert result2 == other_cat


def test_ansible_description():
    from expand import util

    assert util.get_ansible_description("# Test", 50) == ["N/A"]
    assert util.get_ansible_description("\nhehe", 50) == ["N/A"]
    assert util.get_ansible_description("2234wfsd", 0) == ["N/A"]
    assert util.get_ansible_description("2234wfsd\n#asdflhalsdf", 4) == ["N/A"]
    assert util.get_ansible_description("# Test\n#This is the first line.", 50) == ["This is the first line."]
    assert util.get_ansible_description("# Test\n#This is the first line.\n#This is the second line.", 50) == ["This is the first line.", "This is the second line."]
    assert util.get_ansible_description("# Test\n#Hello, World!", 3) == ["Hel", "lo,", " Wo", "rld", "!"]
    assert util.get_ansible_description("# Test\n#he\n#Hello, World!", 3) == ["he", "Hel", "lo,", " Wo", "rld", "!"]
    assert util.get_ansible_description("# Test\n#he\n#Hello, World!\n#\n#", 3) == ["he", "Hel", "lo,", " Wo", "rld", "!", "", ""]


def test_install_progress_title():
    from expand.curses_cli import format_install_title

    assert format_install_title(1, 5, "git") == "Installing [1/5]: git"
    assert format_install_title(1, 1, "git") == "Installing [1/1]: git"
    assert format_install_title(5, 5, "git") == "Installing [5/5]: git"
    assert format_install_title(3, 10, "firefox") == "Installing [3/10]: firefox"


def test_failure_cache(tmp_path, monkeypatch):
    from expand.failure_cache import FailureCache

    cache_file = tmp_path / "failures.json"
    monkeypatch.setattr(FailureCache, "CACHE_FILE", str(cache_file))

    # has_failed returns False when no cache file exists
    assert FailureCache.has_failed("pkg") is False

    # set_failed then has_failed returns True
    FailureCache.set_failed("pkg")
    assert FailureCache.has_failed("pkg") is True

    # clear_failed then has_failed returns False
    FailureCache.clear_failed("pkg")
    assert FailureCache.has_failed("pkg") is False

    # set_failed is idempotent (calling twice doesn't duplicate)
    FailureCache.set_failed("pkg")
    FailureCache.set_failed("pkg")
    import json
    with open(str(cache_file)) as f:
        data = json.load(f)
    assert data["failures"].count("pkg") == 1

    # clear_failed on a non-existent package doesn't crash
    FailureCache.clear_failed("nonexistent")


def test_failure_cache_corrupted(tmp_path, monkeypatch):
    from expand.failure_cache import FailureCache

    cache_file = tmp_path / "failures.json"
    monkeypatch.setattr(FailureCache, "CACHE_FILE", str(cache_file))

    # Invalid JSON string
    cache_file.write_text("not json")
    assert FailureCache.has_failed("pkg") is False

    # Empty string
    cache_file.write_text("")
    assert FailureCache.has_failed("pkg") is False

    # Malformed JSON (extra brace)
    cache_file.write_text('{}}')
    assert FailureCache.has_failed("pkg") is False


def test_failure_cache_missing_key(tmp_path, monkeypatch):
    from expand.failure_cache import FailureCache

    cache_file = tmp_path / "failures.json"
    monkeypatch.setattr(FailureCache, "CACHE_FILE", str(cache_file))

    # Valid JSON but missing "failures" key
    cache_file.write_text('{"other_key": 1}')
    assert FailureCache.has_failed("pkg") is False


# =============================================================================
# 3B: ExpansionCard Parsing Tests
# =============================================================================


def _write_expansion_yaml(tmp_path, filename, privilege, probes, installed_probes,
                          description_lines=None, body=None):
    """Helper that writes a temporary YAML file with the proper 4-line header."""
    lines = [
        f"# {privilege}",
        f"# {probes}",
        f"# {installed_probes}",
    ]
    if description_lines:
        for desc in description_lines:
            lines.append(f"# {desc}" if desc else "#")
    if body:
        lines.append(body)
    path = tmp_path / filename
    path.write_text("\n".join(lines) + "\n")
    return str(path)


def test_expansion_card_privilege(tmp_path):
    from expand.expansion_card import ExpansionCard
    from expand.priviledge import OnlyRoot, AnyUserEscalation, AnyUserNoEscalation

    cases = [
        ("OnlyRoot()", OnlyRoot),
        ("AnyUserEscalation()", AnyUserEscalation),
        ("AnyUserNoEscalation()", AnyUserNoEscalation),
    ]
    for priv_str, expected_cls in cases:
        path = _write_expansion_yaml(
            tmp_path, f"test_{priv_str}.yaml",
            privilege=priv_str, probes="[]", installed_probes="[]",
            description_lines=["test description"],
        )
        card = ExpansionCard(path)
        result = card.get_priviledge_level()
        assert isinstance(result, expected_cls), (
            f"Expected {expected_cls.__name__}, got {type(result).__name__}"
        )


def test_expansion_card_probes(tmp_path):
    from expand.expansion_card import ExpansionCard
    from expand.probes import AmdProbe

    # Empty probes list
    path = _write_expansion_yaml(
        tmp_path, "empty_probes.yaml",
        privilege="OnlyRoot()", probes="[]", installed_probes="[]",
        description_lines=["desc"],
    )
    card = ExpansionCard(path)
    assert card.get_probes() == []

    # Single probe
    path = _write_expansion_yaml(
        tmp_path, "one_probe.yaml",
        privilege="OnlyRoot()", probes="[AmdProbe()]", installed_probes="[]",
        description_lines=["desc"],
    )
    card = ExpansionCard(path)
    result = card.get_probes()
    assert len(result) == 1
    assert isinstance(result[0], AmdProbe)


def test_expansion_card_installed_probes(tmp_path):
    from expand.expansion_card import ExpansionCard
    from expand.probes import CommandProbe

    # With installed probes
    path = _write_expansion_yaml(
        tmp_path, "installed.yaml",
        privilege="OnlyRoot()", probes="[]",
        installed_probes='[CommandProbe("git")]',
        description_lines=["desc"],
    )
    card = ExpansionCard(path)
    result = card.get_installed_probes()
    assert len(result) == 1
    assert isinstance(result[0], CommandProbe)
    assert result[0].command == "git"

    # Empty installed probes
    path = _write_expansion_yaml(
        tmp_path, "no_installed.yaml",
        privilege="OnlyRoot()", probes="[]", installed_probes="[]",
        description_lines=["desc"],
    )
    card = ExpansionCard(path)
    assert card.get_installed_probes() == []

    # File with only 2 lines (no installed probes line) → returns []
    two_line = tmp_path / "two_line.yaml"
    two_line.write_text("# OnlyRoot()\n# []\n")
    card = ExpansionCard(str(two_line))
    assert card.get_installed_probes() == []


def test_expansion_card_description(tmp_path):
    from expand.expansion_card import ExpansionCard

    # Normal description
    path = _write_expansion_yaml(
        tmp_path, "desc.yaml",
        privilege="OnlyRoot()", probes="[]", installed_probes="[]",
        description_lines=["This is a description", "Second line here"],
    )
    card = ExpansionCard(path)
    result = card.get_ansible_description(80)
    assert result == ["This is a description", "Second line here"]

    # No description lines (file has exactly 3 comment lines) → returns []
    path = _write_expansion_yaml(
        tmp_path, "no_desc.yaml",
        privilege="OnlyRoot()", probes="[]", installed_probes="[]",
    )
    card = ExpansionCard(path)
    result = card.get_ansible_description(80)
    assert result == []

    # File with only 2 comment lines → returns ["N/A"]
    two_line_desc = tmp_path / "two_line_desc.yaml"
    two_line_desc.write_text("# OnlyRoot()\n# []\n")
    card = ExpansionCard(str(two_line_desc))
    result = card.get_ansible_description(80)
    assert result == ["N/A"]

    # Description with empty lines (paragraph breaks)
    path = _write_expansion_yaml(
        tmp_path, "para_desc.yaml",
        privilege="OnlyRoot()", probes="[]", installed_probes="[]",
        description_lines=["First paragraph", "", "Second paragraph"],
    )
    card = ExpansionCard(path)
    result = card.get_ansible_description(80)
    assert result == ["First paragraph", "", "Second paragraph"]

    # Description that gets word-wrapped at word boundaries
    path = _write_expansion_yaml(
        tmp_path, "wrap_desc.yaml",
        privilege="OnlyRoot()", probes="[]", installed_probes="[]",
        description_lines=["Install git from source"],
    )
    card = ExpansionCard(path)
    result = card.get_ansible_description(11)
    assert result == ["Install git", "from source"]

