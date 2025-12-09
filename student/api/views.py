from rest_framework.viewsets import ModelViewSet
from ..models import (
    StudentProfile, GradeClass, AcademicYear, Term,
    StudentTermRecord, Subject, StudentSubjectRecord, 
)
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.decorators import action

from .ses import (
    StudentProfileSerializer, GradeClassSerializer, AcademicYearSerializer,
    TermSerializer, StudentTermRecordSerializer, SubjectSerializer,
    StudentSubjectRecordSerializer, StudentProfileCreateUserSerializer
)
from rest_framework.decorators import action

class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

    @action(detail=False, methods=['get'])
    def total(self, request):
        total_students = self.get_queryset().count()
        return Response({"total": total_students})


    @action(detail=False, methods=['get'])
    def per_class(self, request):
        data = (
            self.get_queryset()
            .values("current_class")
            .annotate(count=Count("id"))
            .order_by("current_class")
        )

        # Convert numeric code → class name text using choices
        results = [
            {
                "class": dict(StudentProfile.CURRENT_CLASS_CHOICES).get(item["current_class"]),
                "count": item["count"],
            }
            for item in data
        ]

        return Response(results)



class GradeClassViewSet(ModelViewSet):
    queryset = GradeClass.objects.all()
    serializer_class = GradeClassSerializer

    def create(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)
        return super().create(request, *args, **kwargs)



class AcademicYearViewSet(ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer


class TermViewSet(ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class StudentTermRecordViewSet(ModelViewSet):
    queryset = StudentTermRecord.objects.all()
    serializer_class = StudentTermRecordSerializer


class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class StudentSubjectRecordViewSet(ModelViewSet):
    queryset = StudentSubjectRecord.objects.all()
    serializer_class = StudentSubjectRecordSerializer



class StudentCreateProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileCreateUserSerializer

    #def dispatch(self, request, *args, **kwargs):
     #   print("\n[DISPATCH] HIT")
      #  print("[DISPATCH] method:", request.method)
       # print("[DISPATCH] path:", request.path)
        #print("[DISPATCH] content_type:", request.content_type)
        #print("[DISPATCH] raw body:", request.body.decode('utf-8') if request.body else "<empty>")
        #return super().dispatch(request, *args, **kwargs)
