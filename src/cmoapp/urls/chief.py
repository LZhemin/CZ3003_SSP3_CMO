from django.conf.urls import url
from cmoapp.views import ChiefOfficerManager

urlpatterns = [
    url(r'^$', ChiefOfficerManager.index, name="Chief_Index"),
    url(r'^action_plans/(?P<pk>\d+)/$', ChiefOfficerManager.ActionPlanDetail.as_view(), name='Chief_Action_Plan_Detail'),
    url(r'^approve_action_plan/$', ChiefOfficerManager.ApproveActionPlan, name="Approve_Action_Plan"),
    url(r'^reject_action_plan/$', ChiefOfficerManager.RejectActionPlan, name="Reject_Action_Plan"),
    url(r'^reload_table/$', ChiefOfficerManager.ReloadTable, name="Reload_Table"),
    url(r'^reload_notification/$', ChiefOfficerManager.reload_notification, name="Reload_Notification"),
    url(r'^delete_notification/$', ChiefOfficerManager.delete_notification, name="Delete_Notification"),
    url(r'^reload_crisis/$', ChiefOfficerManager.ReloadCrisis, name="Reload_Crisis"),
    url(r'^select_crisischat/$', ChiefOfficerManager.select_crisischat, name="Select_Crisischat"),
    url(r'^get_efupdate_count/$', ChiefOfficerManager.get_efupdates_count, name="Get_EfUpdate_Count"),
    url(r'^get_efupdates/$', ChiefOfficerManager.get_efupdates, name="Get_EFUpdates"),
    url(r'^change_status/$', ChiefOfficerManager.change_status, name="Change_Status"),
    url(r'^send_deployment_plan/(?P<id>\d+)/$', ChiefOfficerManager.sendDeploymentPlan, name="Send_Deployment_Plan"),
    url(r'^historical_data/$', ChiefOfficerManager.getHistorical_data,name="display_historical_data"),
]