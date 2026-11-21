from django import template

register = template.Library()


@register.filter
def dictkey(d, key):
    """Récupère d[key] dans un template (clé entière)."""
    try:
        return d.get(key, [])
    except AttributeError:
        return []
