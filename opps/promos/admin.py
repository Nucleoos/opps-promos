# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.admin.widgets import FilteredSelectMultiple
from opps.core.widgets import OppsEditor

from .models import Promo, Answer, PromoContainer
from opps.core.admin import PublishableAdmin
from opps.core.admin import apply_opps_rules
from opps.images.generate import image_url


class PromoAdminForm(forms.ModelForm):
    mirror_site = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(),
        widget=FilteredSelectMultiple(_("Mirror site"), is_stacked=False),
        required=False
    )

    class Meta:
        model = Promo
        widgets = {
            "headline": OppsEditor(),
            "description": OppsEditor(),
            "confirmation_email_html": OppsEditor(),
            "rules": OppsEditor(),
            "result": OppsEditor()
        }


@apply_opps_rules('promos')
class PromoContainerInline(admin.TabularInline):
    model = PromoContainer
    fk_name = 'promo'
    raw_id_fields = ['container']
    actions = None
    extra = 1
    classes = ('collapse',)
    verbose_name = _(u'Promo Container')
    verbose_name_plural = _(u'Promo Containers')


@apply_opps_rules('promos')
class PromoAdmin(PublishableAdmin):
    form = PromoAdminForm
    prepopulated_fields = {"slug": ["title"]}
    list_display = ['title', 'channel', 'date_available',
                    'date_end', 'published', 'preview_url']
    list_filter = ["date_end", "date_available", "published", "channel"]
    search_fields = ["title", "headline", "description"]
    exclude = ('user',)
    raw_id_fields = ['main_image', 'banner', 'channel']
    inlines = [PromoContainerInline]

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'title', 'slug')}),

        (_(u'Content'), {
            'classes': ('extrapretty'),
            'fields': (('main_image', 'image_thumb'), ('banner', 'banner_thumb'), 'tags')}),

        (_(u'Headline'), {
            'classes': ('extrapretty'),
            'fields': ('headline', )}),

        (_(u'Description'), {
            'classes': ('extrapretty'),
            'fields': ('description',)}),

        (_(u'Rules'), {
            'classes': ('extrapretty'),
            'fields': ('rules',)}),

        (_(u'Relationships'), {
            'fields': ('channel',)}),

        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', ('date_available', 'date_end'),
                       'order', 'form_type',
                       'display_answers',
                       'countdown_enabled',
                       'mirror_site')}),

        (_(u'Participation'), {
            'fields': ('send_confirmation_email', 'confirmation_email_txt',
                       "confirmation_email_html", "confirmation_email_address")}),

        (_(u'Result'), {
            'classes': ('extrapretty'),
            'fields': ('result', 'display_winners')}),
    )

    readonly_fields = ['image_thumb', 'banner_thumb']

    def banner_thumb(self, obj):
        if obj.banner:
            return u'<img width="60px" height="60px" src="{0}" />'.format(
                image_url(obj.banner.archive.url, width=60, height=60))
        return _(u'No Image')
    banner_thumb.short_description = _(u'Thumbnail')
    banner_thumb.allow_tags = True

    def queryset(self, request):
        """Limit objects to those that belong to the request's user."""
        qs = super(PromoAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@apply_opps_rules('promos')
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['promo', 'user', 'date_insert',
                    'published', 'is_winner', 'image_thumb']
    list_filter = ["promo", "date_insert", "published", 'is_winner']
    search_fields = ["answer", "answer_url", "user"]
    raw_id_fields = ['promo', 'user']

    def image_thumb(self, obj):
        return obj.get_file_display()
    image_thumb.short_description = _(u'Upload')
    image_thumb.allow_tags = True


admin.site.register(Promo, PromoAdmin)
admin.site.register(Answer, AnswerAdmin)
