from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'item_desc', 'item_price', 'item_image']
        labels = {
            "item_name": "Item Name",
            'item_desc': 'Description',
            'item_price': "Price",
            'item_image': "Item Image",
        }
