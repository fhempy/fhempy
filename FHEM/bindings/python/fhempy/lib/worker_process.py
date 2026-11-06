"""Started by the fhempy process for a worker group, see core/workers.py"""

import argparse
import logging


def main(argv=None):
    parser = argparse.ArgumentParser(description="fhempy worker process")
    parser.add_argument("--socket", required=True)
    parser.add_argument("--group", required=True)
    args = parser.parse_args(argv)

    logging.basicConfig(
        format=(
            "%(asctime)s - %(levelname)-8s - [" + args.group + "] %(name)s: %(message)s"
        ),
        level=logging.INFO,
    )

    from fhempy.lib import fhem_pythonbinding

    fhem_pythonbinding.run_worker(args.socket, args.group)


if __name__ == "__main__":
    main()
