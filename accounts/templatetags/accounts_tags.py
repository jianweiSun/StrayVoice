from django import template

register = template.Library()


@register.inclusion_tag('accounts/menu.html')
def show_menu(section):
    return {'section': section}


