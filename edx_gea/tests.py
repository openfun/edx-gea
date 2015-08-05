import csv
import datetime
from mock import Mock
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import RequestFactory, RequestFactory

from courseware.grades import iterate_grades_for, _grade
from courseware.tests.factories import StudentModuleFactory
from student.tests.factories import UserFactory, CourseEnrollmentFactory

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory

from edx_gea.forms import UploadAssessmentFileForm

class GradeExternalActivityXBlockTests(ModuleStoreTestCase):
    def setUp(self):
        super(GradeExternalActivityXBlockTests, self).setUp(create_user=False)
        self.course = CourseFactory.create(grading_policy={"GRADER": [{"type": "Homework",
                                                                       "min_count": 1,
                                                                       "drop_count": 0,
                                                                       "short_label": "HW",
                                                                       "weight": 1.0}]},
                                           metadata={'start': datetime.datetime.now() - datetime.timedelta(days=1)}
        )

        self.gea_xblock = None
        self.generate_modules_tree(self.course, 'chapter', 'sequential',
                                   'vertical', 'edx_gea')
        self.gea_xblock.csv_delimiter = ','

    def test_staff_view_is_called(self):
        self.gea_xblock.xmodule_runtime = Mock()
        self.gea_xblock.xmodule_runtime.user_is_staff = True
        self.gea_xblock.staff_view = Mock()
        self.gea_xblock.student_view()
        self.gea_xblock.staff_view.assert_called()

    def create_csv(self, *args):
        input_file = tempfile.NamedTemporaryFile()
        writer = csv.writer(input_file)
        for arg in args:
            writer.writerow(arg)
        input_file.seek(0)
        return input_file

    def test_handle_assessment_file(self):
        users = UserFactory.create_batch(2)
        file = self.create_csv([users[0], '5', u"Well done."],
                               [users[1], '1', u"Very bad."])
        self.gea_xblock.usernames[users[0].username] = users[0]
        self.gea_xblock.usernames[users[1].username] = users[1]
        self.gea_xblock.handle_assessment_file(file)
        results = self.edx_grade_students(users)
        self.assertEqual(results.next()[1]['percent'], 0.5)
        self.assertEqual(results.next()[1]['percent'], 0.1)

    def edx_grade_students(self, users):
        return iterate_grades_for(self.course, users)

    def generate_modules_tree(self, module, *args):
        if not args:
            self.gea_xblock = module
            return
        category = args[0]
        is_graded = True if category == 'sequential' or category == 'edx_gea' else False
        self.generate_modules_tree(ItemFactory(parent=module,
                                               category=category,
                                               display_name=None,
                                               format='Homework' if is_graded else '',
                                               graded=is_graded),
                                   *args[1:])

    def get_form_errors(self, form):
        form.is_valid()
        return str(form._errors['assessment_file'])

    def generate_form(self, raw_text):
        return UploadAssessmentFileForm({'csv_delimiter' : ','},
                                        files={'assessment_file' : SimpleUploadedFile('lol.csv', raw_text)},
                                        auto_id=True,
                                        gea_xblock=self.gea_xblock)

    def test_user_does_not_exist(self):
        CourseEnrollmentFactory.create(course_id=self.course.id,
                                       user=UserFactory(username='Joe'))
        form = self.generate_form("UnknownUser, 50\nJoe, 20")
        errors = self.get_form_errors(form)
        self.assertIn("UnknownUser", errors)
        self.assertNotIn("Joe", errors)

    def test_user_is_not_enrolled(self):
        CourseEnrollmentFactory.create(course_id=self.course.id,
                                       user=UserFactory(username='Joe'))
        UserFactory(username='NotEnrolled')
        form = self.generate_form("Joe, 20\nNotEnrolled, 10")
        errors = self.get_form_errors(form)
        self.assertIn("NotEnrolled", errors)
        self.assertNotIn("Joe", errors)

    def test_invalid_score(self):
        CourseEnrollmentFactory.create(course_id=self.course.id,
                                       user=UserFactory(username='Joe'))
        self.gea_xblock.points = 10
        form = self.generate_form("Joe, SCORE")
        errors = self.get_form_errors(form)
        self.assertIn("SCORE", errors)
        form = self.generate_form("Joe, 100")
        errors = self.get_form_errors(form)
        self.assertIn("100", errors)

    def test_edx_grade_with_no_score_but_problem_loaded(self):
        """Test grading with an already loaded problem but without score.

        This can happen when the student calls the progress page from the courseware (djangoapps.courseware.views.progress).
        The progress view grades the activity only to get the current score but staff may have not given the problem a score yet.
        """
        request = RequestFactory().get('/')
        user = UserFactory(username='Joe')
        CourseEnrollmentFactory.create(course_id=self.course.id,
                                       user=user)
        StudentModuleFactory.create(student=user, course_id=self.course.id, module_state_key=str(self.gea_xblock.location))
        grade = _grade(user, request, self.course, None)
        self.assertEqual(grade['percent'], 0.0)
