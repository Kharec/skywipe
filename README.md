# Skywipe

Skywipe is a work-in-progress Python 3.13+ CLI that helps you wipe data from your Bluesky account using the AT Protocol SDK.

## Warning

This tool performs destructive operations. Only use it if you intend to erase data from your Bluesky account.

## Requirements

Check [pyproject.toml](pyproject.toml).

You can use `uv` to install dependencies:

```bash
git clone https://git.kharec.info/Kharec/skywipe.git
cd skywipe
uv sync
```

## How to run

While it's being developed, you can use the tool using `uv` :

```bash
uv run python -m skywipe.cli all            # target everything
uv run python -m skywipe.cli configure      # create configuration
uv run python -m skywipe.cli posts          # delete posts
uv run python -m skywipe.cli medias         # delete posts with medias
uv run python -m skywipe.cli likes          # undo likes
uv run python -m skywipe.cli reposts        # undo reposts
uv run python -m skywipe.cli quotes         # delete quotes
uv run python -m skywipe.cli follows        # unfollow all
uv run python -m skywipe.cli bookmarks      # delete bookmarks
```

Use the `--yes` flag to skip the confirmation prompt and proceed with the operation.

A log of the operations will be saved in `~/.cache/skywipe/skywipe.log`.

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

## Roadmap

- [x] build cli parameter management
- [x] handle configuration logic
- [x] sign in to at protocol
- [x] delete posts in batch
- [x] only delete posts with media
- [x] undo likes
- [x] undo reposts
- [x] delete quotes
- [x] unfollow accounts
- [x] remove bookmarks
- [x] make `all` run the other commands
- [x] add simple progress and logging
- [x] add safeguards (confirmation, dry-run flag)
- [ ] decent code architecture
- [ ] installation and run process

## License

This project is licensed under the GPLv3+ License. See the [LICENSE](LICENSE) file for details.
