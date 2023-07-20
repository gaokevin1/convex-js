#!/usr/bin/env python3

import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Dict

NPM = "npm.CMD" if os.name == "nt" else "npm"

times: Dict[str, float] = {}


def log_duration(func: Callable[[], None]) -> Callable[[], None]:
    def timed() -> None:
        t0 = time.time()
        func()
        duration = time.time() - t0
        times[func.__name__] = duration

    return timed


@log_duration
def build_types() -> None:
    subprocess.run([NPM, "run", "build-types"], check=True)


@log_duration
def build_internal_types() -> None:
    subprocess.run([NPM, "run", "build-internal-types"], check=True)


@log_duration
def check_cli_types() -> None:
    subprocess.run([NPM, "run", "check-cli-types"], check=True)


@log_duration
def build_esm() -> None:
    subprocess.run([NPM, "run", "build-esm"], check=True)


@log_duration
def build_cjs() -> None:
    subprocess.run([NPM, "run", "build-cjs"], check=True)


@log_duration
def build_browser_script_tag() -> None:
    subprocess.run([NPM, "run", "build-browser-script-tag"], check=True)


@log_duration
def build_react_script_tag() -> None:
    subprocess.run([NPM, "run", "build-react-script-tag"], check=True)


@log_duration
def build_standalone_cli() -> None:
    subprocess.run([NPM, "run", "build-standalone-cli"], check=True)


def main() -> None:
    global times
    t0 = time.time()

    pool = ThreadPoolExecutor(max_workers=20)

    children = []
    children.append(pool.submit(build_types))
    children.append(pool.submit(build_internal_types))
    children.append(pool.submit(check_cli_types))
    children.append(pool.submit(build_cjs))
    children.append(pool.submit(build_esm))
    children.append(pool.submit(build_browser_script_tag))
    children.append(pool.submit(build_react_script_tag))
    children.append(pool.submit(build_standalone_cli))

    for child in as_completed(children):
        try:
            child.result()
        except subprocess.CalledProcessError:
            # Skip the stacktrace - not really useful in output
            sys.exit(1)

    for name in sorted(times.keys(), key=lambda task: times[task]):
        print(f"{round(times[name], 3):2.2f}s {name}")

    print(f"{time.time() - t0:2.2f}s total")


if __name__ == "__main__":
    main()
