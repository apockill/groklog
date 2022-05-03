from groklog.args import parse_args
from groklog.filter_manager import FilterManager
from groklog.process_node import ShellProcessIO
from groklog.ui import GroklogApp

from .version import __version__


def main():
    # TODO: Pass args
    args = parse_args()
    GroklogApp.run(title="Groklog")


if __name__ == "__main__":
    main()
