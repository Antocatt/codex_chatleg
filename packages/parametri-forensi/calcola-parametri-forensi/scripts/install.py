#!/usr/bin/env python3
"""Install a self-contained skill without overwriting existing installations."""
import argparse
import os
from pathlib import Path
import shutil
import sys

NAME = 'calcola-parametri-forensi'
SOURCE = Path(__file__).resolve().parents[1]


def destination(agent, home, codex_home=None):
    if agent == 'codex':
        return home / '.agents' / 'skills' / NAME
    if agent == 'codex-legacy':
        return Path(codex_home or home / '.codex') / 'skills' / NAME
    return home / '.claude' / 'skills' / NAME


def install(agent, home, codex_home=None):
    target = destination(agent, home, codex_home)
    if target.exists() or target.is_symlink():
        raise FileExistsError(f'Installazione già presente: {target}. Nessun file sovrascritto.')
    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store', '.git'))
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=['codex', 'codex-legacy', 'claude', 'both'], required=True)
    parser.add_argument('--home', type=Path, default=Path.home(), help='Home alternativa per installazione di prova')
    args = parser.parse_args()
    agents = ['codex', 'claude'] if args.agent == 'both' else [args.agent]
    try:
        # Check all destinations before copying either package.
        for agent in agents:
            target = destination(agent, args.home, os.environ.get('CODEX_HOME') if agent == 'codex-legacy' else None)
            if target.exists() or target.is_symlink():
                raise FileExistsError(f'Installazione già presente: {target}')
        for agent in agents:
            print(install(agent, args.home, os.environ.get('CODEX_HOME') if agent == 'codex-legacy' else None))
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
