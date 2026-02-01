from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm #LoginForm

from django.contrib.auth import authenticate, login, get_user_model
from django.views.decorators.http import require_POST
from actions.utils import create_action
from actions.models import Action

from django.contrib.auth.decorators import login_required
from .models import Profile, Contact
from django.contrib import messages



# # custom user validation 
# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(
#                 request,
#                 username = cd['username'],
#                 password = cd['password']
#             )
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return HttpResponse('Authenticated seccessfully !')
#                 else:
#                     return HttpResponse('Disabled account !')
#             else:
#                 return HttpResponse("Invalid login (user not found!)")
#     else:
#         form = LoginForm()
#     return render(
#         request,
#         'account/login.html',
#         {'form': form}
#         )

# registration from forms.py->views.py -> urls.py -> templates
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            # save user object
            new_user.save()
            create_action(new_user, 'joined goldbookmark')
            # create the user profile
            Profile.objects.create(user=new_user)
            return render(
                request,
                'account/register_done.html',
                {'new_user':new_user}
            )
        else:
            return render(
                request,
                'account/register.html',
                {'user_form':user_form}
            )
    else:
        user_form = UserRegistrationForm()
        return render(
            request,
            'account/register.html',
            {'user_form':user_form}
        )

@login_required
def dashboard(request):
    """
    Render the dashboard page populated with recent actions performed by users the
    current user follows.

    This view function performs the following steps in order:

    1. Excludes the current user's own actions from consideration by starting from
        Action.objects.exclude(user=request.user). This ensures the dashboard does
        not show actions that the user themselves performed.

    2. Retrieves the IDs of users that the current user is following via
        request.user.following.values_list('id', flat=True). The attribute
        `following` is expected to be a related manager (e.g., a ManyToMany or a
        reverse ForeignKey relation) that yields User (or Profile) instances. The
        flat=True option returns a plain sequence of IDs.

    3. If the current user follows at least one other user (i.e., `following_ids`
        is non-empty), the base action queryset is filtered to include only actions
        whose user_id is in that set. If `following_ids` is empty, no additional
        filtering is applied and the initial exclusion of the current user remains
        in effect.

    4. Optimizes ORM access before evaluation by calling:
        - select_related('user', 'user__profile'): follows SQL JOINs to fetch the
          foreign-key related User and User.profile objects in the same query,
          avoiding additional per-row queries when the template accesses attributes
          like action.user or action.user.profile.
        - prefetch_related('target'): triggers a separate prefetch query for the
          'target' relation (commonly used for GenericForeignKey or reverse
          relations), preventing N+1 query patterns when the template accesses
          action.target.

    5. Limits the result set to the first ten items via slicing [:10]. Note that
        the order in which those first ten items are selected depends on the
        queryset's ordering; if Action has no default ordering defined in its
        Meta, the slice will be arbitrary unless an explicit order_by(...) is
        applied elsewhere.

    6. Renders the 'account/dashboard.html' template with a context containing:
        - 'section': 'dashboard' (a string typically used by the template to mark
          which navigation section is active)
        - 'actions': the (evaluated) queryset or list of up to ten Action objects,
          ready for iteration and display in the template.

    Return value:
         django.http.HttpResponse -- the rendered dashboard page.

    Notes and assumptions:
    - This view assumes request.user is an authenticated user (e.g., the view is
      intended to be decorated with @login_required). If request.user is
      AnonymousUser, access to request.user.following or other attributes may
      raise errors.
    - Because select_related and prefetch_related are used, database access is
      optimized to reduce N+1 query problems; the exact number of queries depends
      on the relationships and whether related objects exist.
    - The current function does not implement pagination beyond a fixed 10-item
      slice and does not explicitly control ordering; consider adding ordering and
      a paginated response for larger datasets or better UX.
    - The function performs no writes to the database and has no side effects
      beyond executing read queries and rendering a template.
    """
    # display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list(
        'id',
        flat=True
    )
    if following_ids:
        # if user is following others, retrieve only their actions
        following_action = actions.filter(user_id__in=following_ids)
    following_action=actions.select_related(
        'user', 'user__profile'
    ).prefetch_related('target')[:10]
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard', 'actions': following_action}
    )

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(
                request,
                "Profile updated successfully 🎉"
            )
        else:
            messages.error(
                request,
                "Error updating your profile."
            )
    else:
        user_form = UserEditForm(
            instance=request.user
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile
        )
        
    return render(
        request,
        'account/edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action=='follow':
                Contact.objects.get_or_create(
                    user_from = request.user,
                    user_to=user
                )
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(
                    user_from = request.user,
                    user_to = user
                ).delete()
            return JsonResponse({'status': 'ok'})
        except user.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})

User = get_user_model()
@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(
        request,
        'account/user/list.html',
        {'section':'people',
         'users':users
        }
    )
@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(
        request,
        'account/user/detail.html',
        {
            'section': 'people',
            'user': user
        }
    )