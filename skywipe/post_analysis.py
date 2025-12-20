"""Post analysis utilities for Skywipe"""


class PostAnalyzer:
    MEDIA_TYPES = {
        'app.bsky.embed.images',
        'app.bsky.embed.video',
        'app.bsky.embed.external'
    }

    QUOTE_TYPES = {
        'app.bsky.embed.record',
        'app.bsky.embed.recordWithMedia',
        'app.bsky.embed.record_with_media'
    }

    QUOTE_WITH_MEDIA_TYPES = {
        'app.bsky.embed.recordWithMedia',
        'app.bsky.embed.record_with_media'
    }

    @staticmethod
    def _get_embed(post_record):
        return getattr(post_record, 'embed', None)

    @staticmethod
    def _get_embed_type_base(embed):
        embed_type = getattr(embed, 'py_type', None)
        if embed_type:
            return embed_type.split('#')[0]
        return None

    @staticmethod
    def has_media(post_record):
        embed = PostAnalyzer._get_embed(post_record)
        if not embed:
            return False

        embed_type_base = PostAnalyzer._get_embed_type_base(embed)
        if embed_type_base:
            if embed_type_base in PostAnalyzer.MEDIA_TYPES:
                return True

            if embed_type_base in PostAnalyzer.QUOTE_WITH_MEDIA_TYPES:
                media = getattr(embed, 'media', None)
                if media:
                    media_type_base = PostAnalyzer._get_embed_type_base(media)
                    if media_type_base and media_type_base in PostAnalyzer.MEDIA_TYPES:
                        return True

        for attr in ('images', 'video', 'external'):
            if hasattr(embed, attr):
                return True
            if isinstance(embed, dict) and embed.get(attr):
                return True

        return False

    @staticmethod
    def has_quote(post_record):
        embed = PostAnalyzer._get_embed(post_record)
        if not embed:
            return False

        embed_type_base = PostAnalyzer._get_embed_type_base(embed)
        if embed_type_base and embed_type_base in PostAnalyzer.QUOTE_TYPES:
            return True

        return (hasattr(embed, 'record') or
                (isinstance(embed, dict) and embed.get('record')))
