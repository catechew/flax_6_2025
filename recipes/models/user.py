from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

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

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M',
        help_text='Select your gender'
    )

    AGE_CHOICES = [
        ('young', '18-30'),
        ('middle', '31-50'),
        ('senior', '51+'),
    ]

    age_range = models.CharField(
        max_length=10,
        choices=AGE_CHOICES,
        default='young',
        help_text='Select your age range'
    )

    following = models.ManyToManyField(
        'self',
        symmetrical=False,  # If A follows B, B doesn't automatically follow A
        related_name='followers',
        blank=True
    )
    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        import hashlib
        seed = int(hashlib.md5(self.username.encode()).hexdigest()[:8], 16) % 70
        return f"https://i.pravatar.cc/{size}?img={seed}"

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)

    def follow(self, user):
        """Follow another user."""
        if user != self:
            self.following.add(user)
    def unfollow(self, user):
        """Unfollow a user."""
        self.following.remove(user)

    def is_following(self, user):
        """Check if this user is following another user."""
        return self.following.filter(pk=user.pk).exists()

    def follower_count(self):
        """Return tot n. of followers."""
        return self.followers.count()

    def following_count(self):
        """Return the n. of users followed by this user."""
        return self.following.count()