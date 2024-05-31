from django import forms
from .models import Item, Comment
from ckeditor.widgets import CKEditorWidget

class ItemForm(forms.ModelForm):
    item_desc = forms.CharField(widget=CKEditorWidget(), label="Description")
    class Meta:
        model = Item
        fields = ['item_name', 'item_desc', 'item_image', 'cooking_time']
        labels = {
            "item_name": "Recipe Name",
            'item_desc': 'Description',
            'item_image': "Recipe Image",
            'cooking_time': 'Cooking time'
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields =['text']
        labels ={
            'text': 'Leave your comment here'
        }