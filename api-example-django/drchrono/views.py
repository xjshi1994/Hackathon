from django.contrib import messages
from utils import *
from dbutils import *
from django.contrib import messages
from forms import DemographicForm, ListForm, AddForm
from drchrono.models import List
from django.shortcuts import render, redirect

# static variable for the status of the appointment
STATUS_BLANK = ""
STATUS_ARRIVED = "Arrived"
STATUS_IN_SESSION = "In Session"
STATUS_COMPLETED = "Complete"

# For this Hackathon only has one doctor and one office. These variables are needed to add new appointment.
DOCTOR_ID = 242548
OFFICE_ID = 257827


# synchronize the local db and remote db
def db_sync(appointment_id, params):
    helper = utils()
    dbutils.update(appointment_id, params)
    helper.change_appointment_status(appointment_id, params['status'])


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        helper = utils()

        # get doctor info
        doctor = helper.get_doctor(DOCTOR_ID)
        # get all today's appointments for the doctor
        appointments_iterator = helper.get_all_appointments(doctor_id=DOCTOR_ID)
        # iterate
        result = helper.get_appointments_render(appointments_iterator)

        # doctor first name and last name for the welcome
        kwargs['first_name'] = doctor['first_name']
        kwargs['last_name'] = doctor['last_name']
        kwargs['appointments'] = result
        kwargs["size"] = len(result)
        # get average waiting time for today
        kwargs['average_waiting_time'] = helper.get_average_waiting_time(result)

        return kwargs


class PatientCheckIn(TemplateView):
    """
    patient's appointments info page
    """
    template_name = "patient_check_in.html"

    def get_context_data(self, **kwargs):
        kwargs = super(PatientCheckIn, self).get_context_data(**kwargs)
        helper = utils()

        # get first_name and last_name from url
        first_name = self.request.GET.get("first_name")
        last_name = self.request.GET.get("last_name")
        full_name = first_name + " " + last_name

        # get date_of_birth from url
        date_of_birth = self.request.GET.get("date_of_birth")

        # get all appointments
        try:
            appointments_iterator = helper.get_all_appointments(first_name, last_name, date_of_birth)
        except Exception:
            # indication of whether there exists appointment today. 1 denote there is no appointment today
            kwargs["err"] = 1
            return kwargs

        result = helper.get_appointments_render(appointments_iterator)

        # compare the newest result with db, if there is new data, add it.
        dbutils.add(result)

        # pass all appointment to the page
        kwargs["appointments"] = result

        # patient name
        kwargs["last_name"] = last_name
        kwargs["first_name"] = first_name
        kwargs["pid"] = helper.get_patient(first_name, last_name, date_of_birth)["id"]
        # size for no appointments
        kwargs["size"] = len(result)
        return kwargs


class PatientHome(TemplateView):
    """
    check-in page allows the patient to input first name, last name and DOB
    """
    template_name = "patient_home.html"


class UpdatePatientInfo(TemplateView):
    """
    show info of updating after the patient check in
    """
    template_name = "update_patient_info.html"

    def get_context_data(self, **kwargs):
        helper = utils()
        kwargs = super(UpdatePatientInfo, self).get_context_data(**kwargs)
        my_request_get = self.request.GET
        # get appointment id
        appointment_id = my_request_get["appointment_id"]

        # get current time
        current_time = helper.get_current_time()

        # update in the local db hange the status on the remote db
        db_sync(appointment_id, {"status": STATUS_ARRIVED, "arrive_time": current_time})
        helper.change_appointment_status(appointment_id, STATUS_ARRIVED)

        # update the demographic data
        patient_id = my_request_get["patient_id"]
        helper.update_patient_info(patient_id, helper.get_init_dict(my_request_get))

        # update the patient body information to the database
        PatientBodyDbUtils.add(helper.get_body_info_dict(my_request_get))

        messages.success(self.request, "You have checked in successfully! Please wait patiently :-)")
        return kwargs


class UpdateAppointmentStatus(TemplateView):
    """
    show info of updating after the doctor edit the status of the appointment
    """
    template_name = "update_appointment_status.html"

    def get_context_data(self, **kwargs):
        helper = utils()
        kwargs = super(UpdateAppointmentStatus, self).get_context_data(**kwargs)

        # if the doctor click the update button
        appointment_id = self.request.GET["appointment_id"]

        if self.request.GET['start'] == '1':
            # start the session
            db_sync(appointment_id, {"status": STATUS_IN_SESSION})

            # update the session start time
            dbutils.update(appointment_id, {"session_start_time": helper.get_current_time()})

            # get waiting time and update waiting_duration
            arrive_time = dbutils.query(appointment_id, "arrive_time")
            waiting_duration = helper.get_duration(arrive_time, helper.get_current_time())
            dbutils.update(appointment_id, {"waiting_duration": waiting_duration})

        else:
            # end the session
            db_sync(appointment_id, {"status": STATUS_COMPLETED})

            # get session time
            session_start_time = dbutils.query(appointment_id, "session_start_time")
            session_time = helper.get_duration(session_start_time, helper.get_current_time())
            dbutils.update(appointment_id, {"session_duration": session_time})

        messages.success(self.request, "You have updated the appointment status successfully!")
        return kwargs


class Demographic(TemplateView):
    """
    form which allows patient to input his/her demographic data
    """
    template_name = "demographic_form.html"

    def get_context_data(self, **kwargs):
        helper = utils()
        kwargs = super(Demographic, self).get_context_data(**kwargs)
        appointment_id = self.request.GET['appointment_id']
        patient_id = self.request.GET['patient_id']
        patient_detail = helper.get_patient_id(patient_id)

        # get the recent body info
        boiler_plate_body = PatientBodyDbUtils.get_recent_body_info(patient_id)

        boiler_plate_important = helper.get_init_dict(patient_detail)
        # give the patient a boilerplate
        form = DemographicForm(initial=helper.merge(boiler_plate_body, boiler_plate_important))
        kwargs['form'] = form
        kwargs['appointment_id'] = appointment_id
        kwargs['patient_id'] = patient_id

        return kwargs


class TimeStat(TemplateView):
    """
    show the statistic of waiting and in_session time
    """
    template_name = "time_stat.html"

    def get_context_data(self, **kwargs):
        helper = utils()
        kwargs = super(TimeStat, self).get_context_data(**kwargs)
        appointment_id = self.request.GET['appointment_id']
        """
        get the time stat
        """
        kwargs["time_stat"] = helper.get_time_stat(appointment_id)
        return kwargs


class NewAppointmentForm(TemplateView):
    """
    a form which is used to new appointment
    """
    template_name = "new_appointment_form.html"

    def get_context_data(self, **kwargs):
        helper = utils()
        kwargs = super(NewAppointmentForm, self).get_context_data(**kwargs)
        patient_id = self.request.GET['patient_id']
        kwargs["patient_id"] = patient_id
        return kwargs


class AddAppointmentStatus(TemplateView):
    """
    post new appointment
    """
    template_name = "add_appointment_status.html"

    def get_context_data(self, **kwargs):
        helper = utils()
        kwargs = super(AddAppointmentStatus, self).get_context_data(**kwargs)
        my_request_get = self.request.GET

        # construct the params for post
        res = {'doctor': DOCTOR_ID,
               'duration': my_request_get['duration'],
               'exam_room': my_request_get['exam_room'],
               'office': OFFICE_ID,
               'patient': my_request_get['patient_id'],
               'scheduled_time': my_request_get['scheduled_time']}
        try:
            helper.post_appointment(res)
            messages.success(self.request, "You have added the appointment successfully!")
        except Exception:
            messages.error(self.request, "add failure!")
        kwargs["patient_id"] = my_request_get['patient_id']
        return kwargs


def ToDoList(request):
    """
    to-do list app
    """

    helper = utils()

    if request.method == 'POST':
        form = ListForm(request.POST or None)

        if form.is_valid():
            form.save()
            all_items = List.objects.all
            messages.success(request, "new item has been added successfully!!!")
            return render(request, "to_do_list.html", {'all_items': all_items})

    else:
        all_items = List.objects.all

        return render(request, "to_do_list.html", {'all_items': all_items})


def delete(request, list_id):
    """
    delete record
    """
    item = List.objects.get(pk=list_id)
    item.delete()
    messages.success(request, "item has been deleted!")
    return redirect('to_do_list')


def cross_off(request, list_id):
    """
    cross-off record
    """
    item = List.objects.get(pk=list_id)
    item.finished = True
    item.save()
    return redirect('to_do_list')


def uncross(request, list_id):
    """
    uncross the record
    """
    item = List.objects.get(pk=list_id)
    item.finished = False
    item.save()
    return redirect('to_do_list')
