from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language


CACHE_PREFIX = 'chunks_'

class Chunk(models.Model):
    """
    A Chunk is a piece of content associated
    with a unique key that can be inserted into
    any template with the use of a special template
    tag
    """
    key = models.CharField(_('key'), max_length=255, unique=True, 
                           help_text=_("A unique name for this chunk of content"))
    content = models.TextField(_('content'), blank=True)


    def __unicode__(self):
        return self.key
    
    def save(self, *args, **kwargs):
        # cache invalidation on save
        cache.delete(CACHE_PREFIX + self.key)
        for language in settings.LANGUAGES:
            cache.delete(CACHE_PREFIX + self.key + language[0])

        super(Chunk, self).save(*args, **kwargs)
    
    
    @staticmethod
    def get(key):
        cache_key = CACHE_PREFIX + key + get_language()
        content = cache.get(cache_key)
        if content is None:
            obj, c_ = Chunk.objects.get_or_create(key=key, defaults={'content': key})
            cache.set(cache_key, obj.content)
            content = obj.content
        return content
