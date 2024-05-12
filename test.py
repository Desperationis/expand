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



