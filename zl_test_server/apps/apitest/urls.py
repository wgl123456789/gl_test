from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

router = DefaultRouter(trailing_slash=False)
router.register('project',views.ProjectViewSets,basename="project")
router.register('host',views.HostViewSets,basename="host")
router.register('api',views.ApiViewSets,basename="api")

app_name = "apitest"
urlpatterns = [
    path("index",views.IndexView.as_view(),name="index"),
    path('run/api/<int:api_id>',views.RunApiView.as_view(),name="run_api"),
    path('run/case/<int:case_id>',views.RunCaseView.as_view(),name="run_case"),
    path('case',views.CaseView.as_view(),name='case'),
    path('case/<int:case_id>',views.CaseView.as_view(),name="edit_case"),
    path('record',views.RecordView.as_view(),name="record"),
    path('task',views.CrontabTaskView.as_view(),name="task"),
    path('task/<int:task_id>',views.CrontabTaskView.as_view(),name="update_task"),
    path('task/<int:task_id>/<int:target_status>',views.StartStopTaskView.as_view(),name="task_status"),
] + router.urls