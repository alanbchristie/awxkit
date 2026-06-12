# awxkit

A standalone Python package living inside the AWX monorepo. It provides:

- **`awxkit`** — a Python library for talking to the AWX/Tower REST API
  (`awxkit/api/`), plus config (`config.py`), websocket client (`ws.py`),
  and utilities (`utils/`).
- **`awx`** — the official AWX command-line client
  (entry point `awx=awxkit.cli:run`, code in `awxkit/cli/`).
- **`akit`** — an interactive shell session
  (entry point `akit=awxkit.scripts.basic_session:load_interactive`).

Upstream publishes this directory to PyPI as `awxkit` (last upstream release
of this fork's lineage: `24.6.1`). This fork exists to publish its own package
from here.

**This fork supports Python 3.13 and 3.14 only** (`python_requires >= 3.13`).
The branch carries fixes that upstream 24.6.1 lacked for modern Pythons:
the `HelpfulArgumentParser._parse_known_args()` signature change in argparse
3.13 (ansible/awx#16441), `pkg_resources` → `importlib.metadata`,
`distutils` removal (`LooseVersion` → `packaging.version.Version`, a local
`strtobool` in `cli/format.py`), and `datetime.utcnow()` deprecation.

## Layout

```
awxkit/                 # this directory = the package root (setup.py lives here)
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

## Versioning — the most important thing to understand

`setup.py` has two mutually exclusive version sources, checked in this order:

1. **`VERSION` file** in this directory (not in git; listed in MANIFEST.in).
   If present, its contents are the version verbatim and setuptools_scm is
   skipped entirely.
2. **setuptools_scm** with `root=".."` — i.e. the version is derived from
   **git tags of the parent AWX repo**, not anything in this directory.
   The repo's tags look like `24.6.1`; an untagged checkout yields a dev
   version such as `24.6.2.dev846+gc8981e321e`.

Upstream's release pipeline (`.github/workflows/promote.yml`) sidesteps both
by exporting `SETUPTOOLS_SCM_PRETEND_VERSION=<tag>` before building. That env
var is the simplest way to pin an exact version for this fork's releases too.

At runtime the CLI reports its version via
`importlib.metadata.version('awxkit')` (`awxkit/cli/client.py:18`), so the
package **must be installed** (`pip install -e .` is fine) for `awx --version`
or any CLI usage to work — there is no hardcoded `__version__` in the source.

## Building a release

From this directory (mirrors upstream's promote workflow):

```bash
pip install wheel twine setuptools-scm
SETUPTOOLS_SCM_PRETEND_VERSION=X.Y.Z python3 setup.py sdist bdist_wheel
twine upload -r <pypi|testpypi> dist/*
```

`python -m build` also works (it honours the same env var). The custom
`python setup.py clean` command force-removes `__pycache__`, `.pyc`, and
egg-info debris.

### Fork-specific gotchas

- **The PyPI name `awxkit` is taken** by upstream. Publishing this fork's
  package requires changing `name=` in `setup.py` (and remember
  `importlib.metadata.version('awxkit')` in `cli/client.py` must match the
  new distribution name, or the CLI crashes on import).
- Upstream's promote.yml automatically targets **testpypi** when the repo
  owner isn't `ansible` — useful as a dry-run target.
- Building from a shallow clone breaks setuptools_scm (no tags); either
  fetch tags, use `SETUPTOOLS_SCM_PRETEND_VERSION`, or drop a `VERSION` file.

## Testing

Tests are self-contained — no running AWX server, no database, nothing from
the parent repo is required.

```bash
cd awxkit
tox             # runs py313 + py314 (264 tests each; verified passing 2026-06)
tox -e py313    # one interpreter only
tox -e lint     # flake8 — currently FAILS, see below
```

**The lint env is bitrotted — do not trust it.** The code is formatted by
black at line-length 160 (repo-root `pyproject.toml`), but `tox.ini` sets
flake8 `max-line-length = 120`, so `flake8 awxkit` reports ~200 E501
violations (plus E203, a known black/flake8 conflict). It is excluded from
the default envlist; run it only to lint specific changed files.

Tox specifics (`tox.ini`):

- Default envlist is `py313, py314` — the only supported interpreters.
- Test deps: `websocket-client coverage mock pytest pytest-mock`.
- The test command is
  `coverage run --parallel --source awxkit -m pytest --doctest-glob='*.md' --junit-xml=report.xml`,
  producing `report.xml` and `coverage.xml` (consumed by upstream CI/Codecov).
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

`.github/workflows/awxkit-ci.yml` is this fork's dedicated workflow: on any
push/PR touching `awxkit/**` it runs the tox suite on a Python 3.13 + 3.14
matrix and builds + `twine check`s the sdist/wheel. It checks out with
`fetch-depth: 0` because setuptools_scm needs the repo tags. The inherited
upstream workflows (`ci.yml` etc.) test the full AWX stack in Docker and are
irrelevant to this fork's packaging goal.

## Ties to the parent repo (the only ones that matter)

- **Version source**: git tags live at the repo root (see Versioning above).
- **Formatting**: the root `make black` formats `awxkit/` with the repo-root
  `pyproject.toml` config (`line-length = 160`). This **conflicts** with
  flake8's `max-line-length = 120` in `tox.ini` — see below.
- **Release**: `.github/workflows/promote.yml` builds and twine-uploads this
  directory on a GitHub release/tag (alongside the collection and images —
  trim those jobs if this fork only ships the Python package).

Nothing in `awxkit` imports from the `awx` Django application; the directory
can be built and tested in complete isolation.

## Runtime dependencies

From `setup.py`: `PyYAML`, `requests`, `packaging` (deliberately minimal —
`packaging` is needed by `awxkit.awx.version_cmp`). Extras: `[formatting]` →
`jq`, `[websockets]` → `websocket-client==0.57.0` (pinned), `[crypto]` →
`cryptography`. `python_requires >= 3.13`.

## CLI docs

`awxkit/cli/docs/` is a Sphinx project that auto-generates CLI reference docs
by **introspecting a live AWX server**:

```bash
cd awxkit/awxkit/cli/docs
pip install sphinx sphinxcontrib-autoprogram
CONTROLLER_HOST=https://awx.example.org CONTROLLER_USERNAME=u CONTROLLER_PASSWORD=p make clean html
```
