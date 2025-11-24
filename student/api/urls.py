from rest_framework.routers import DefaultRouter
from .views import (
    StudentProfileViewSet, GradeClassViewSet, AcademicYearViewSet,
    TermViewSet, StudentTermRecordViewSet, SubjectViewSet,
    StudentSubjectRecordViewSet, StudentCreateProfileViewSet
)

router = DefaultRouter()
router.register("students", StudentProfileViewSet)
router.register("classes", GradeClassViewSet)
router.register("academic-years", AcademicYearViewSet)
router.register("terms", TermViewSet)


router.register("create", StudentCreateProfileViewSet, basename="student-create")


router.register("student-term-records", StudentTermRecordViewSet)
router.register("subjects", SubjectViewSet)
router.register("subject-records", StudentSubjectRecordViewSet)

urlpatterns = router.urls
