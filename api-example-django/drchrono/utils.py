from django.shortcuts import redirect
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth
from drchrono.endpoints import DoctorEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.endpoints import PatientEndpoint
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from dbutils import *


class utils():

    def __init__(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        self.access_token = oauth_provider.extra_data['access_token']

    """
    get the only patient by first_name, last_name and date_of_birth
    """

    def get_patient(self, first_name=None, last_name=None, date_of_birth=None):

        api = PatientEndpoint(self.access_token)

        params = {'first_name': first_name, 'last_name': last_name, 'date_of_birth': date_of_birth}

        # grab one
        return next(api.list(params))

    """
    get all appointments on the current date
    
    either from patient: first_name, last_name, date_of_birth
    
    or from doctor: doctor_id
    
    """

    def get_all_appointments(self, first_name=None, last_name=None, date_of_birth=None, doctor_id=None):
        """
        :param : either {first_name: last_name: date_of_birth: } or {doctor_id: }
        :return: all appointments iterator
        """
        api = AppointmentEndpoint(self.access_token)

        # should be the current date.
        current_time = self.get_current_time()
        date = current_time.strftime("%Y-%m-%d")

        params = {}

        if doctor_id is not None:
            params = {'date': date, 'doctor': doctor_id}
        elif first_name is not None and last_name is not None and date_of_birth is not None:
            patient_details = self.get_patient(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth)
            patient_id = patient_details["id"]
            params = {'date': date, "patient": patient_id}
        else:
            raise Exception("Must provide first name, last name and date_of_birth OR doctor id")

        return api.list(params)

    """
    Get doctor information by his/her id
    """

    def get_doctor(self, doctor_id):
        """
        :param doctor_id: doctor id
        :return: doctor info
        """

        api = DoctorEndpoint(self.access_token)
        return api.fetch(doctor_id)

    """
    Get patient info by his/her id
    """

    def get_patient_id(self, patient_id):
        """
        :param patient_id:
        :return:
        """

        api = PatientEndpoint(self.access_token)
        return api.fetch(patient_id)

    """
    Use the id and Change the appointment'status to Arrived 
    """

    def change_appointment_status(self, appointment_id, status):
        """
        :param appointment_id: get the appointment_id from the url. status: status to update
        """

        api = AppointmentEndpoint(self.access_token)
        params = {"status": status}

        api.update(appointment_id, params, True)

    """
    every appointment object contains detailed information:
        1. appointment
        2. doctor
        3. patient
    """

    def get_appointments_render(self, apoointment_iterator):
        """
        :param apoointment_iterator: the iterator of the appointment
        :return:
        """
        # iterate the appointments
        result = []
        while True:
            try:
                # get the appointment info
                appointment_object = {}

                appointment = next(apoointment_iterator)

                appointment_object["appointment_detail"] = appointment
                appointment_object["doctor_detail"] = self.get_doctor(appointment["doctor"])
                appointment_object["patient_detail"] = self.get_patient_id(appointment["patient"])
                # append to the list
                # body info
                appointment_object["body_info"] = self.get_final_body_condition(appointment["patient"])

                result.append(appointment_object)

                if datetime.strptime(appointment["scheduled_time"],
                                     '%Y-%m-%dT%H:%M:%S') < self.get_current_time() and len(appointment["status"]) == 0:
                    appointment_object["is_late"] = "1"
                else:
                    appointment_object["is_late"] = "0"
            except StopIteration:
                break;

        return result

    """
    get current time
    """

    def get_current_time(self):
        return timezone.now();

    """
    calculate the elapsed time
    """

    def get_duration(self, start, end):
        """
        :param start: start time point
        :param end: end time point
        :return:
        """
        return (end - start).seconds // 60

    """
    give the form previous data(seldom change data), so that patient is able to type less.
    """

    def get_init_dict(self, patient_detail):
        res = {'first_name': patient_detail['first_name'], 'last_name': patient_detail['last_name'],
               'email': patient_detail['email'], 'gender': patient_detail['gender'],
               'address': patient_detail['address'], 'cell_phone': patient_detail['cell_phone'],
               'state': patient_detail['state']}
        return res

    """
    update the patient info to remote
    """

    def update_patient_info(self, patient_id, patient_info):
        api = PatientEndpoint(self.access_token)
        api.update(patient_id, patient_info, True)

    """
    substract body info from request dict
    """

    def get_body_info_dict(self, my_request_get):
        res = {
            'patient_id': my_request_get['patient_id'],
            'body_weight': my_request_get['body_weight'],
            'height': my_request_get['height'],
            'blood_pressure': my_request_get['blood_pressure'],
            'heart_rate_bpm': my_request_get['heart_rate_bpm'],
            'body_temperature': my_request_get['body_temperature'],
            'timestamp': self.get_current_time()
        }
        return res

    """
    get time stat by appointment_id
    """

    def get_time_stat(self, appointment_id):
        try:
            appointment_status = dbutils.query(appointment_id, "status")
            # if status is "

            if appointment_status == 'Arrived':
                arrived_time = dbutils.query(appointment_id, "arrive_time")
                waiting_duration = self.get_duration(arrived_time, self.get_current_time())
                res = {"waiting_duration": waiting_duration, "session_duration": ''}
            elif appointment_status == 'In Session':
                session_start_time = dbutils.query(appointment_id, "session_start_time")
                session_duration = self.get_duration(session_start_time, self.get_current_time())
                res = {"waiting_duration": dbutils.query(appointment_id, "waiting_duration"),
                       "session_duration": session_duration}
            elif appointment_status == 'Complete':
                res = {"waiting_duration": dbutils.query(appointment_id, "waiting_duration"),
                       "session_duration": dbutils.query(appointment_id, "session_duration")}
            else:
                res = {"waiting_duration": '', "session_duration": ''}
        except Exception:
            res = {"waiting_duration": '', "session_duration": ''}
        return res

    """
    get average waiting time
    """
    def get_average_waiting_time(self, appointments):
        waiting_time_sum = 0
        count = 0
        for appointment_object in appointments:
            time_stat = self.get_time_stat(appointment_object["appointment_detail"]["id"])
            if time_stat["waiting_duration"]:
                waiting_time_sum += int(time_stat["waiting_duration"])
                count += 1;

        # if there is no patient, waiting time should be 0
        if count == 0:
            return 0
        return waiting_time_sum / count

    """
    merge two dict
    """
    def merge(self, dict1, dict2):
        res = {}
        for k, v in dict1.items():
            res[k] = v
        for k, v in dict2.items():
            res[k] = v
        return res

    """
    add new appointment
    """

    def post_appointment(self, params):
        api = AppointmentEndpoint(self.access_token)
        api.create(data=params)

    """
    get body_condition
    """

    def get_final_body_condition(self, patient_id):
        res = PatientBodyDbUtils.get_recent_body_info(patient_id)
        if not res:
            res = {"body_weight": '',
                   "height": '',
                   "blood_pressure": '',
                   "heart_rate_bpm": '',
                   "body_temperature": ''}
        return res
