from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='banners/')
    link_url = models.CharField(max_length=500, default='/')
    button_text = models.CharField(max_length=50, default='Shop Now')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=100, default='Uncategorized')
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class HomeSlider(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='sliders/')
    link_url = models.CharField(max_length=500, default='/')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        # Keep data in the original store_homeslider table
        db_table = 'store_homeslider'

    def __str__(self):
        return self.title


class PromotionCard(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='promotions/')
    link_url = models.CharField(max_length=500, default='/')
    badge_text = models.CharField(max_length=50, blank=True, help_text="e.g. NEW, -20%, HOT")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        # Keep data in the original store_promotioncard table
        db_table = 'store_promotioncard'

    def __str__(self):
        return self.title

class AboutPage(models.Model):
    # Singleton Model
    hero_title = models.CharField(max_length=200, default="Empowering Better Health at Home")
    mission_text = models.TextField(blank=True)
    vision_text = models.TextField(blank=True)
    hero_image_1 = models.ImageField(upload_to='about/', blank=True, null=True)
    hero_image_2 = models.ImageField(upload_to='about/', blank=True, null=True)

    services_title = models.CharField(max_length=200, default="Quality is our priority")
    services_subtitle = models.CharField(max_length=500, blank=True)

    feature1_tagline = models.CharField(max_length=100, default="Features")
    feature1_title = models.CharField(max_length=200, default="Faster Free Delivery")
    feature1_description = models.TextField(blank=True)
    feature1_bullet1 = models.CharField(max_length=200, blank=True)
    feature1_bullet2 = models.CharField(max_length=200, blank=True)
    feature1_bullet3 = models.CharField(max_length=200, blank=True)
    feature1_image1 = models.ImageField(upload_to='about/', blank=True, null=True)
    feature1_image2 = models.ImageField(upload_to='about/', blank=True, null=True)

    app_section_title = models.CharField(max_length=200, default="App Is Available For Free In App | Play Store")
    app_section_description = models.TextField(blank=True, default="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
    app_image_1 = models.ImageField(upload_to='about/', blank=True, null=True, help_text="Image inside first phone")
    app_image_2 = models.ImageField(upload_to='about/', blank=True, null=True, help_text="Image inside second phone")
    play_store_link = models.URLField(blank=True)
    app_store_link = models.URLField(blank=True)
    feature2_tagline = models.CharField(max_length=100, default="Features")
    feature2_title = models.CharField(max_length=200, default="Focus on Customer Satisfaction")
    feature2_description = models.TextField(blank=True)
    feature2_bullet1 = models.CharField(max_length=200, blank=True)
    feature2_bullet2 = models.CharField(max_length=200, blank=True)
    feature2_bullet3 = models.CharField(max_length=200, blank=True)
    feature2_image = models.ImageField(upload_to='about/', blank=True, null=True)
    feature2_youtube_link = models.URLField(blank=True, help_text="YouTube link for the video button")

    team_title = models.CharField(max_length=200, default="Meet Our Team")
    team_subtitle = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return "About Page Content"

class AboutStat(models.Model):
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='stats')
    value = models.CharField(max_length=50, help_text="e.g. 120+, 100M, 99%")
    label = models.CharField(max_length=100, help_text="e.g. Years of Experience")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class AboutService(models.Model):
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='services')
    icon_class = models.CharField(max_length=50, help_text="FontAwesome class, e.g. fas fa-truck")
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class AboutTeamMember(models.Model):
    about_page = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='about/')
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Testimonial(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_role = models.CharField(max_length=100, blank=True, help_text="e.g. Digital Marketer")
    review_text = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.customer_role}"
