# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField
from validatorchain import ValidatorChain

from . import validators


avatar_min_max_dimension = {}
if validators.AVATAR_MIN_DIMENSION:
    avatar_min_max_dimension.update({
        'min_w': validators.AVATAR_MIN_DIMENSION[0],
        'min_h': validators.AVATAR_MIN_DIMENSION[1]
    })
    if validators.AVATAR_MAX_DIMENSION:
        avatar_help_text = _('Please upload an image with a side length between %(min_w)dx%(min_h)d px and %(max_w)dx%(max_h)d px.')
        avatar_min_max_dimension.update({
            'max_w': validators.AVATAR_MAX_DIMENSION[0],
            'max_h': validators.AVATAR_MAX_DIMENSION[1]
        })
    else:
        avatar_help_text = _('Please upload an image with a side length of at least %(min_w)dx%(min_h)d px.')
else:
    if validators.AVATAR_MAX_DIMENSION:
        avatar_help_text = _('Please upload an image with a side length of at most %(max_w)dx%(max_h)d px.')
        avatar_min_max_dimension.update({
            'max_w': validators.AVATAR_MAX_DIMENSION[0],
            'max_h': validators.AVATAR_MAX_DIMENSION[1]
        })
    else:
        avatar_help_text = ''
avatar_help_text = avatar_help_text % avatar_min_max_dimension


class Profile(models.Model):
    """
    A userprofile model that provides a short_info, twitter handle, website URL, avatar
    field and details about number/age of accompanying children

    This is also used as AUTH_PROFILE_MODULE.
    """
    user = models.OneToOneField(User)
    short_info = models.TextField(_('short info'), blank=True)
    avatar = ThumbnailerImageField(
        _('avatar'), upload_to='avatars', null=True, blank=True,
        help_text=avatar_help_text, validators=ValidatorChain()
            .add(validators.avatar_dimension)
            .add(validators.avatar_format, skip_on_error=True)
        )
    num_accompanying_children = models.PositiveIntegerField(_('Number of accompanying children'),
        null=True, blank=True, default=0)
    age_accompanying_children = models.CharField(_("Age of accompanying children"), blank=True, max_length=20)
    twitter = models.CharField(_("Twitter"), blank=True, max_length=20,
        validators=[validators.twitter_username])
    website = models.URLField(_("Website"), blank=True)
    organisation = models.TextField(_('Organisation'), blank=True)
    full_name = models.CharField(_("Full name"), max_length=255, blank=True)
    display_name = models.CharField(_("Display name"), max_length=255,
        help_text=_('What name should be displayed to other people?'),
        blank=True)
    addressed_as = models.CharField(_("Address me as"), max_length=255,
        help_text=_('How should we call you in mails and dialogs throughout the website?'),
        blank=True)
    accept_pysv_conferences = models.BooleanField(_('Allow copying to PySV conferences'),
        default=False, blank=True)
    accept_ep_conferences = models.BooleanField(_('Allow copying to EPS conferences'),
        default=False, blank=True)


@receiver(user_logged_in)
def show_logged_in_message(request, user, **kwargs):
    messages.success(request, _("You've logged in successfully."),
                     fail_silently=True)
