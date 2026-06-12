alanbchristie-awxkit
====================

[![CI](https://github.com/alanbchristie/awxkit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/alanbchristie/awxkit/actions/workflows/ci.yml?query=branch%3Amain)

A Python library that backs the provided `awx` command line client.

This repository is an **unofficial** fork of the `awxkit` directory of
[ansible/awx](https://github.com/ansible/awx), extracted (with history) at
upstream release `24.6.1` and maintained independently for
**Python 3.13 and 3.14**. It is not affiliated with, or endorsed by,
Red Hat or the Ansible project.

The distribution is named `alanbchristie-awxkit` (the PyPI name `awxkit`
belongs to upstream), but it installs the same `awxkit` Python package and
`awx`/`akit` commands as the original — so don't install it alongside
upstream `awxkit`.

For more information on installing the CLI and building the docs on how to use it, look [here](./awxkit/cli/docs).

License
-------

The original work is copyright the AWX project contributors (Red Hat, Inc.)
and is licensed under the [Apache License 2.0](./LICENSE.md). The files in
this repository have been modified from the upstream originals — notably for
Python 3.13/3.14 compatibility and standalone packaging — and those
modifications are distributed under the same Apache License 2.0.
