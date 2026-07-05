import argparse
import contextlib
import sys

import alembic.config

from rbot.bootstrap.entrypoint.discord_bot import run_discord_bot
from rbot.infrastracture.database.alembic.config import get_alembic_config_path


def run_migrations() -> None:
    config_path_generator = get_alembic_config_path()
    config_path = str(next(config_path_generator))
    alembic.config.main(argv=["-c", config_path, "upgrade", "head"])
    with contextlib.suppress(StopIteration):
        next(config_path_generator)


def autogenerate_migration(message: str) -> None:
    config_path_generator = get_alembic_config_path()
    config_path = str(next(config_path_generator))
    alembic.config.main(
        argv=["-c", config_path, "revision", "--autogenerate", "-m", message],
    )
    with contextlib.suppress(StopIteration):
        next(config_path_generator)


def main(argv: list[str] | None = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_subparsers = run_parser.add_subparsers(dest="service", required=True)

    run_discord_bot_parser = run_subparsers.add_parser("bot")
    run_discord_bot_parser.set_defaults(func=lambda _: run_discord_bot(argv))

    migrations_parser = subparsers.add_parser("migrations")
    migrations_subparsers = migrations_parser.add_subparsers(
        dest="operation",
        required=True,
    )

    autogenerate_parser = migrations_subparsers.add_parser("autogenerate")
    autogenerate_parser.add_argument("message")
    autogenerate_parser.set_defaults(
        func=lambda args: autogenerate_migration(args.message),
    )

    args = parser.parse_args(argv)
    run_migrations()

    if hasattr(args, "func"):
        args.func(args)
