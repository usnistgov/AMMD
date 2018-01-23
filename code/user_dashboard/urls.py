################################################################################
#
# File Name: urls.py
# Application: dashboard
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#		  Xavier SCHMITT
#		  xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from user_dashboard.views import UserDashboardPasswordChangeFormView
from user_dashboard.views import dashboard_otherusers_records

urlpatterns = patterns('',
    url(r'^$', 'user_dashboard.views.my_profile'),
    url(r'^my-profile$', 'user_dashboard.views.my_profile'),
    url(r'^my-profile/edit', 'user_dashboard.views.my_profile_edit'),
    url(r'^my-profile/change-password', UserDashboardPasswordChangeFormView.as_view(
        template_name='dashboard/my_profile_change_password.html', success_url='/dashboard/my-profile')),
    url(r'^forms', 'user_dashboard.views.dashboard_my_forms'),
    url(r'^records$', 'user_dashboard.views.dashboard_records'),
    url(r'^dashboard_otherusers_records', dashboard_otherusers_records, name='dashboard_otherusers_records'),
    url(r'^templates$', 'user_dashboard.views.dashboard_templates'),
    url(r'^types$', 'user_dashboard.views.dashboard_types'),
    url(r'^files$', 'user_dashboard.views.dashboard_files'),
    url(r'^toXML$', 'user_dashboard.ajax.dashboard_toXML'),
    url(r'^edit_information$', 'user_dashboard.ajax.edit_information'),
    url(r'^delete_object$', 'user_dashboard.ajax.delete_object'),
    url(r'^modules$', 'user_dashboard.views.dashboard_modules'),
    url(r'^detail$', 'user_dashboard.views.dashboard_detail_record'),
    url(r'^otheruserdetail$', 'user_dashboard.views.dashboard_detail_record_otherusers'),#details of other users records
    url(r'^delete_result', 'user_dashboard.ajax.delete_result'),
    url(r'^update_publish', 'user_dashboard.ajax.update_publish'),
    url(r'^update_unpublish', 'user_dashboard.ajax.update_unpublish'),
    url(r'^change-owner-record', 'user_dashboard.views.change_owner_record'),
)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += staticfiles_urlpatterns()
