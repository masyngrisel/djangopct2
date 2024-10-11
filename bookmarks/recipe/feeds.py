from django.db.models.base import Model
from django.utils.safestring import SafeText
import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Report

class LatestReportsFeed(Feed):
    
    title = 'My  recipe blog'
    link = reverse_lazy('recipe:report_list')
    description = 'New posts of my recipe blog'
    
    def items(self):
        return Report.published.all()[:5]
    
    def item_title(self, item):
        return item.title 
    
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)
    
    def item_pubdate(self, item):
        return item.publish