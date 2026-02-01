from django.shortcuts import render, redirect
from django.contrib import messages
from  django.contrib.auth.decorators import login_required

from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import (EmptyPage,
                                   PageNotAnInteger,
                                   Paginator
                                   )
from django.http import HttpResponse
from actions.utils import create_action
import redis
from django.conf import settings

# connect to redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

def image_list(request):
    images = Image.objects.all()
    my_paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = my_paginator.page(page)
    except PageNotAnInteger:
        images = my_paginator.page(1)
    except EmptyPage:
        if images_only:
            # if AJAX request and page out of range
            # return an empty page
            return HttpResponse('')
        images = my_paginator.page(my_paginator.num_pages)
    if images_only:
        return render(
            request,
            'images/image/list_images.html',
            {
                'section':'images',
                'images': images
            }
        )
    return render(
        request,
        'images/image/list.html',
        {
            'section': 'images',
            'images': images
        }
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
                image.user_like.add(request.user)
                create_action(request.user, 'likes', image) #tracking user action
            else:
                image.user_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
        
        return JsonResponse({'status':'error'})

@login_required
def image_create(request):
    if request.method=='POST':
        # form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # assign current user to the item
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image) #new added to tract user action
            messages.success(request, 'Image added successfully 🎉')
            return redirect(new_image.get_absolute_url())
        
    else:
        # build form with data provided by the bookmarklet via get
        form = ImageCreateForm(data=request.GET)
    return render(
        request,
        'images/image/create.html',
        {
            'section':'images',
            'form':form
        }
        )
            
def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug= slug)
    total_views = r.incr(f'image: {image.id} :views')
    # Increment image ranking by 1
    r.zincrby('image_ranking', 1, image.id)
    return render(
        request,
        'images/image/detail.html',
        {
            'section':'image',
            'image':image,
            'total_views': total_views
        }
    )
@login_required
def image_ranking(request):
    # get image ranking dictionary
    image_ranking = r.zrange(
        'image_ranking', 0, -1,
        desc=True
    )[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    
    # get most viewed images
    most_viewed = list(
        Image.objects.filter(
            id__in=image_ranking_ids
        )
    )
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images',
         'most_viewed': most_viewed
        }
    )