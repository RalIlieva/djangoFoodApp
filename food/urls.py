from .import views
from django.urls import path

app_name = 'food'
urlpatterns =[
    path('', views.IndexClassView.as_view(), name='index'),
    path('<int:pk>/', views.FoodDetail.as_view(), name='detail'),
    path('add', views.CreateItem.as_view(), name='create_item'),
    # edit items - initial version
    # path('update/<int:id>/', views.update_item, name='update_item'),
    path('update/<int:pk>/', views.UpdateView.as_view(), name='update_item'),
    # delete
    path('delete/<int:id>/', views.delete_item, name='delete_item'),
    path('item/<int:item_pk>/comment/<int:comment_pk>/delete/', views.delete_comment, name='delete_comment'),
]