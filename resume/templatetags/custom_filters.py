from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})



@register.filter
def humanize_criteria(value):
    """
    Converts snake_case criteria names into human-readable titles.
    Example: "consistency_flow" -> "Consistency & Flow"
    """
    # Replace underscores with spaces and capitalize each word
    value = value.replace('_', ' ').title()
    
    # Custom replacements for specific cases
    replacements = {
        "Ats": "ATS",
        "And": "&",
    }
    
    for old, new in replacements.items():
        value = value.replace(old, new)
    
    return value