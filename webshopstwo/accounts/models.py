import random
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Verification(models.Model):
    """
    مدل برای ذخیره کد تایید موقت
    """
    phone = models.CharField(max_length=11, unique=True, verbose_name="شماره موبایل")
    code = models.CharField(max_length=4, verbose_name="کد تایید")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} -> {self.code}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="کاربر")
    first_name = models.CharField(max_length=100,blank=True,null=True,verbose_name="نام")
    last_name = models.CharField(max_length=100, blank=True, null=True,verbose_name="نام خانوادگی")
    email = models.EmailField( blank=True, null=True, verbose_name="پست الکترونیک")
    national_code = models.CharField(max_length=10, blank=True,  null=True,  verbose_name="کد ملی")
    card_number = models.CharField(max_length=16,  blank=True,  null=True,  verbose_name="شماره کارت" )
    newsletter = models.BooleanField(  default=False,   verbose_name="دریافت خبرنامه")

    def __str__(self):
        return f"پروفایل {self.user.username}"



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            Profile.objects.create(user=instance)