# Skywipe

Skywipe is a work-in-progress Python 3.13+ CLI that helps you wipe data from your Bluesky account using the AT Protocol.

## Warning

This tool performs destructive operations. Only use it if you intend to erase data from your Bluesky account.

## Requirements

- Python 3.13+
- [`atproto`](https://atproto.blue/en/latest/)
- [`uv`](https://github.com/astral-sh/uv) for dependency and virtual environment management

## Setup

```bash
git clone https://git.kharec.info/Kharec/skywipe.git
cd skywipe
uv sync  # creates a local virtualenv and installs dependencies
```

## How to run

When installation will be worked out, you'll be able to :

```bash
skywipe all            # target everything
skywipe configure      # create configuration
skywipe posts          # only posts
skywipe medias         # only posts with medias
skywipe likes          # only likes
skywipe reposts        # only reposts
skywipe follows        # only follows
```

While it's being developed, you can use the tool using `uv` :

```bash
uv run main.py all            # target everything
uv run main.py configure      # create configuration
uv run main.py posts          # only posts
uv run main.py medias         # only posts with medias
uv run main.py likes          # only likes
uv run main.py reposts        # only reposts
uv run main.py follows        # only follows
```

### Configuration

If you run the tool for the first time, it will prompt you to use `skywipe configure` to create the configuration file, which is located in `~/.config/skywipe/`.

It looks like this :

```yaml
handle: your_handle
password: your_password
batch_size: 10
delay: 1
verbose: true
```

BE SURE TO USE A [BLUESKY APP PASSWORD](https://blueskyfeeds.com/faq-app-password) FOR OBVIOUS SECURITY REASONS.

## Roadmap

- [ ] build cli parameter management
- [ ] handle configuration logic
- [ ] sign in to at protocol
- [ ] delete posts in groups
- [ ] only delete posts with media
- [ ] remove likes
- [ ] remove reposts
- [ ] unfollow accounts
- [ ] make `all` run the other commands
- [ ] add simple progress and logging
- [ ] add safeguards like confirmations and clear dry-run info
- [ ] installation and run process

## License

This project is licensed under the GPLv3+ License. See the [LICENSE](LICENSE) file for details.
