# Project introduction

### Doctor Dashboard
The dashboard is an interactive and informative page for the doctor, 
showing the information of today's appointments (scheduled time, patient name, status).  
  
The doctor is able to see the current status of arrived patients and update the status to IN SESSION or COMPLETED.  
  
The page also providing the doctor with patient body information and appointment statistic data featuring getting the patients' body information by hovering the mouse on the 
patient name and getting the waiting time and in session time by clicking the clock icon. The average waiting time 
for today shows up on the top-right of the table.  
  
There is a application to-do list where the doctor is able to add to-do things. It helps the doctor not to forget a thing and boosts his/her
productivity.
  





### Check-in kiosk
The kiosk is an interactive and informative page for the patient.
Patient first need to input his/her first name, last name and date of birth to confirm the identity.  
  
After logging in, there showing all appointments for the patient. Before check in, the patient is required to
update the demographic information and fill his/her body information(weight, body temperature, blood pressure etc.)
  
The patient is also able to add new valid appointment by filling the duration, datetime. But if there is 
a conflict of scheduling the appointment. The warning message will pop up.




### Requirements
- a free [drchrono.com](https://www.drchrono.com/sign-up/) account
- [docker](https://www.docker.com/community-edition) (optional)

### Dev environment Setup
Change the client id and secret key in docker/data/environment  
change the static variable and office id(For this project, I have the assumption having only one doctor)  
make migration  
docker-compose up

