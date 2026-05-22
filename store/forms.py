from django import forms
from .models import Product, ProductVariation, ProductImage, Color, Size, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'discount_price', 'stock', 'image', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'required': True}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01, 'required': True}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'required': True}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = ProductVariation
        fields = ['color', 'size', 'stock']
        widgets = {
            'color': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'required': True}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'color']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-select'}),
        }

ProductVariationFormSet = forms.inlineformset_factory(
    Product, ProductVariation, form=ProductVariationForm,
    extra=1, can_delete=True
)

ProductImageFormSet = forms.inlineformset_factory(
    Product, ProductImage, form=ProductImageForm,
    extra=1, can_delete=True
)
