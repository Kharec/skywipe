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

    @staticmethod
    def has_media(post_record):
        embed = getattr(post_record, 'embed', None)
        if not embed:
            return False

        embed_type = getattr(embed, 'py_type', None)
        if embed_type:
            embed_type_base = embed_type.split('#')[0]

            if embed_type_base in PostAnalyzer.MEDIA_TYPES:
                return True

            if embed_type_base in ('app.bsky.embed.recordWithMedia', 'app.bsky.embed.record_with_media'):
                media = getattr(embed, 'media', None)
                if media:
                    media_type = getattr(media, 'py_type', None)
                    if media_type:
                        media_type_base = media_type.split('#')[0]
                        if media_type_base in PostAnalyzer.MEDIA_TYPES:
                            return True

        for attr in ('images', 'video', 'external'):
            if hasattr(embed, attr):
                return True
            if isinstance(embed, dict) and embed.get(attr):
                return True

        return False

    @staticmethod
    def has_quote(post_record):
        embed = getattr(post_record, 'embed', None)
        if not embed:
            return False

        embed_type = getattr(embed, 'py_type', None)
        if embed_type:
            embed_type_base = embed_type.split('#')[0]
            if embed_type_base in PostAnalyzer.QUOTE_TYPES:
                return True

        return (hasattr(embed, 'record') or
                (isinstance(embed, dict) and embed.get('record')))
