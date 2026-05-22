from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product, Category, Color, Size, ProductVariation, ProductImage
from accounts.models import UserProfile

class SellerDashboardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller', password='password')
        self.profile = UserProfile.objects.create(user=self.user, is_seller=True)
        self.category = Category.objects.create(name='Electronics')
        self.color = Color.objects.create(name='Red', code='#FF0000')
        self.size = Size.objects.create(name='L')
        self.client = Client()
        self.client.login(username='seller', password='password')

    def test_add_product_with_variations(self):
        url = reverse('add_product')
        data = {
            'name': 'Test Product',
            'category': self.category.id,
            'description': 'Description',
            'price': '100.00',
            'stock': '10',
            # Variations formset
            'variations-TOTAL_FORMS': '1',
            'variations-INITIAL_FORMS': '0',
            'variations-MIN_NUM_FORMS': '0',
            'variations-MAX_NUM_FORMS': '1000',
            'variations-0-color': self.color.id,
            'variations-0-size': self.size.id,
            'variations-0-stock': '5',
            # Images formset
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
        }
        response = self.client.post(url, data)
        if response.status_code != 302:
            print("Response Status Code:", response.status_code)
            if 'form' in response.context:
                print("Form Errors:", response.context['form'].errors)
            if 'variation_formset' in response.context:
                print("Variation Errors:", response.context['variation_formset'].errors)
            if 'image_formset' in response.context:
                print("Image Errors:", response.context['image_formset'].errors)
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(name='Test Product')
        self.assertEqual(product.variations.count(), 1)
        variation = product.variations.first()
        self.assertEqual(variation.color, self.color)
        self.assertEqual(variation.stock, 5)
        # Check if parent product stock is updated via signal/save override
        self.assertEqual(product.stock, 5)
