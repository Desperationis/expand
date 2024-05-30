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

