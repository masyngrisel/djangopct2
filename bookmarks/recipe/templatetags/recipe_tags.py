from django import template
from ..models import Report
from django.db.models import Count
import markdown
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.simple_tag
def get_most_commented_reports(count=5):
    return Report.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]
    
@register.simple_tag
def total_reports():
    return Report.published.count()

@register.inclusion_tag('recipe/report/latest_reports.html')
def show_latest_reports(count=5):
    latest_posts = Report.published.order_by('-publish')[:count]
    return {'latest_reports': show_latest_reports}