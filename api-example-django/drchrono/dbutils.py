from drchrono.models import AppointmentsHistory
from drchrono.models import PatientBody
from django.forms import models

"""
wrapper for the operations with the database
"""
class dbutils():

    def __init__(self):
        pass

    """
    check the appointments, if it is the  new one to db; else do nothing
    """

    @staticmethod
    def add(appointments_list):
        """

        :param appointments_list:
        :return:
        """

        for appointment_object in appointments_list:

            appointment_detail = appointment_object["appointment_detail"]
            patient_detail = appointment_object["patient_detail"]
            doctor_detail = appointment_object["doctor_detail"]

            try:
                AppointmentsHistory.objects.get(appointment_id=appointment_detail["id"])

            except AppointmentsHistory.DoesNotExist:
                appointment_object = AppointmentsHistory(appointment_id=appointment_detail["id"],
                                                         patient_name=patient_detail["first_name"] + " " +
                                                                      patient_detail["last_name"],
                                                         scheduled_time=appointment_detail["scheduled_time"]
                                                         )
                appointment_object.save()

    """
    update the field by appointment_id
    """

    @staticmethod
    def update(appointment_id, params):
        try:
            data_entry = AppointmentsHistory.objects.get(appointment_id=appointment_id)

            for key, value in params.items():
                if key == appointment_id:
                    raise Exception("appointment_id can not be revised")
                data_entry.__setattr__(key, value)
            data_entry.save()

        except AppointmentsHistory.DoesNotExist:
            raise Exception("appointment_id not found")

    """
    query the field by appointment_id
    """

    @staticmethod
    def query(appointment_id, field):

        try:
            appointment_object = AppointmentsHistory.objects.get(appointment_id=appointment_id)
            return appointment_object.__getattribute__(field)

        except AppointmentsHistory.DoesNotExist:
            raise Exception("appointment_id can not be found")


class PatientBodyDbUtils():
    """
    add patient body condition
    """

    @staticmethod
    def add(body_info):
        patient_body_object = PatientBody(patient_id=body_info['patient_id'],
                                          body_weight=body_info['body_weight'],
                                          height=body_info['height'],
                                          blood_pressure=body_info['blood_pressure'],
                                          heart_rate_bpm=body_info['heart_rate_bpm'],
                                          body_temperature=body_info['body_temperature'],
                                          timestamp=body_info['timestamp'])
        patient_body_object.save()

    """
    get the most recent patient body condition
    """

    @staticmethod
    def get_recent_body_info(patient_id):
        try:
            patient_body_info = PatientBody.objects.filter(patient_id=patient_id).latest("timestamp")
            og_dict = models.model_to_dict(patient_body_info)
            return {k: og_dict[k] for k in ("body_weight",
                                            "height",
                                            "blood_pressure",
                                            "heart_rate_bpm",
                                            "body_temperature")}
        except Exception:
            # no result
            return {}
