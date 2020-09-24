from django.shortcuts import render
from django.http import HttpResponse
from .forms import CreateForm1,CreateForm2,CreateForm3,CreateForm4, lastForm, AnonyForm, SessionForm, AudioflForm
from formtools.wizard.views import SessionWizardView
from django import forms
from django.db import transaction
from .models import Project, Survey, Link, Submission, Session, SessionPin
from django.contrib import messages
import uuid
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.db.models import Count
from datetime import date
from django.db import transaction
import uuid
from django.core.files.storage import FileSystemStorage
from .models import Audiofl

CREATE_FORMS = (
    ("questionnaire", CreateForm1),
    ("product", CreateForm2),
    ("participants", CreateForm3),
    ("editq", CreateForm4),
    ("overview",lastForm))

TEMPLATES = {"questionnaire": "create.html",
             "product": "create.html",
             "participants": "create.html",
             "editq": "create.html",
             "overview": "overview.html"}



import os
from django.core.files.base import File
from django.shortcuts import render, redirect



def model_form_upload(request):
    if request.method == 'POST':
        form = AudioflForm(request.POST, request.FILES)
        print('function called')
        if form.is_valid():
            newform = form.save(commit=False)
            print('valid form')
            djfile = File(request.FILES['fl'])
            newform.fl.save(request.FILES['fl'].name, djfile)
            newform.save()
            print('data saved')

            # convert to fix the duration of audio
            file_path = newform.fl.path
            #os.system("/usr/bin/mv %s %s" % (file_path, (file_path + '.original')))
            #os.system("/usr/bin/ffmpeg -i %s -c copy -fflags +genpts %s" % ((file_path + '.original'), file_path))

            return redirect('/')
    else:
        form = AudioflForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })


def list_files(request):
    files = Audiofl.objects.all().order_by('uploaded_at')

    return render(request, 'list_files.html', {
        'files': files
    })




def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def getAnonyForm(request):
    if request.method == "POST":
        form = AnonyForm(request.POST)
        return HttpResponse('submitted')
    else:
        form = AnonyForm()
        return render(request,"anonymous-form.html",{'form':form})


# View to generate report for specific project_type
def getReport(request):
    ################################

    # code to generate report here




    ##################################
    return HttpResponse('Report will be provided here')

@transaction.atomic
def createSession(request):

    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            current_user = request.user
            s_name = form.cleaned_data['name']
            s_groups = form.cleaned_data['groups']
            s_description = form.cleaned_data['description']
            s = Session.objects.create(owner=current_user,name = s_name,groups = s_groups, description = s_description)


            while True:
                u_pin = uuid.uuid4().hex[:6].upper()
                objs = SessionPin.objects.filter(pin = u_pin)
                if objs.count() == 0:
                    break
            pin_obj = SessionPin.objects.create(session=s,pin=u_pin)
        messages.success(request, 'Project created successfully !')
        return redirect('project_home')
    else:
        form = SessionForm()
        return render(request,'session.html',{'form':form})


def filterProjects(request,filter):
    current_site = get_current_site(request)
    domain = current_site.domain
    if filter not in ['Running','Archived','Closed']:
        messages.error(request,'Incorrect filter applied.')
        return redirect('project_home')
    else:
        projects = []
        if filter == 'Running':
            projects = Project.objects.all().filter(end_date >= date.today())
            msg = 'Running projects are fetched successfully!'
        elif filter == 'Archived':
            projects = Project.objects.all().filter(archived=True)
            msg = 'Archived projects are fetched successfully!'
        else:
            msg = 'Closed projects are fetched successfully!'
            projects = Project.objects.all().filter(end_date < date.today())

        messages.success(request,msg)
        return render(request, "dashboard.html",{'projects':projects,'site':current_site,'domain':domain})


def projectAction(request,project_id,type):
    if type not in ['activate','deactivate','archive','unarchive']:
        messages.danger(request,'Unsupported action.')

    else:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            messages.danger(request,'Project id does not exists.')
            project=None
        if project is not None:
            if type == 'activate':
                project.project_status = True
            elif type == 'deactivate':
                project.project_status = False
            elif type == 'archive':
                project.archived = True
            else:
                project.archived = False
            project.save()
            msg = 'Project '+project.project_name+' has been ' +type+'d successfully!'
            messages.success(request,msg)

    return redirect('project_home')

def surveyForm(request,link):
    if request.method == "POST":
        q1 = int(request.POST['q1'])
        q2 = int(request.POST['q2'])
        q3 = int(request.POST['q3'])
        q4 = int(request.POST['q4'])
        q5 = int(request.POST['q5'])
        q6 = int(request.POST['q6'])
        q7 = int(request.POST['q7'])
        q8 = int(request.POST['q8'])
        q9 = int(request.POST['q9'])
        q10 = int(request.POST['q10'])
        q11 = int(request.POST['q7'])
        q12 = int(request.POST['q8'])
        q13 = int(request.POST['q9'])
        q14 = int(request.POST['q10'])

        link_obj = Link.objects.get(url=link)
        submission = Submission.objects.create(link=link_obj,q1=q1,q2=q2,q3=q3,q4=q4,q5=q5,q6=q6,q7=q7,q8=q8,q9=q9,q10=q10,q11=q11,q12=q12,q13=q13,q14=q14)

        return getAnonyForm(request)
    else:
        return render(request,"survey_form.html",{'product':'Smartphone','title':'Measure the Trust'})

def generateSurvey(request,link):
    if not is_valid_uuid(link):
        return render(request, "survey_msg.html",{'msg_title':'Invalid Link','msg_body':'The survey link is invalid.'})

    survey_url = Link.objects.all().filter(url=link)

    if survey_url.count() == 0:
        return render(request, "survey_msg.html",{'msg_title':'Invalid Link','msg_body':'The survey link is invalid.'})
    else:
        survey_url = Link.objects.get(url=link)

        if survey_url.survey.project.project_status:
            variables = {
                "PROJECT_NAME":survey_url.survey.project.project_name,
                "PRODUCT_NAME":survey_url.survey.product_name,
                "PRODUCT_INDUSTRY":survey_url.survey.product_industry,
                "TODAY":date.today(),
                "SURVEY_NAME":survey_url.survey.survey_name,
            }
            print(variables)
            title = survey_url.survey.title
            subtitle = survey_url.survey.subtitle
            paragraph = survey_url.survey.paragraph

            title = title.format(**variables)
            subtitle = subtitle.format(**variables)
            paragraph = paragraph.format(**variables)


            return render(request,"survey_front.html",{'project_title':title,'subtitle':subtitle,'paragraph':paragraph,'link':survey_url.url})
        else:
            return render(request, "survey_msg.html",{'msg_title':'Not active','msg_body':'The survey is not active.'})










# Create your views here.
def overview(request):
    sessions = Session.objects.all().filter(owner=request.user)
    print(sessions.count())
    return render(request, "dashboard.html",{'sessions':sessions})

def enterForm(request):
    if request.method == "POST":
        request.session.flush()


        s_pin = request.POST['pin']

        session = SessionPin.objects.all().filter(pin=s_pin)
        if session.count() == 0:
            messages.error(request,'Entered pin is invalid.')

            return render(request,"session_student_entry.html",{})
        else:
            session_obj = SessionPin.objects.get(pin=s_pin)
            print('Session Key:',request.session.session_key)
            if not request.session or not request.session.session_key:
                request.session.save()
                request.session['session_id'] = session_obj.id

            print('Session Key:',request.session.session_key)

            groups = range(session_obj.session.groups)
            return render(request,'student_session_home.html',{'session':session_obj.session,'groups':groups})
    else:
        if 'session_id' in request.session.keys():
            session_obj = SessionPin.objects.get(id=request.session['session_id'])
            groups = range(session_obj.session.groups)
            return render(request,'student_session_home.html',{'session':session_obj.session,'groups':groups})
        else:

            return render(request,"session_student_entry.html",{})

def uploadAudio(request):
    if request.method == 'POST':
        form = AudioflForm(request.POST,request.FILES)
        print(form)
        if form.is_valid():
            print('Form is valid')
            newform = form.save(commit=False)
            djfile = File(request.FILES['data_blob'])
            newform.fl.save(request.FILES['data_blob'].name,djfile)
            newform.save()
            return HttpResponse('Done')
        else:
            print('Form not valid')
            return HttpResponse('Form not valid')
    else:

        return HttpResponse('Not done')
def LeaveSession(request):
    request.session.flush()
    return redirect('home')

def getPad(request,group_id):
    if 'session_id' in request.session.keys():
        session_obj = SessionPin.objects.get(id=request.session['session_id'])

        if int(group_id) > session_obj.session.groups or int(group_id) < 1:
            messages.error(request,'Invalid group id')
            return redirect('student_entry')


        form = AudioflForm()

        return render(request,'pad.html',{'group':group_id,'session_obj':session_obj.session,'session':request.session['session_id'],'form':form})
    else:
        messages.error(request,'Session is not authenticated. Enter the access pin.')
        return redirect('student_entry')

def activateSession(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        session.status = True
        session.save()
        messages.success(request,'Session is started.')
        return render(request,'session_main.html',{'session':session})

def deactivateSession(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        session.status = False
        session.save()
        messages.success(request,'Session is stopped.')
        return render(request,'session_main.html',{'session':session})



def getSession(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        return render(request,'session_main.html',{'session':session})


class CompleteForm(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super(CompleteForm, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'overview':
            context.update({'all_data': self.get_all_cleaned_data()})
        return context


    @transaction.atomic
    def done(self, form_list, **kwargs):
        print('done called')
        all_data = self.get_all_cleaned_data()
        print(all_data)
        current_user = self.request.user
        project = Project.objects.create(user=current_user,questionnaire_type=all_data['type_questionnaire'],project_name=all_data['project_name'],project_type=all_data['project_type'],test_project=all_data['test_project'],project_status=all_data['project_status'])
        survey = Survey.objects.create(project=project,start_date = all_data['start_date'],end_date=all_data['end_date'],survey_name = all_data['name_of_survey'],product_name=all_data['product_name'],product_type=all_data['project_type'],product_industry=all_data['product_industry'], title=all_data['title'],subtitle=all_data['subtitle'],paragraph=all_data['paragraph'])

        for i in range(int(all_data['project_type'])):
            survey_url = Link.objects.create(survey=survey,sequence=(i+1))


        messages.success(self.request, 'Project created successfully !')
        return redirect('project_home')
