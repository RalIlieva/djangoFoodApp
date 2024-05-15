from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Item, Comment
from .forms import ItemForm, CommentForm
from django.template import loader
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.db.models import Avg
from django.utils import timezone

# ClassBased View
class IndexClassView(ListView):
    model = Item
    template_name = 'food/index.html'
    context_object_name = 'item_list'

    def get_queryset(self):
        # add - in front of ratings to make descending order - first the highest rating
        queryset = Item.objects.filter(ratings__isnull=False).order_by('-ratings__average')
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
        item = self.get_object()
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
class CreateItem(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'food/item-form.html'

    def form_valid(self, form):
        form.instance.user_name = self.request.user
        form.instance.publish_date = timezone.now()
        return super().form_valid(form)


def update_item(request, id):
    item = Item.objects.get(id=id)
    form = ItemForm(request.POST or None, instance=item)

    if form.is_valid():
        form.instance.update_date = timezone.now()
        form.save()
        return redirect('food:index')

    return render(request,'food/item-form.html',{'form': form,'item': item})


def delete_item(request, id):
    item = Item.objects.get(id=id)

    if request.method == 'POST':
        item.delete()
        return redirect('food:index')

    return render(request, 'food/item-delete.html', {'item':item})