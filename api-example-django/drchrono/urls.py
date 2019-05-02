from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin

admin.autodiscover()
import views
import django

urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url(r'patient_check_in/', views.PatientCheckIn.as_view(), name='patient_check_in'),
    url(r'patient_home/', views.PatientHome.as_view(), name='patient_home'),
    url(r'update_patient_info/', views.UpdatePatientInfo.as_view(), name="update_patient_info"),
    url(r'update_appointment_status.html', views.UpdateAppointmentStatus.as_view(), name="update_appointment_status"),
    url(r'demographic_form.html/', views.Demographic.as_view(), name='demographic_form'),
    url(r'time_stat.html/', views.TimeStat.as_view(), name='time_stat'),
    url(r'to_do_list.html', views.ToDoList, name='to_do_list'),
    url(r'delete/(?P<list_id>\d+)/$', views.delete, name='delete'),
    url(r'cross_off/(?P<list_id>\d+)/$', views.cross_off, name='cross_off'),
    url(r'uncross/(?P<list_id>\d+)/$', views.uncross, name='uncross'),
    url(r'new_appointment_form.html/', views.NewAppointmentForm.as_view(), name='new_appointment_form'),
    url(r'add_appointment_status.html/', views.AddAppointmentStatus.as_view(), name='add_appointment_status'),

]
