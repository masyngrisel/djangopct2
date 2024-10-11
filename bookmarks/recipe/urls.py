from django.urls import path
from . import views
from .feeds import LatestReportsFeed
from .views import rate_report

app_name = 'recipe'

urlpatterns = [
    path('', views.report_list, name="report_list"),
    path('tag/<slug:tag_slug>/', views.report_list, name='report_list_by_tag'),
    #path('', views.PostListView.as_view(), name='post_list'),
    path("<int:year>/<int:month>/<int:day>/<slug:report>/", views.report_detail, name="report_detail"),
    path('<int:report_id>/share/', views.report_share, name='report_share'),
    path('<int:report_id>/comment/',views.report_comment, name='report_comment'),
    path('feed/', LatestReportsFeed(), name = 'report_feed'),
    path('search/', views.report_search, name='report_search'),
    path('report/<int:report_id>/rate/', rate_report, name='rate_report'),
    
]
