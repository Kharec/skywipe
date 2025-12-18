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

When installation will be worked out, you'll be able to :

```bash
skywipe all            # target everything
skywipe configure      # create configuration
skywipe posts          # delete posts
skywipe medias         # delete posts with medias
skywipe likes          # undo likes
skywipe reposts        # undo reposts
skywipe quotes         # delete quotes
skywipe follows        # unfollow all
skywipe bookmarks      # delete bookmarks
```

While it's being developed, you can use the tool using `uv` :

```bash
uv run main.py all            # target everything
uv run main.py configure      # create configuration
uv run main.py posts          # delete posts
uv run main.py medias         # delete posts with medias
uv run main.py likes          # undo likes
uv run main.py reposts        # undo reposts
uv run main.py quotes         # delete quotes
uv run main.py follows        # unfollow all
uv run main.py bookmarks      # delete bookmarks
```

### Configuration

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
- [ ] undo reposts
- [ ] delete quotes
- [ ] unfollow accounts
- [ ] remove bookmarks
- [ ] make `all` run the other commands
- [ ] add simple progress and logging
- [ ] add safeguards like confirmations and clear dry-run info

Once it's done, we'll think:

- [ ] decent code architecture
- [ ] installation and run process

## License

This project is licensed under the GPLv3+ License. See the [LICENSE](LICENSE) file for details.
