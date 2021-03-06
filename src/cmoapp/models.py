"""All models for myapp Django application.
"""
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator,ValidationError
import datetime
from datetime import timedelta

#all models have automatically add an auto-increment id unless another field is explicitly specified as primary key
#note, on_delete assigns a Function 'Callback'
#note, no fking clue in the django tutorial that says you can add a null option, only says field options are
#avaliable to all field types, but no explict example wtf
#note, if you want a FK that is null, you have to set blank=true so that validation will not be triggered

class Account(models.Model):
    TYPES = (
        ('Analyst','Analyst'),
        ('Operator', 'Operator'),
        ('Chief', 'Chief')
    )
    login = models.CharField(max_length=100)
    password = models.CharField(max_length=1024)
    type = models.CharField(max_length=20, choices=TYPES)

    class Meta:
        ordering = ['login']
    def __str__(self):
        return '{}'.format(self.login)

class CrisisType(models.Model):
    #Attributes
    name = models.CharField(max_length=50)
    def __str__(self):
        return '{}'.format(self.name)

#has nothing but a bunch of foreign keys such keys much wow
#Crisis ID
class Crisis(models.Model):
    #analyst is FK to crisis. This enables analyst to be deleted once the crisis is resolved
    #name = models.TextField()
    crisis_title = models.CharField(max_length=50,null=True)
    analyst = models.OneToOneField(Account,blank=True,null=True,limit_choices_to={'type':'Analyst'}, on_delete=models.SET_NULL)
    STATUS = (
        ('Clean-up','Clean Up'),
        ('Ongoing','Ongoing'),
        ('Resolved', 'Resolved')
    )
    status = models.CharField(max_length=20, choices=STATUS)
    external_agencies = models.TextField(null=True, blank=True)
    #class Meta:
     #   ordering = ['analyst']

    def injuries(self):
        try:
            return self.efupdate_set.latest('datetime').totalInjured
        except(EFUpdate.DoesNotExist):
            return None

    def deaths(self):
        try:
            return self.efupdate_set.latest('datetime').totalDeaths
        except(EFUpdate.DoesNotExist):
            return None

    def __str__(self):
        return 'ID: {} - assigned to: {}'.format(self.pk, self.analyst)

    def latestPlan(self):
        return self.actionplan_set.latest('id')

class CrisisReport(models.Model):
    #attributes
    description = models.TextField()
    datetime = models.DateTimeField()
    latitude = models.DecimalField(max_digits=12, decimal_places=8)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    radius = models.IntegerField(verbose_name="Radius(Metres)", validators=[MinValueValidator(0)])
    #Relations, can have no crisis assigned for the sake of testi

    crisis = models.ForeignKey(Crisis,null=True,blank=True,on_delete=models.CASCADE)
    crisisType = models.ForeignKey(CrisisType,null=True,blank=True,on_delete=models.DO_NOTHING)

    def __str__(self):
        return 'ID: {} - {} - Crisis {} - Type: {}'.format(self.pk,self.description,self.crisis,self.crisisType)


#The response plan of the crsis.
#The deployment id is the action plan id
class ActionPlan(models.Model):
    #attributes

    #plan Number supports the CMO-PMO API as their endpoint is expecting "<<CrisisID>><<planNumber>> where "
    #where planNumber is the running number of the plan related to its crisis
    plan_number = models.IntegerField(validators=[MinValueValidator(1)], editable=False)
    description = models.TextField(null=True,blank=True)
    STATUS= (
        ('Planning','Planning'),
        ('CORequest','Requesting CO'),
        ('PMORequest','Requesting PMO'),
        ('Rejected','Rejected'),
        ('PMOApproved','Approved')
    )
    outgoing_time = models.DateTimeField(editable=False, null=True)
    status = models.CharField(max_length=20, choices=STATUS)
    resolution_time = models.DurationField()
    projected_casualties = models.IntegerField(validators=[MinValueValidator(0)])
    #Relations
    TYPES = (
        ('Combat', 'Combat'),
        ('Clean-up','Clean Up'),
        ('Resolved','Resolved')
    )
    type = models.CharField(max_length=20, choices=TYPES)
    crisis = models.ForeignKey(Crisis, on_delete= models.CASCADE)
    def abridged_description(self):
        if(len(self.description) < 140):
            return self.description
        else:
            return self.description[:140] + "..."

    def __str__(self):
        return 'ID: {} | Internal Plan Number: {} | Type: {} | Status: {} | Crisis ID: {} | Abridged Description: {} '.format(
            self.pk,
            self.plan_number,
            self.type,
            self.get_status_display(),
            self.crisis.id,
            self.abridged_description()
        )

    #Custom Model
    def clean(self, *args, **kwargs):
        # add custom validation here
        try:
            if self.status == "Planning" and ActionPlan.objects.filter(crisis=self.crisis,status="Planning").count() > 1:
                raise ValidationError("There can only be 1 Action Plan in the planning phase")
        except Crisis.DoesNotExist:
            pass    #Do nothing if there are no crisis found
        super(ActionPlan, self).clean(*args, **kwargs)

    #Method intended to be private
    def _nextPlanNumber(self):
        return self.crisis.actionplan_set.all().count() + 1

    def save(self, *args, **kwargs):
        if not self.plan_number: #only set the plan number if not set
            self.plan_number = self._nextPlanNumber()
        super().save(*args, **kwargs)  # Call the "real" save() method.

class Comment(models.Model):
    text = models.TextField()
    authors = (
        ('PMO','Prime Minister\'s Office'),
        ('CO','Chief Officer')
    )
    author = models.CharField(max_length=20, choices=authors)
    #timeCreated = models.DateTimeField(auto_now=True/auto_now_add=True) not used cause it causes the field to not be seen
    #on the DB/ admin site, it can still be referenced (hard to debug/ check)
    timeCreated = models.DateTimeField(default=timezone.now,editable=False)
    #If the CO comments, then it is rejected by CO. If PMO comments, then PMO has rejected.
    actionPlan = models.OneToOneField(ActionPlan, on_delete= models.CASCADE)

    def abridged(self):
        return self.description[:140] + "..."

    def __str__(self):
        return 'ID: {} - Author: {} - Comment: {} for Action Plan: {}'.format(self.id, self.author,self.text, self.actionPlan.id)

    def timefrom(self):
        now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        difference = (now - self.timeCreated).total_seconds()
        #return hours
        if int(difference/3600) >= 23:
            return self.timeCreated.strftime('Posted on %d %b %Y, at %I:%M %p')
        elif int(difference/3600) >= 1:
            return '{} hours ago...'.format(int(difference / 3600))
        elif int(difference/60) >= 1:
            return '{} minutes ago...'.format((int(difference / 60)))
        else:
            return '{} seconds ago...'.format(int (difference))

class Force(models.Model):
    name = models.CharField(primary_key=True, max_length=200)
    #Current Utilisation can be NULL, in the event that EF cannot provide, then the field is set to NULL and Blank
    currentUtilisation = models.DecimalField(null=True,blank=True, max_digits=5, decimal_places=2)
    def __str__(self):
        return '{}'.format(self.name);
    def available(self):
        return 100-self.currentUtilisation;

#Force deployment tracks how much force to deploy for an action plan
class ForceDeployment(models.Model):
    #a force can only be deleted after all force deployments are deleted
    name = models.ForeignKey(Force, on_delete= models.PROTECT)
    recommended = models.DecimalField(max_digits=5, decimal_places=2)
    max = models.DecimalField(max_digits=5, decimal_places=2)
    actionPlan =  models.ForeignKey(ActionPlan, on_delete= models.CASCADE)

    def __str__(self):
        return 'ID: {} | Name: {} | Action Plan: {}'.format(self.pk,self.name, self.actionPlan)

    def clean(self, *args, **kwargs):
        # add custom validation here

        if self.recommended > self.max:
            raise ValidationError("Recommended amount cannot be greater than Max amount")
        super(ForceDeployment, self).clean(*args, **kwargs)

class EFUpdate(models.Model):
    #Attributes
    datetime = models.DateTimeField()
    affectedRadius = models.DecimalField(max_digits=12,decimal_places=2, verbose_name="Affected Radius")
    totalInjured = models.IntegerField(verbose_name="Total Injured")
    totalDeaths = models.IntegerField(verbose_name="Total Deaths")
    duration =  models.DurationField(null=True)
    actionPlan = models.ForeignKey(ActionPlan,null=True,on_delete = models.SET_NULL)
    #i leave this here in case the action plan can be deleted. we can thus still have a reference back to cris
    crisis = models.ForeignKey(Crisis, on_delete =  models.CASCADE)
    description = models.TextField()
    #We are removing types and adding a request
    TYPES = (
        ('Request','Request'),
        ('Notification','Notification')
    )
    type = models.CharField(choices=TYPES, max_length=40)
    def __str__(self):
        return 'ID: {}'.format(self.pk)

    def timefrom(self):
        now = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        difference = (now - self.datetime).total_seconds()
        #return hours
        if int(difference/3600) >= 23:
            return self.datetime.strftime('Posted on %d %b %Y, at %I:%M %p')
        elif int(difference/3600) >= 1:
            return '{} hours ago...'.format(int(difference / 3600))
        elif int(difference/60) >= 1:
            return '{} minutes ago...'.format(int(difference / 60))
        else:
            return '{} seconds ago...'.format(int (difference))

#Force Utilization tracks how much each force is being used for the current action plan
class ForceUtilization(models.Model):
    name = models.ForeignKey(Force,on_delete= models.CASCADE)
    utilization = models.DecimalField(max_digits=5, decimal_places=2)
    update = models.ForeignKey(EFUpdate, on_delete=models.CASCADE)

    def __str__(self):
        return 'ID: {} | Reported Utilization: {}%'.format(self.name, self.utilization);


class Notifications(models.Model):
    title = models.TextField()
    text = models.TextField()
    _for = models.ForeignKey(Account, on_delete=models.CASCADE)
    new = models.BooleanField(default=True)
    time_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.title)