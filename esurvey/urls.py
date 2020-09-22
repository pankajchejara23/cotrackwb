from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required
from .views import CompleteForm, CREATE_FORMS

urlpatterns = [
    path("esurvey/<link>/start", login_required(views.surveyForm), name="survey_form"),
    path("esurvey/<link>", login_required(views.generateSurvey), name="get_survey"),
    path("projects/<project_id>/<type>", login_required(views.projectAction), name="project_action"),
    path("projects/filter/<filter>", login_required(views.filterProjects), name="project_filter"),
    path("projects/session", login_required(views.createSession), name='create_session'),
    path("sessions/", login_required(views.overview), name="project_home"),  # <-- added
    path("sessions/<session_id>", login_required(views.getSession), name="session_page"),
    path("sessions/activate/<session_id>", login_required(views.activateSession), name="session_activate"),
    path("sessions/deactivate/<session_id>", login_required(views.deactivateSession), name="session_deactivate"),
    path("projects/new/",login_required(CompleteForm.as_view(CREATE_FORMS)), name="create"),
    path("enter/",views.enterForm, name="student_entry"),
    path("enter/pad/<group_id>",views.getPad, name="student_pad"),
    path("projects/report", login_required(views.getReport), name="project_report"),
    path("audio/", views.model_form_upload, name='views.model_form_upload'),
    path("audiolist/", views.list_files, name='views.list_files'),
    path("upload/", views.uploadAudio, name='upload_audio'),
    ]