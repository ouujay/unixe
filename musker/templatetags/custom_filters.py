from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def linkify_hashtags(text):
    return mark_safe(re.sub(r"#(\w+)", r'<a href="/hashtag/\1/">#\1</a>', text))
