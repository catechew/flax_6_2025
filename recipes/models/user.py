from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

"""
Model used for user authentication, and team member related information.
"""

class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    # Gender field for AI avatar
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
        blank=True
    )

    # Age field for AI avatar
    AGE_CHOICES = [
        ('young', '18-30'),
        ('middle', '31-50'),
        ('senior', '51+'),
    ]

    age_range = models.CharField(
        max_length=10,
        choices=AGE_CHOICES,
        default='young',
        blank=True
    )

    AVATAR_TYPE_CHOICES = [
        ('initials', 'Initials'),
        ('random', 'Random'),
        ('ai', 'AI Generated'),
    ]

    avatar_type = models.CharField(
        max_length=10,
        choices=AVATAR_TYPE_CHOICES,
        default='initials',
        help_text='Type of avatar to display'
    )

    # Profile picture upload
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    # Random avatar seed (for random avatars)
    avatar_seed = models.CharField(
        max_length=50,
        blank=True,
        help_text='Seed for random avatar generation'
    )

    # Following relationship - many to many
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    class Meta:
        """ Model options. """
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def avatar_url(self, size=120):
        """ Return avatar URL based on user preference. """
        if self.profile_picture:
            return self.profile_picture.url

        if self.avatar_type == 'initials':
            return self._get_initials_avatar_url(size)

        if self.avatar_type == 'random' and self.avatar_seed:
            return f"https://api.dicebear.com/7.x/avataaars/svg?seed={self.avatar_seed}&size={size}"

        if self.avatar_type == 'ai':
            return self._get_ai_avatar_url(size)

        return self._get_initials_avatar_url(size)

    def _get_initials_avatar_url(self, size):
        """ Generate initials-based avatar URL. """
        name = f"{self.first_name} {self.last_name}".strip()
        return f"https://ui-avatars.com/api/?name={name}&size={size}&background=f15034&color=fff&bold=true&rounded=true"

    def _get_ai_avatar_url(self, size):
        """ Generate AI avatar URL based on age and gender. """
        import hashlib
        seed = int(hashlib.md5(self.username.encode()).hexdigest()[:8], 16)
        gender_path = 'men' if self.gender == 'M' else 'women'
        photo_num = self._get_photo_number_for_age(seed)
        return f"https://randomuser.me/api/portraits/{gender_path}/{photo_num}.jpg"

    def _get_photo_number_for_age(self, seed):
        """ Calculate photo number based on age range. """
        if self.age_range == 'young':
            return (seed % 33) + 1
        if self.age_range == 'middle':
            return (seed % 33) + 34
        return (seed % 33) + 67

    def mini_gravatar(self):
        """ Return a URL to a miniature version of the user's gravatar. """
        return self.avatar_url(size=60)

    def follow(self, user):
        if user != self:
            self.following.add(user)

    def unfollow(self, user):
        self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(pk=user.pk).exists()

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()