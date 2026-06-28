"""Command-line interface for compound-to-sigma."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .runner import from_names
from .utils import Logger


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cosmo-skill",
        description="Compute COSMO-RS sigma profiles from compound names, SMILES, xyz, or coskf files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run pipeline from a YAML config file")
    run_parser.add_argument("config", type=str, help="Path to YAML configuration file")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and environment without running calculations",
    )

    return parser


def _dry_run(config: dict, logger: Logger) -> int:
    """Validate configuration and environment without running jobs."""
    from .runner import _check_environment

    try:
        _check_environment(logger)
    except RuntimeError as e:
        logger.error(str(e))
        return 1

    logger.info(f"Output directory: {config['output_dir']}")
    logger.info(f"Database path: {config.get('database_path') or 'not set'}")
    logger.info(f"Method: {config['method']}")
    logger.info(f"Parallel jobs: {config['n_jobs']}")
    logger.info(f"Compounds: {len(config['compounds'])}")
    for i, c in enumerate(config["compounds"]):
        logger.info(f"  {i}: {c}")

    logger.info("Dry run completed successfully")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        config = load_config(args.config)
        logger = Logger(config["verbose"])

        if args.dry_run:
            return _dry_run(config, logger)

        results = from_names(
            compounds=config["compounds"],
            output_dir=config["output_dir"],
            database_path=config.get("database_path"),
            n_jobs=config["n_jobs"],
            method=config["method"],
            verbose=config["verbose"],
        )

        n_success = len(results["successes"])
        n_failure = len(results["failures"])
        logger.info(f"Done: {n_success} succeeded, {n_failure} failed")

        if n_failure > 0:
            logger.error("Failures:")
            for f in results["failures"]:
                logger.error(f"  {f['name']}: {f['error']}")
            return 1
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
