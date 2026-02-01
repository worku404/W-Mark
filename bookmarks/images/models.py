from django.db import models
from django.utils.text import slugify
from django.conf import settings

from django.urls import reverse

class Image(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='images_created',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField(max_length=2000)
    image = models.ImageField(upload_to='images/%Y/%m/%d')
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    # populate the most liked images
    total_likes = models.PositiveIntegerField(default=0)
    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes']),
        ]
        ordering = ['-created']
    def save(self, *args, **kwargs):
        if not self.slug or not self.slug.strip():
            self.slug = slugify(self.title, allow_unicode=True) or str(self.pk)
        super().save(*args, **kwargs)
            
    user_like = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='images_liked',
        blank=True
    )
    def get_absolute_url(self):
        return reverse("images:detail", 
                       args=[self.id, self.slug]
                    )
    
    def __str__(self) -> str:
        return self.title
    
# Create your models here.
