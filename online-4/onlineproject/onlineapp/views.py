from django.shortcuts import render


# Create your views here.
import re
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
# from .models import Course,User,Module,Lesson,Quiz,Question,Answer,LessonResource,Student
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
from django.db import transaction
from django.core.files.storage import FileSystemStorage

    
def regstudent(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        age = request.POST['age']
        place = request.POST['place']
        phoneno = request.POST['phone']
        uname = request.POST['uname']
        pas = request.POST['pass']

        # Validate phone number using regular expression
        phone_regex = re.compile(r'^\d{10}$')
        if not phone_regex.match(phoneno):
            return HttpResponse("<script>window.alert('Phone number must be exactly 10 digits.');window.history.back();</script>")

        # Validate email using regular expression
        email_regex = re.compile(r'^[\w\.-]+@gmail\.com$')
        if not email_regex.match(email):
            return HttpResponse("<script>window.alert('Email must be a valid Gmail address.');window.history.back();</script>")

        # Validate password using regular expression
        password_regex = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$')
        if not password_regex.match(pas):
            return HttpResponse("<script>window.alert('Password must be at least 8 characters long, include at least one uppercase letter, one number, and one special character.');window.history.back();</script>")

        # Create a new user
        user = User.objects.create_user(username=uname, email=email, password=pas, usertype="student", Status=0)

        # Create a new student associated with the user
        Student.objects.create(user=user, Name=name, Place=place, Phoneno=phoneno, Age=age)

        return HttpResponse("<script>window.alert('Saved');window.location.href='/login/'</script>")

    return render(request, 'register.html')

def log(request):
    if request.method=="POST":
        u=request.POST['uname']
        p=request.POST['psw']
        
        user=authenticate(request,username=u,password=p)
        print(user)
        if user is not None and user.is_superuser==1:
        # if u=='admin' and p=='1234':
            login(request,user)
            # return redirect (course_form)
            return redirect (admin_dashboard)
        elif user is not None and user.usertype=="student" and user.Status==1:
            login(request,user)
            request.session['studid']=user.id
            # return redirect (studenthome)
            return redirect(coursedisplay)
            
        
        return HttpResponse("not approved")
    else:
        return render(request,'login.html')    

def studlist(request):
    x=User.objects.filter(Status="0",usertype='student')
    # y=Student.objects.all()
    
    return render(request,'studlist.html',{'data':x})



def studapprove(request,id):
    user=User.objects.filter(id=id).update(Status=1)
    return redirect('studlist')

def studreject(request,id):
    user=User.objects.get(id=id)
    user.delete()
    return redirect("studlist")


def studenthome(request):
    return render(request,"studentpage.html")





@login_required
def course_form(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        price = request.POST.get('price')
        course = Course(title=title, description=description,image=image,price=price ,created_by=request.user)
        course.save()
        return redirect('course_list')
    return render(request, 'courses/course_form.html')

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    
    if request.method == "POST":
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('course_list')

    return render(request, 'courses/course_delete.html', {'course': course})

@login_required
def update_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        price = request.POST.get('price')

        course.title = title
        course.description = description
        if image:
            course.image = image
        course.price = price    
        course.save()
        
        messages.success(request, 'Course updated successfully.')
        return redirect('course_list')

    return render(request, 'courses/update_course.html', {'course': course})


def create_module(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        
        course = Course.objects.get(id=course_id)
        Module.objects.create(course=course, title=title, description=description, order=order)
        
        return redirect('module_list')  

    courses = Course.objects.all()
    return render(request, 'modules/module_form.html', {'courses': courses})

def module_list(request):
    modules = Module.objects.all()
    return render(request, 'modules/module_list.html', {'modules': modules})


def update_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        order = request.POST.get('order')
        module.title = title
        module.description = description
        module.order = order
        module.save()
        return redirect('module_list')

    return render(request, 'modules/update_module.html', {'module': module})

def delete_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    module.delete()
    return redirect('module_list')



def create_lesson(request):
    if request.method == 'POST':
        module_id = request.POST.get('module')
        title = request.POST.get('title')
        content = request.POST.get('content')
        order = request.POST.get('order')
        pdf = request.FILES.get('pdf')

        module = get_object_or_404(Module, id=module_id)
        lesson = Lesson.objects.create(module=module, title=title, content=content, order=order)

        if pdf:
            LessonResource.objects.create(lesson=lesson, title=pdf.name, pdf=pdf)

        return redirect('lesson_list') 

    modules = Module.objects.all()
    return render(request, 'lessons/lesson_form.html', {'modules': modules})

def lesson_list(request):
    lessons = Lesson.objects.all()
    return render(request, 'lessons/lesson_list.html', {'lessons': lessons})

def update_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        order = request.POST.get('order')
        lesson.title = title
        lesson.content = content
        lesson.order = order
        lesson.save()
        return redirect('lesson_list')

    return render(request, 'lessons/update_lesson.html', {'lesson': lesson})

def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    lesson.delete()
    return redirect('lesson_list')



def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def courses(request):
    return render(request,'courses.html')

def webdesign(request):
    return render(request,'webdesign.html')

def graphicdesign(request):
    return render(request,'graphicdesign.html')

def videoediting(request):
    return render(request,'videoediting.html')

def fullstack(request):
    return render(request,'fullstack.html')

@login_required
def coursedisplay(request):
    # course = get_object_or_404(Course, id=course_id, created_by=request.user)
    query = request.GET.get('q')
    if query:
        courses = Course.objects.filter(title__icontains=query)
    else:
        courses = Course.objects.all()
    return render(request, 'courses/course_display.html', {'courses': courses})




def moduledisplay(request, id):
    course = get_object_or_404(Course, id=id)
    query = request.GET.get('q')
    if query:
        modules = Module.objects.filter(course=course, title__icontains=query)
    else:
        modules = Module.objects.filter(course=course)
    return render(request, 'modules/module_display.html', {'course': course, 'modules': modules})


def lessondisplay(request, id):
    module = get_object_or_404(Module, id=id)
    query = request.GET.get('q')
    if query:
        lessons = Lesson.objects.filter(module=module, title__icontains=query)
    else:
        lessons = Lesson.objects.filter(module=module)
    return render(request, 'lessons/lesson_display.html', {'module': module, 'lessons': lessons})

def lessondetail(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    course = lesson.module.course
    resources = LessonResource.objects.filter(lesson=lesson)
    return render(request, 'lessons/lesson_detail.html', {'lesson': lesson, 'course': course,'resources': resources})

def coursedetail(request):
    return render(request,"courses/course_detail.html")

def moduledetail(request, id):
    module = get_object_or_404(Module, id=id)
    return render(request, 'courses/module_detail.html', {'module': module})



def indexhome(request):
    return redirect('index')

def home2(request):
    return render(request,"home.html")

@login_required
def admin_dashboard(request):
    return render(request, 'admin.html')



def quiz_view(request):
    if request.method == 'POST':
        return calculate_score(request)
    else:
        return render_quiz(request)
    
def quiz_view2(request):
    if request.method == 'POST':
        return calculate_score2(request)
    else:
        return render_quiz2(request)
    
def quiz_view3(request):
    if request.method == 'POST':
        return calculate_score3(request)
    else:
        return render_quiz3(request)
        

def render_quiz(request):
    return render(request, 'quiz.html')

def render_quiz3(request):
    return render(request, 'quiz3.html')

def render_quiz2(request):
    return render(request, 'quiz2.html')

def calculate_score(request):
    correct_answers = {
    'q1': '8',
    'q2': 'Java',
    'q3': 'Cascading Style Sheets',
    'q4': 'Bootstrap',
    'q5': 'Hypertext Markup Language',
    'q6': 'var x;',
    'q7': '# This is a comment',
    'q8': 'decimal',
    'q9': '52',
    'q10': 'myFunction: function() {}',
    'q11': 'for i in range(5):',
    'q12': 'Django is a server-side web framework written in Python.',
    'q13': 'MongoDB',
    'q14': 'UPDATE',
    'q15': 'Virtual DOM'
}

    score = 0
    for key, correct_answer in correct_answers.items():
        user_answer = request.POST.get(key)
        if user_answer == correct_answer:
            score += 1

    return JsonResponse({'score': score})

def calculate_score2(request):
    if request.method == 'POST':
        # Define the correct answers
        correct_answers = {
            'q1': 'Paris',
            'q2': 'Jupiter',
            'q3': 'Harper Lee',
            'q4': 'Vatican City',
            'q5': 'Oxygen',
            'q6': 'Leonardo da Vinci',
            'q7': 'Diamond',
            'q8': 'Yen',
            'q9': 'Avocado',
            'q10': 'Canberra',
            'q11': 'Alexander Fleming',
            'q12': 'Antarctic Desert',
            'q13': 'Rice',
            'q14': 'Albert Einstein',
            'q15': 'Au'
        }

        # Calculate the score
        score = 0
        for question, correct_answer in correct_answers.items():
            if request.POST.get(question) == correct_answer:
                score += 1

        # Return the score as JSON
        return JsonResponse({'score': score})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def calculate_score3(request):
    if request.method == 'POST':
        correct_answers = {
            'q1': 'H2O',
            'q2': 'Mars',
            'q3': 'Photosynthesis',
            'q4': 'Carbon Dioxide',
            'q5': 'Albert Einstein',
            'q6': '100°C',
            'q7': 'Mitochondria',
            'q8': 'Nitrogen',
            'q9': 'Gravity',
            'q10': '299,792 km/s',
            'q11': 'Na',
            'q12': 'Nitrogen',
            'q13': '6',
            'q14': 'NaCl',
            'q15': 'Diamond'
        }

        score = 0
        for key, correct_answer in correct_answers.items():
            if request.POST.get(key) == correct_answer:
                score += 1

        return JsonResponse({'score': score})
    return JsonResponse({'error': 'Invalid request method'}, status=400)



@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, course=course)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    total_price = sum(item.course.price * item.quantity for item in cart_items)
    for item in cart_items:
        item.individual_price = item.course.price * item.quantity
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        
    }
    return render(request, 'cart/cart_detail.html', context)


@login_required
def custom_logout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.items.all().delete() 
    logout(request)
    return redirect('login')


def quizmain(request):
    return render(request,"quizmain.html")
    
def readmore(request):
    return render(request,"readpage.html")    

def team(request):
    return render(request,"team.html")

def error404(request):
    return render(request,"404.html")




    
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Module, Question
import random

def home3(request):
    modules = Module.objects.all()
    return render(request, 'home3.html', {'modules': modules})

def quiz33(request):
    module_id = request.GET.get('module')
    if module_id:
        module = Module.objects.get(id=module_id)
        questions = Question.objects.filter(module=module)
        context = {'module': module, 'questions': questions}
        return render(request, 'quiz33.html', context)
    else:
        return redirect('home3')

def get_quiz(request):
    try:
        question_objs = Question.objects.all()
        
        if request.GET.get('module'):
            question_objs = question_objs.filter(module__id=request.GET.get('module'))
            
        question_objs = list(question_objs)
        data = []
        random.shuffle(question_objs)
        
        for question_obj in question_objs:
            answers = question_obj.get_answers()
            data.append({
                "uid": str(question_obj.uid),
                "module": question_obj.module.title,
                "question": question_obj.question,
                "marks": question_obj.marks,
                "answer": answers,
            })
            # print(f'Question: {question_obj.question}, Answers: {answers}')  # Debug print

        payload = {'status': True, 'data': data}
        return JsonResponse(payload)
        
    except Exception as e:
        print(e)
        return HttpResponse("Something went wrong")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, Answer
import json

@csrf_exempt
def submit_quiz(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', [])
            score = 0

            for answer in answers:
                question_uid = answer['question_uid']
                selected_answer = answer['selected_answer'].strip()

                # Fetch question and correct answer
                question = Question.objects.get(uid=question_uid)
                correct_answers = Answer.objects.filter(question=question, is_correct=True)

                # Debug statements
                print(f'Processing Question UID: {question_uid}')
                print(f'Selected Answer: "{selected_answer}"')

                # Check if selected answer is correct
                correct_answer_found = False
                for correct_answer in correct_answers:
                    correct_answer_text = correct_answer.answer.strip()
                    print(f'Correct Answer: "{correct_answer_text}"')

                    if correct_answer_text == selected_answer:
                        print('Match found!')
                        score += question.marks
                        correct_answer_found = True
                        break  # No need to check further if one correct answer is found

                if not correct_answer_found:
                    print('No match for this answer.')

            print(f'Total Score: {score}')
            return JsonResponse({'status': True, 'score': score})
        except Exception as e:
            print(f'Exception: {e}')
            return JsonResponse({'status': False, 'error': 'Something went wrong'}, status=400)
    return JsonResponse({'status': False, 'error': 'Invalid request method'}, status=400)





# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Question, Answer
# import json

# @csrf_exempt
# def submit_quiz(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             answers = data.get('answers', [])
#             score = 0

#             for answer in answers:
#                 question_uid = answer['question_uid']
#                 selected_answer = answer['selected_answer']

#                 question = Question.objects.get(uid=question_uid)
#                 correct_answer = Answer.objects.get(question=question, is_correct=True)

#                 # Debug statements
#                 print(f'Question UID: {question_uid}')
#                 print(f'Selected Answer: {selected_answer}')
#                 print(f'Correct Answer: {correct_answer.answer}')

#                 if correct_answer.answer == selected_answer:
#                     score += question.marks

#             print(f'Total Score: {score}')
#             return JsonResponse({'status': True, 'score': score})
#         except Exception as e:
#             print(e)
#             return JsonResponse({'status': False, 'error': 'Something went wrong'}, status=400)
#     return JsonResponse({'status': False, 'error': 'Invalid request method'}, status=400)




from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Question, Answer, Module

def create_quiz(request):
    if request.method == 'POST':
        module_id = request.POST.get('module')
        question_text = request.POST.get('question')
        marks = request.POST.get('marks')
        answers = request.POST.getlist('answer')
        is_corrects = request.POST.getlist('is_correct')
        
        module = Module.objects.get(id=module_id)
        question = Question.objects.create(module=module, question=question_text, marks=marks)
        
        for answer_text, is_correct in zip(answers, is_corrects):
            is_correct = True if is_correct == 'on' else False
            Answer.objects.create(question=question, answer=answer_text, is_correct=is_correct)
        
        return redirect('home3')  
    
    modules = Module.objects.all()
    return render(request, 'create_quiz.html', {'modules': modules})
