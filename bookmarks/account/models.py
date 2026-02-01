from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    photo = models.ImageField(
        upload_to = 'user/%Y/%m/%d/',
        blank = True
    )
    def __str__(self) -> str:
        return f'Profile of {self.user.username}'
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
        
class Contact(models.Model):
    """Represent a one-way "follow" (contact) relationship between two user accounts.
    Fields:
        user_from (ForeignKey): The user who initiates the follow (related_name='rel_from_set').
        user_to (ForeignKey): The user being followed (related_name='rel_to_set').
        created (DateTimeField): Timestamp when the follow was created (auto_now_add=True).
    Behavior and notes:
        - Deleting either user cascades and removes related Contact instances (on_delete=CASCADE).
        - The model defines an index on '-created' and a default ordering of ['-created'] to optimize
          queries that retrieve the most recent relationships first.
        - The relationship is directional; mutual follows require two Contact instances.
        - __str__ returns a human-readable string in the form '<user_from> follows <user_to>'.
    Common usage:
        - Get users a user follows: user.rel_from_set.all()
        - Get followers of a user: user.rel_to_set.all()
    """
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rel_from_set',
        on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rel_to_set',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']
    def __str__(self) -> str:
        return f'{self.user_from} follows {self.user_to}' 
    
user_model =get_user_model()
user_model.add_to_class(
    'following',
    models.ManyToManyField(
        'self',
        through=Contact,
        related_name='follower',
        symmetrical=False
    )
)