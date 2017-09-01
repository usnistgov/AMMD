from django.conf.urls import patterns, url
from django.contrib import admin

admin_urls = patterns(
    'schema_viewer.admin_views',
    url(r'^manage_visible_default/$', 'manage_visible_default', name='manage_visible_default'),
    url(r'^upload_oxygen/$', 'upload_oxygen', name='upload_oxygen')
)

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
