from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from .models import Item, Comment
from .forms import ItemForm, CommentForm
from django.template import loader
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Avg
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse_lazy
# used only for function-based views - manually set the pagination
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ClassBased View
class IndexClassView(ListView):
    model = Item
    template_name = 'food/index.html'
    context_object_name = 'item_list'
    paginate_by = 3

    def get_queryset(self):
        query = self.request.GET.get('q')
        # add - in front of ratings to make descending order - first the highest rating
        queryset = Item.objects.filter(ratings__isnull=False).order_by('-ratings__average')

        if query:
            queryset = queryset.filter(
                Q(item_name__icontains=query) |
                Q(item_desc__icontains=query) |
                Q(user_name__username__icontains=query)
            )

        if not queryset.exists():  # If no results found
            messages.info(self.request, 'No results found.')

        return queryset


# Detail Base View
class FoodDetail(DetailView):
    model = Item
    template_name = 'food/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()

#         Increment view count
        item.views +=1
        item.save()

        comments = item.comments.all()
        context['comments'] = comments
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        # item = self.get_object()
        self.object = self.get_object()  # Ensure self.object is set
        item = self.object
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.item = item
            comment.save()
            return redirect('food:detail', pk=item.pk)
        else:
            context = self.get_context_data()
            context['comment_form'] = comment_form
            return self.render_to_response(context)


# Generic Create View
class CreateItem(LoginRequiredMixin, CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'food/item-form.html'

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        form.instance.publish_date = timezone.now()
        return super().form_valid(form)


class UpdateItem(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'food/item-form.html'
    success_url = reverse_lazy('food:index')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user_name != request.user:
            return HttpResponseForbidden("You are not allowed to update this item.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.update_date = timezone.now()
        return super().form_valid(form)

# Initial version
# def update_item(request, id):
#     item = Item.objects.get(id=id)
#     form = ItemForm(request.POST or None, instance=item)
#
#     if form.is_valid():
#         form.instance.update_date = timezone.now()
#         form.save()
#         return redirect('food:index')
#
#     return render(request,'food/item-form.html',{'form': form,'item': item})


class DeleteItem(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = 'food/item-delete.html'
    success_url = reverse_lazy('food:index')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user_name != request.user:
            return HttpResponseForbidden("You are not allowed to delete this item.")
        return super().dispatch(request, *args, **kwargs)

# First approach for deletion - with html for confirmation and check in html
# @login_required
# def delete_item(request, id):
#     item = Item.objects.get(id=id)
#
#     if request.method == 'POST':
#         item.delete()
#         return redirect('food:index')
#
#     return render(request, 'food/item-delete.html', {'item': item})


# Second approach for deletion - checks are here, no confirmation - JS needed.
@login_required
def delete_comment(request, item_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk, item_id=item_pk)
    if comment.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    comment.delete()
    return redirect('food:detail', pk=item_pk)