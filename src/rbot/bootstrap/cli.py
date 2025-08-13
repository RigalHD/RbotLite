import argparse
import sys

from rbot.bootstrap.entrypoint.discord_bot import run_discord_bot


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_subparsers = run_parser.add_subparsers(dest="service", required=True)

    run_discord_bot_parser = run_subparsers.add_parser("discord_bot")
    run_discord_bot_parser.set_defaults(func=lambda _: run_discord_bot(argv))

    args = parser.parse_args(argv)

    if hasattr(args, "func"):
        args.func(args)
