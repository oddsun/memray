import os

import pytest
from IPython.core.displaypub import CapturingDisplayPublisher
from IPython.core.interactiveshell import InteractiveShell


def run_in_ipython_shell(tmpdir, cells):
    """Run the given cells in an IPython shell and return the HTML output."""
    InteractiveShell.clear_instance()

    shell = InteractiveShell.instance(display_pub_class=CapturingDisplayPublisher)
    prev_running_dir = os.getcwd()
    try:
        os.chdir(tmpdir)
        for cell in cells:
            shell.run_cell(cell)
    finally:
        os.chdir(prev_running_dir)

    InteractiveShell.clear_instance()
    try:
        html = shell.display_pub.outputs[-1]["data"]["text/html"]
        return html
    except IndexError:
        return None


@pytest.mark.filterwarnings("ignore")
class TestIPython:
    def test_ipython_profiling(self, tmpdir):
        """Test that the IPython extension works."""
        # GIVEN
        code = [
            "%load_ext memray",
            """
            %%memray_flamegraph
            x = "a" * 10000
            """,
        ]

        # WHEN

        html = run_in_ipython_shell(tmpdir, code)

        # THEN

        assert html is not None
        assert "<iframe" in html
        assert "flamegraph.html" in html

    def test_exception_while_ipython_profiling(self, tmpdir):
        """Test that the IPython extension works even if an exception
        is raised."""
        # GIVEN

        code = [
            "%load_ext memray",
            """
            %%memray_flamegraph
            x = "a" * 10000
            1/0
            """,
        ]

        # WHEN

        html = run_in_ipython_shell(tmpdir, code)

        # THEN

        assert html is not None
        assert "<iframe" in html
        assert "flamegraph.html" in html

    def test_passing_help_argument(self, tmpdir, capsys):
        # GIVEN

        code = [
            "%load_ext memray",
            """
            %%memray_flamegraph -h
            """,
        ]

        # WHEN

        html = run_in_ipython_shell(tmpdir, code)

        # THEN

        assert html is None
        stdout, stderr = capsys.readouterr()
        assert "show this help message" in stdout
        assert "" == stderr

    def test_passing_invalid_argument(self, tmpdir, capsys):
        # GIVEN

        code = [
            "%load_ext memray",
            """
            %%memray_flamegraph --oopsie
            """,
        ]

        # WHEN

        html = run_in_ipython_shell(tmpdir, code)

        # THEN

        assert html is None
        stdout, stderr = capsys.readouterr()
        assert "" == stdout
        assert "usage:" in stderr

    def test_passing_valid_argument(self, tmpdir, capsys):
        # GIVEN

        code = [
            "%load_ext memray",
            """
            %%memray_flamegraph --leaks
            x = "a" * 10000
            """,
        ]

        # WHEN

        html = run_in_ipython_shell(tmpdir, code)

        # THEN

        assert html is not None
        stdout, _ = capsys.readouterr()
        assert "<iframe" in html
        assert "flamegraph.html" in html
        assert "Results saved to" in stdout
