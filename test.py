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


def test_textcomponent():
    from expand import textcomponent, brect
    
    def c(text, rect, flags):
        text = textcomponent.get_cropped_text(text, rect)
        return textcomponent.calculate_text_alignment_offset(text, rect, flags)

    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 10), textcomponent.NONE) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(-2, 40, 1, 10), textcomponent.NONE) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(1, 1, 1, 4), textcomponent.NONE) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 100), textcomponent.NONE) == (0,0)

    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 10), textcomponent.ALIGN_H_LEFT) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(-2, 40, 1, 10), textcomponent.ALIGN_H_LEFT) == (2,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(1, 1, 1, 4), textcomponent.ALIGN_H_LEFT) == (-1,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 100), textcomponent.ALIGN_H_LEFT) == (0,0)

    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 10), textcomponent.ALIGN_V_TOP) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(-2, 40, 1, 10), textcomponent.ALIGN_V_TOP) == (0,-40)
    assert c("ABCDEFGHIJKLMNLOP", brect(1, 1, 1, 4), textcomponent.ALIGN_V_TOP) == (0,-1)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 100), textcomponent.ALIGN_V_TOP) == (0,0)

    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 10), textcomponent.ALIGN_H_RIGHT) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 10), textcomponent.ALIGN_H_RIGHT) == (83,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 10), textcomponent.ALIGN_H_MIDDLE) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 19, 10), textcomponent.ALIGN_H_MIDDLE) == (1,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 21, 10), textcomponent.ALIGN_H_MIDDLE) == (2,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 27, 10), textcomponent.ALIGN_H_MIDDLE) == (5,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 10), textcomponent.ALIGN_V_MIDDLE) == (0,4)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 1), textcomponent.ALIGN_V_MIDDLE) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 10), textcomponent.ALIGN_V_MIDDLE) == (0,4)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 1), textcomponent.ALIGN_V_MIDDLE) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 10), textcomponent.ALIGN_V_BOTTOM) == (0,9)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 100, 1), textcomponent.ALIGN_V_BOTTOM) == (0,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 0, 10, 10001), textcomponent.ALIGN_V_BOTTOM) == (0,10000)

    assert c("ABCDEFGHIJKLMNLOP", brect(1092, 0, 10, 10), textcomponent.ALIGN_H_RIGHT) == (-1092,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(234982, 0, 100, 10), textcomponent.ALIGN_H_RIGHT) == (83 - 234982,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(-12, 0, 10, 10), textcomponent.ALIGN_H_MIDDLE) == (12,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(12, 0, 19, 10), textcomponent.ALIGN_H_MIDDLE) == (-12 + 1,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(234, 0, 21, 10), textcomponent.ALIGN_H_MIDDLE) == (2 - 234,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(-234, 0, 27, 10), textcomponent.ALIGN_H_MIDDLE) == (5 + 234,0)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 10, 100, 10), textcomponent.ALIGN_V_MIDDLE) == (0,-6)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, -1, 100, 1), textcomponent.ALIGN_V_MIDDLE) == (0,1)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, -3, 10, 10), textcomponent.ALIGN_V_MIDDLE) == (0,7)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 23, 10, 1), textcomponent.ALIGN_V_MIDDLE) == (0,-23)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 234, 100, 10), textcomponent.ALIGN_V_BOTTOM) == (0,9 - 234)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, 1002, 100, 1), textcomponent.ALIGN_V_BOTTOM) == (0,-1002)
    assert c("ABCDEFGHIJKLMNLOP", brect(0, -1, 10, 10001), textcomponent.ALIGN_V_BOTTOM) == (0,10000 + 1)

    assert textcomponent.get_cropped_text("hellothere", brect(100, -1, 5, 1)) == "hello"

def test_component_alignment():
    from expand import component, brect

    assert component.calculate_alignment_offset(rect=brect(0, 0, 10, 10), container_rect=brect(0, 0, 100, 100), alignment=(-1, -1)) == (0,0)
    assert component.calculate_alignment_offset(rect=brect(224, -12, 10, 10), container_rect=brect(0, 0, 100, 100), alignment=(-1, -1)) == (-224,12)
    assert component.calculate_alignment_offset(rect=brect(224, -12, 10, 10), container_rect=brect(20, 22, 100, 100), alignment=(-1, -1)) == (-204,34)

    assert component.calculate_alignment_offset(rect=brect(0, 0, 10, 10), container_rect=brect(0, 0, 100, 100), alignment=(-1, 1)) == (0,100 - 10)
    assert component.calculate_alignment_offset(rect=brect(224, -12, 10, 10), container_rect=brect(0, 0, 100, 100), alignment=(-1, 1)) == (-224,100 + 12 - 10)
    assert component.calculate_alignment_offset(rect=brect(224, -12, 10, 10), container_rect=brect(20, 22, 100, 100), alignment=(-1, 1)) == (-204,100 + 12 + 22 - 10)

    assert component.calculate_alignment_offset(rect=brect(0, 0, 10, 10), container_rect=brect(0, 0, 100, 100), alignment=(-1, 0)) == (0,50 - 5)
    assert component.calculate_alignment_offset(rect=brect(224, -12, 10, 10), container_rect=brect(0, 0, 100, 100), alignment=(-1, 0)) == (-224,50 + 12 - 5)
    assert component.calculate_alignment_offset(rect=brect(224, -12, 10, 10), container_rect=brect(20, 22, 100, 100), alignment=(-1, 0)) == (-204,50 + 12 + 22 - 5)


def test_bounding_collision():
    from expand import brect
    assert brect(0,0,10,10).colliding(brect(0,0,10,10)) == True
    assert brect(0,0,10,10).colliding(brect(9,9,10,10)) == True
    assert brect(-1,2,10,10).colliding(brect(-5,2,10,10)) == True
    assert brect(-1,2,10000,10000).colliding(brect(928,231,1,1)) == True


    assert brect(0,0,10,10).colliding(brect(10,10,10,10)) == False
    assert brect(0,0,10,10).colliding(brect(11,10,10,10)) == False
    assert brect(0,0,10,10).colliding(brect(10,11,10,10)) == False
    assert brect(-10,-10,10,10).colliding(brect(0,0,10,10)) == False


def test_pubsub():
    from expand import PubSub, KeyMessage

    PubSub.reset()

    called = [False] * 10

    def flip(i):
        called[i] = not called[i]

    PubSub.add_listener("1", KeyMessage, lambda a: flip(0))
    PubSub.add_listener("2", KeyMessage, lambda a: flip(4))
    PubSub.add_listener("3", KeyMessage, lambda a: flip(8))

    for i in called:
        assert not i

    PubSub.invoke_global(KeyMessage("a", "a"))

    assert called[0] == True
    assert called[1] == False
    assert called[2] == False
    assert called[3] == False
    assert called[4] == True
    assert called[5] == False
    assert called[6] == False
    assert called[7] == False
    assert called[8] == True
    assert called[9] == False


def test_pubsub2():
    from expand import PubSub, KeyMessage

    PubSub.reset()

    called = [False] * 10

    def flip(i):
        called[i] = not called[i]

    PubSub.add_listener("1", KeyMessage, lambda a: flip(0))
    PubSub.add_listener("2", KeyMessage, lambda a: flip(4))
    PubSub.add_listener("3", KeyMessage, lambda a: flip(8))

    for i in called:
        assert not i

    PubSub.invoke_to(KeyMessage("a", "a"), "1")

    assert called[0] == True
    assert called[1] == False
    assert called[2] == False
    assert called[3] == False
    assert called[4] == False
    assert called[5] == False
    assert called[6] == False
    assert called[7] == False
    assert called[8] == False
    assert called[9] == False



    PubSub.invoke_to(KeyMessage("a", "a"), "1")

    assert called[0] == False
    assert called[1] == False
    assert called[2] == False
    assert called[3] == False
    assert called[4] == False
    assert called[5] == False
    assert called[6] == False
    assert called[7] == False
    assert called[8] == False
    assert called[9] == False

    PubSub.invoke_to(KeyMessage("a", "a"), "2")

    assert called[0] == False
    assert called[1] == False
    assert called[2] == False
    assert called[3] == False
    assert called[4] == True
    assert called[5] == False
    assert called[6] == False
    assert called[7] == False
    assert called[8] == False
    assert called[9] == False


    PubSub.invoke_to(KeyMessage("a", "a"), "3")

    assert called[0] == False
    assert called[1] == False
    assert called[2] == False
    assert called[3] == False
    assert called[4] == True
    assert called[5] == False
    assert called[6] == False
    assert called[7] == False
    assert called[8] == True
    assert called[9] == False



    PubSub.add_listener("1", KeyMessage, lambda a: flip(0))
    PubSub.invoke_to(KeyMessage("a", "a"), "1")


    assert called[0] == False
    assert called[1] == False
    assert called[2] == False
    assert called[3] == False
    assert called[4] == True
    assert called[5] == False
    assert called[6] == False
    assert called[7] == False
    assert called[8] == True
    assert called[9] == False
