
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q

from .models import Student
from .forms import StudentForm


# MODULE 08: STAFF AUTHENTICATION

def staff_check(user):
    return user.is_authenticated and user.is_staff


# ORIGINAL MODULE 06 VIEWS

def student_registration(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        contact_no = request.POST.get('contact_no')

        Student.objects.create(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            contact_no=contact_no
        )
        return redirect('registration_success')

    return render(request, 'registration/registration.html')


def registration_success(request):
    return render(request, 'registration/success.html')


# MODULE 07: STUDENT DIRECTORY AND SEARCH

@user_passes_test(staff_check, login_url='login')
def student_list(request):
    query = request.GET.get('q', '').strip()

    students = Student.objects.all().order_by(
        'last_name', 'first_name'
    )

    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    context = {
        'students': students,
        'query': query,
    }

    return render(
        request,
        'registration/student_list.html',
        context
    )


# MODULE 07: STUDENT DETAILS

@user_passes_test(staff_check, login_url='login')
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    return render(
        request,
        'registration/student_detail.html',
        {'student': student}
    )


# MODULE 07: CREATE STUDENT

@user_passes_test(staff_check, login_url='login')
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Student record created successfully.'
            )

            return redirect('student_list')
    else:
        form = StudentForm()

    return render(
        request,
        'registration/student_form.html',
        {
            'form': form,
            'page_title': 'Register Student'
        }
    )


# MODULE 07: UPDATE STUDENT

@user_passes_test(staff_check, login_url='login')
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Student record updated successfully.'
            )

            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        'registration/student_form.html',
        {
            'form': form,
            'page_title': 'Update Student',
            'student': student,
        }
    )


# MODULE 07: DELETE STUDENT

@user_passes_test(staff_check, login_url='login')
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == 'POST':
        student.delete()

        messages.success(
            request,
            'Student record deleted successfully.'
        )

        return redirect('student_list')

    return render(
        request,
        'registration/student_confirm_delete.html',
        {'student': student}
    )


# MODULE 08: STAFF DASHBOARD

@user_passes_test(staff_check, login_url='login')
def staff_dashboard(request):
    # 1. Count all Student records
    total_students = Student.objects.count()

    # 2. Count Student records by gender
    male_students = Student.objects.filter(
        gender='Male'
    ).count()
    female_students = Student.objects.filter(
        gender='Female'
    ).count()

    # 3. Calculate percentages safely
    male_percent = (
        male_students / total_students * 100
        if total_students > 0 else 0
    )
    female_percent = (
        female_students / total_students * 100
        if total_students > 0 else 0
    )

    # 4. Read the search term from the URL
    query = request.GET.get('q', '').strip()

    # 5. Prepare the student report
    students = Student.objects.all().order_by(
        'last_name',
        'first_name'
    )

    # 6. Filter the report when a search term is supplied
    if query:
        students = students.filter(
            Q(student_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    # 7. Send all required values to the template
    context = {
        'total_students': total_students,
        'male_students': male_students,
        'female_students': female_students,
        'male_percent': male_percent,
        'female_percent': female_percent,
        'students': students,
        'query': query,
    }

    return render(
        request,
        'registration/dashboard.html',
        context
    )
