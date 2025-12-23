# Skywipe

Skywipe is a Python 3.13+ CLI that helps you wipe data from your Bluesky account using the AT Protocol SDK.

**Warning:** This tool performs _**destructive operations**_.

Only use it if you intend to permanently erase data from your Bluesky account.

## Requirements

Python 3.13+.

The rest of the dependencies are listed in [pyproject.toml](pyproject.toml).

## Installation

Use [`pipx`](https://pipx.pypa.io/latest/installation/) to install `skywipe`:

```bash
pipx install git+https://git.kharec.info/Kharec/skywipe.git
```

Run the tool and see available commands with:

```bash
skywipe -h
```

Use the `--yes` flag to skip the confirmation prompt and proceed with the operation. A log of the operations will be saved in `~/.cache/skywipe/skywipe.log`.

## Configuration

If you run the tool for the first time, it will prompt you to use `skywipe configure` to create the configuration file, which is located in `~/.config/skywipe/config.yml` :

```yaml
handle: your_handle
password: your_password
batch_size: 10
delay: 1
verbose: true
```

BE SURE TO USE A [BLUESKY APP PASSWORD](https://blueskyfeeds.com/faq-app-password) FOR OBVIOUS SECURITY REASONS.

## Hacking

You can use `uv` to install dependencies:

```bash
git clone https://git.kharec.info/Kharec/skywipe.git
cd skywipe
uv sync
```

Run unit tests with:

```bash
uv sync --extra dev
uv run pytest
```

If you want to test your changes, you can run the tool with:

```bash
uv run python -m skywipe.cli -h
uv run python -m skywipe.cli all
# or any other command
```

## License

This project is licensed under the GPLv3+ License. See the [LICENSE](LICENSE) file for details.
