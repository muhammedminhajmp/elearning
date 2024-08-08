from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
# Create your models here.



class User(AbstractUser):
    usertype=models.CharField(max_length=20)
    Status=models.IntegerField(verbose_name="Status", default='0')

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,default=False)
    Name=models.CharField(max_length=100,verbose_name="Name")
    Place=models.CharField(max_length=100,verbose_name="Place")
    Phoneno=models.IntegerField(verbose_name="Phone",null=False)
    Age=models.IntegerField(verbose_name="age",null=False)

    class Meta:  
        db_table = "Student"

class Teacher(models.Model):
    Name=models.CharField(max_length=100,verbose_name="Name")
    Place=models.CharField(max_length=100,verbose_name="Place")
    Phoneno=models.IntegerField(verbose_name="Phone",null=False)
    Age=models.IntegerField(verbose_name="age",null=False)
    Qualification=models.CharField(max_length=100,verbose_name="Qualification")
    Djoin=models.DateField(verbose_name="Joining Date")

    class Meta:  
        db_table = "Teacher"


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    price = models.DecimalField(max_digits=10, decimal_places=2,default=False)

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

class LessonResource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    pdf = models.FileField(upload_to='lesson_pdfs/')

    def __str__(self):
        return self.title

from django.db import models
import uuid
import random

class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True

class Question(BaseModel):
    module = models.ForeignKey(Module, related_name='questions', on_delete=models.CASCADE)
    question = models.CharField(max_length=100)
    marks = models.IntegerField(default=5)

    def __str__(self):
        return self.question

    def get_answers(self):
        answer_objs = list(Answer.objects.filter(question=self))
        data = []
        random.shuffle(answer_objs)
        
        for answer_obj in answer_objs:
            data.append({
                'answer': answer_obj.answer,
                'is_correct': answer_obj.is_correct
            })
        return data

class Answer(BaseModel):
    question = models.ForeignKey(Question, related_name='question_answers', on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer







# class Quiz(models.Model):
#     module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes')
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True, null=True)
#     question_count = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return self.title

# class Question(models.Model):
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
#     text = models.CharField(max_length=500)
#     answer_count = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return self.text

# class Answer(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
#     text = models.CharField(max_length=500)
#     is_correct = models.BooleanField(default=False)

#     def __str__(self):
#         return self.text

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"{self.user}'s Cart"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.course.title}"