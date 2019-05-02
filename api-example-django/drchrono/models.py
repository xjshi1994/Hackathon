from django.db import models


# Add your models here


class AppointmentsHistory(models.Model):
    appointment_id = models.CharField(primary_key=True, max_length=100)
    patient_name = models.CharField(max_length=100)
    status = models.CharField(max_length=100, blank=True, default="")
    scheduled_time = models.DateTimeField()
    arrive_time = models.DateTimeField(null=True, default=None)
    waiting_duration = models.IntegerField(null=True, default=None)
    session_start_time = models.DateTimeField(null=True, default=None)
    session_duration = models.IntegerField(null=True, default=None)


class PatientBody(models.Model):
    patient_id = models.IntegerField()
    body_weight = models.IntegerField()
    height = models.IntegerField()
    blood_pressure = models.IntegerField()
    heart_rate_bpm = models.IntegerField()
    body_temperature = models.FloatField()
    timestamp = models.DateTimeField()


class List(models.Model):
    item = models.CharField(max_length=100)
    finished = models.BooleanField(default=False)
