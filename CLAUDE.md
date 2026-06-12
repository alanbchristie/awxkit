# awxkit

A standalone repository holding the `awxkit` Python package, extracted (with
full history) from the `awxkit/` directory of the
[ansible/awx](https://github.com/ansible/awx) monorepo at upstream release
`24.6.1`. It provides:

- **`awxkit`** — a Python library for talking to the AWX/Tower REST API
  (`awxkit/api/`), plus config (`config.py`), websocket client (`ws.py`),
  and utilities (`utils/`).
- **`awx`** — the AWX command-line client
  (entry point `awx=awxkit.cli:run`, code in `awxkit/cli/`).
- **`akit`** — an interactive shell session
  (entry point `akit=awxkit.scripts.basic_session:load_interactive`).

**This repository supports Python 3.13 and 3.14 only**
(`python_requires >= 3.13`). It carries fixes that upstream 24.6.1 lacked
for modern Pythons: the `HelpfulArgumentParser._parse_known_args()` signature
change in argparse 3.13 (ansible/awx#16441), `pkg_resources` →
`importlib.metadata`, `distutils` removal (`LooseVersion` →
`packaging.version.Version`, a local `strtobool` in `cli/format.py`), and
`datetime.utcnow()` deprecation.

## Layout

```
.                       # repo root = the package root
├── setup.py            # the ONLY build definition (no pyproject.toml/setup.cfg)
├── MANIFEST.in         # sdist contents (includes VERSION, requirements.txt, tests)
├── requirements.txt    # literally "." — package is self-describing
├── tox.ini             # test/lint envs + flake8 + pytest config
├── awxkit/             # the importable package
│   ├── api/            # REST API page objects, client, registry
│   ├── cli/            # `awx` CLI (client.py, options.py, format.py, ...)
│   │   └── docs/       # Sphinx docs for the CLI (needs a live AWX server)
│   ├── scripts/        # `akit` interactive session
│   └── utils/
└── test/               # unit tests (pytest), excluded from wheels via
                        # find_packages(exclude=['test'])
```

## Versioning

`setup.py` has two mutually exclusive version sources, checked in this order:

1. **`VERSION` file** in the repo root (not in git; listed in MANIFEST.in).
   If present, its contents are the version verbatim and setuptools_scm is
   skipped entirely.
2. **setuptools_scm** on this repository's own git tags. An untagged commit
   yields a dev version such as `1.0.1.dev3+gabc1234`.

`SETUPTOOLS_SCM_PRETEND_VERSION=X.Y.Z` overrides both — handy for builds
from shallow clones or for pinning a release version explicitly. The
publish workflow uses it to pass the release tag through, so the override
only accepts strings `packaging.version.Version` can parse — name-prefixed
tags like `alanbchristie-awxkit-1.0.0` raise `InvalidVersion` here, even
though setuptools_scm's own tag discovery would strip the prefix. (One such
legacy tag exists; release tags are plain semver from `1.0.1` onward.)

**Release tags must be plain semver**: `X.Y.Z`, optionally with an
`-alpha[.N]`, `-beta[.N]`, or `-rc[.N]` pre-release suffix (enforced by a
fail-fast check in `publish.yaml`). Pre-release versions normalise to
their PEP 440 spellings in the built artifacts (`1.0.0-rc.1` → `1.0.0rc1`)
and PyPI/pip treat them as pre-releases.

At runtime the CLI reports its version via
`importlib.metadata.version('alanbchristie-awxkit')` (`awxkit/cli/client.py`),
so the package **must be installed** (`pip install -e .` is fine) for
`awx --version` or any CLI usage to work — there is no hardcoded
`__version__` in the source.

## Building a release

Normal releases are published by `.github/workflows/publish.yaml`: create a
GitHub release on `main` whose tag is a plain semver version (see
"Versioning" above) and the workflow builds the package with the tag as its
version and uploads it to PyPI via trusted publishing (GitHub Environment
`pypi`). To build/upload manually instead:

```bash
pip install build twine setuptools-scm
git tag <X.Y.Z>
python -m build
twine upload -r <pypi|testpypi> dist/*
```

The custom `python setup.py clean` command force-removes `__pycache__`,
`.pyc`, and egg-info debris.

### Gotchas

- **The distribution name is `alanbchristie-awxkit`** (the PyPI name `awxkit`
  is taken by upstream ansible/awx), while the import package remains
  `awxkit`. The `name=` in `setup.py` and the
  `importlib.metadata.version('alanbchristie-awxkit')` call in
  `cli/client.py` must stay in sync, or the CLI crashes on import —
  `test/cli/test_utils.py` guards this.
- Building from a shallow clone breaks setuptools_scm (no tags); either
  fetch tags, use `SETUPTOOLS_SCM_PRETEND_VERSION`, or drop a `VERSION` file.
- To pull a future upstream awxkit fix, export it from an ansible/awx clone
  with `git format-patch -1 <sha> -- awxkit/` and apply it here with
  `git am -p2` (`-p2` strips the leading `a/awxkit/` so paths land at this
  repo's root).

## Testing

Tests are self-contained — no running AWX server or database required.

```bash
tox             # runs py313 + py314 (264 tests each; verified passing 2026-06)
tox -e py313    # one interpreter only
tox -e lint     # flake8 — currently FAILS, see below
```

**The lint env is bitrotted — do not trust it.** The code is formatted by
black at line-length 160 (the monorepo's convention), but `tox.ini` sets
flake8 `max-line-length = 120`, so `flake8 awxkit` reports ~200 E501
violations (plus E203, a known black/flake8 conflict). It is excluded from
the default envlist; run it only to lint specific changed files.

Tox specifics (`tox.ini`):

- Default envlist is `py313, py314` — the only supported interpreters.
- Test deps: `websocket-client coverage mock pytest pytest-mock`.
- The test command is
  `coverage run --parallel --source awxkit -m pytest --doctest-glob='*.md' --junit-xml=report.xml`.
- **`filterwarnings = error`** — any Python warning fails the test run. New
  deprecation warnings from dependency upgrades will break tests; that is
  intentional, do not blanket-ignore them.
- flake8: `max-line-length = 120`.

Direct pytest also works once deps are installed:

```bash
pip install -e . websocket-client mock pytest pytest-mock
pytest test/
```

## CI

`.github/workflows/ci.yml` runs on every push/PR: the tox suite on a
Python 3.13 + 3.14 matrix, plus an sdist/wheel build with `twine check`.
It checks out with `fetch-depth: 0` because setuptools_scm needs the tags.

## Runtime dependencies

From `setup.py`: `PyYAML`, `requests`, `packaging` (deliberately minimal —
`packaging` is needed by `awxkit.awx.version_cmp`). Extras: `[formatting]` →
`jq`, `[websockets]` → `websocket-client==0.57.0` (pinned), `[crypto]` →
`cryptography`. `python_requires >= 3.13`.

## CLI docs

`awxkit/cli/docs/` is a Sphinx project that auto-generates CLI reference docs
by **introspecting a live AWX server**:

```bash
cd awxkit/cli/docs
pip install sphinx sphinxcontrib-autoprogram
CONTROLLER_HOST=https://awx.example.org CONTROLLER_USERNAME=u CONTROLLER_PASSWORD=p make clean html
```
