from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
import requests
from .forms import ImageCreateForm
from .models import Image

from actions.utils import create_action


@login_required
def image_create(request):
    if request.method == 'POST':
        # form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.recipe = form.cleaned_data['recipe']  # associate the recipe
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            # redirect to new created image detail view
            return redirect(new_image.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form},
    )

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    recipe = image.recipe
    return render(
        request,
        'images/image/detail.html',
        {'section': 'images', 'image': image},
    )


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # If AJAX request and page out of range
            # return an empty page
            return HttpResponse('')
        # If page out of range return last page of results
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(
            request,
            'images/image/list_images.html',
            {'section': 'images', 'images': images},
        )
    return render(
        request,
        'images/image/list.html',
        {'section': 'images', 'images': images},
    )
    
    

from django.shortcuts import render
from .models import Image

def bookmarked_images(request):
    if request.user.is_authenticated:
        bookmarked_images = request.user.images_liked.all()
    else:
        bookmarked_images = []

    return render(request, 'images/image/bookmarked_images.html', {'bookmarked_images': bookmarked_images})