import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

import argparse
from . import convert_f


def main(*override_args):
    parser = argparse.ArgumentParser(
        description='Serialized file converter',
        fromfile_prefix_chars='@'
    )
        
    parser.add_argument(
        "input",
        type=str,
        help="The path to the source file"
    )
    parser.add_argument(
        "-i",
        "--ilang",
        metavar="ilang",
        type=str,
        default="",
        help="Override markup language for source file"
    )
    parser.add_argument(
        "output",
        type=str,
        help="The path to the new file"
    )
    parser.add_argument(
        "-o",
        "--olang",
        metavar="olang",
        type=str,
        default="",
        help="Override markup language for new file"
    )

    args = parser.parse_args(*override_args)

    convert_f(**vars(args))


if __name__ == "__main__":
    try:
        main()        
    except KeyboardInterrupt:
        logging.info("The program was interrupted by user")
