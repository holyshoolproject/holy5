from rest_framework.viewsets import ModelViewSet
from ..models import (
    StudentProfile, GradeClass, AcademicYear, Term,
    StudentTermRecord, Subject, StudentSubjectRecord, 
)
from .ses import (
    StudentProfileSerializer, GradeClassSerializer, AcademicYearSerializer,
    TermSerializer, StudentTermRecordSerializer, SubjectSerializer,
    StudentSubjectRecordSerializer, StudentProfileCreateUserSerializer
)


class StudentProfileViewSet(ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


class GradeClassViewSet(ModelViewSet):
    queryset = GradeClass.objects.all()
    serializer_class = GradeClassSerializer


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

   # def dispatch(self, request, *args, **kwargs):
    #    print("\n[DISPATCH] HIT")
     #   print("[DISPATCH] method:", request.method)
      #  print("[DISPATCH] path:", request.path)
       # print("[DISPATCH] content_type:", request.content_type)
        #print("[DISPATCH] raw body:", request.body.decode('utf-8') if request.body else "<empty>")
        #return super().dispatch(request, *args, **kwargs)
