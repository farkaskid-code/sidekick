from argparse import ArgumentParser, Namespace


def parse_args() -> Namespace:
    parser = ArgumentParser(description="sidekick args parser")

    parser.add_argument("query", type=str, help="User query")

    return parser.parse_args()
