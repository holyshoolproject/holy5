from django.contrib import admin
from .models import StudentProfile, GradeClass, AcademicYear, Term, StudentTermRecord, Subject, StudentSubjectRecord
from .utils import import_students_from_excel
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages




# Form for uploading Excel
class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()



@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "contact_of_father",
        "contact_of_mother",
        "get_current_class_display_name",
        "name_of_father",
        "name_of_mother",
    )
    list_filter = (
        "current_class",
     

    )
    search_fields = (
        "user__full_name",   # assuming your User model has full_name

    )


    change_list_template = "admin/student_import_changelist.html"
    def get_current_class_display_name(self, obj):
        return obj.get_current_class_display_name()
    
    get_current_class_display_name.short_description = "Current Class"


    # Custom view to handle Excel import
    def import_excel(self, request):
        if request.method == "POST":
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES["excel_file"]

                # Save uploaded file temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                    for chunk in excel_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                # Call utility function to import students
                result = import_students_from_excel(tmp_path)
                messages.success(request, result)
                return redirect("..")
        else:
            form = ExcelUploadForm()

        return render(request, "admin/import_excel_form.html", {"form": form})

    # Add custom URL for Excel import
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel, name='import_students_excel'),
        ]
        return custom_urls + urls



@admin.register(GradeClass)
class GradeClassAdmin(admin.ModelAdmin):
    list_display = ("name", "staff")
    list_filter = ("name",)
    search_fields = ("name",)





@admin.register(StudentTermRecord)
class StudentTermRecordAdmin(admin.ModelAdmin):
    list_display = ("student", "get_class", "term", "attendance")
    list_filter = ("term", "grade_class")
    search_fields = ("student__user__full_name",)

    def get_class(self, obj):
        return obj.grade_class
    get_class.short_description = 'Class'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(StudentSubjectRecord)
class StudentSubjectRecordAdmin(admin.ModelAdmin):
    list_display = ("student_term_record", "subject", "total_score", "grade")
    list_filter = ("subject", "grade")
    search_fields = ("student_term_record__student__full_name", "subject__name")



