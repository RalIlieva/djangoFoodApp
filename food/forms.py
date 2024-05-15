from django import forms
from .models import Item, Comment

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'item_desc', 'item_image', 'cooking_time']
        labels = {
            "item_name": "Item Name",
            'item_desc': 'Description',
            'item_image': "Item Image",
            'cooking_time': 'Cooking time'
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields =['text']
        labels ={
            'text': 'Leave your comment here'
        }