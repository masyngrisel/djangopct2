from django.shortcuts import get_object_or_404, render
from .models import Report, Rating
from django.http import Http404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import ListView
from django.contrib.postgres.search import ( SearchVector, SearchQuery, SearchRank)
from .forms import CommentForm, EmailReportForm, SearchForm, RatingForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity

# Create your views here.
def report_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A')+ SearchVector('body', weight ='B')
            search_query = SearchQuery(query)
            results = (
                Report.published.annotate(similarity = TrigramSimilarity('title', query)
                                        ).filter(similarity__gt=0.1).order_by('-similarity')
            )
    return render(request, 'recipe/report/search.html', {'form':form, 'query':query, 'results':results})
            
def report_detail(request, year, month, day, report):
    report = get_object_or_404(Report, status=Report.Status.PUBLISHED,
    slug=report,
    publish__year=year,
    publish__month=month,
    publish__day=day)
    comments = report.comments.filter(active=True)
    form=CommentForm()
    report_tags_ids = report.tags.values_list('id', flat=True)
    similar_reports = Report.published.filter(
        tags__in = report_tags_ids
    ).exclude(id=report.id)
    similar_reports = similar_reports.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]
    return render(request, "recipe/report/detail.html", {"report": report, 'comments':comments, 'form':form, 'similar_reports': similar_reports})


def report_list(request, tag_slug=None):
    report_list = Report.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        report_list = report_list.filter(tags__in=[tag])
    paginator = Paginator(report_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        reports = paginator.page(page_number)
    except PageNotAnInteger:
        reports = paginator.page(1)
    except EmptyPage:
        reports = paginator.page(paginator.num_pages)
    return render(request, "recipe/report/list.html", {"reports": reports, 'tag':tag})

class ReportListView(ListView):
    """
    Alternative post list view
    """

    queryset = Report.published.all()
    context_object_name = 'reports'
    paginate_by = 3
    template_name = 'recipe/report/list.html'

def report_share(request, report_id):
    report = get_object_or_404(
        Report, 
        id=report_id,
        status=Report.Status.PUBLISHED
    )
    sent = False
    
    if request.method == 'POST':
        form = EmailReportForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            report_url = request.build_absolute_uri(
                report.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']}) recommends you read {report.title}"
            )
            message = (
                f"Read {report.title} at {report_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']],
            )
            sent = True
            
    else:
        form = EmailReportForm()
    return render(
        request,
        'recipe/report/share.html',
        {
            'report': report,
            'form':form,
            'sent': sent
        }
    )
    
@require_POST
def report_comment(request, report_id):
    report = get_object_or_404(Report, id=report_id, status = Report.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = report
        comment.save()
    return render(request, 'recipe/report/comment.html', {'post': report, 'form': form, 'comment':comment})

def rate_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    user = request.user
    success_message = None

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['value']
            existing_rating = Rating.objects.filter(report=report, user=user).first()
            if existing_rating:
                existing_rating.value = rating_value
                existing_rating.save()
            else:
                Rating.objects.create(report=report, user=user, value=rating_value)
            
            success_message = "Rating submitted successfully"
            return render(request, 'recipe/report/rate_report.html', {'form': form, 'report': report, 'success_message': success_message})

    else:
        form = RatingForm()

    return render(request, 'recipe/report/rate_report.html', {'form': form, 'report': report})