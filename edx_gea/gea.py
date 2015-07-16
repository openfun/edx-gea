"""GEA (Grade External Activity). An XBlock used to grade external activities.

All kind of student activities can't be achieved inside edx-platform. Therefore a teacher
will only describe the activity in the lms and add a GEA XBlock to grade it.
"""

import csv

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy, ugettext as _

from webob.response import Response

from xblock.core import XBlock
from xblock.fields import Scope, String, Integer, Float
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin
from xblockutils.resources import ResourceLoader

from .forms import UploadAssessmentFileForm
from .gea_assessment import GeaAssessment, Score


loader = ResourceLoader(__name__)

class GradeExternalActivityXBlock(XBlock, StudioEditableXBlockMixin):
    """XBlock to grade external activities."""

    has_score = True #: This flags the XBlock as a problem.
    icon_class = 'problem'

    display_name = String(
        default=ugettext_lazy('External Activity Grader'), scope=Scope.settings,
        help="This name appears in the horizontal navigation at the top of "
             "the page."
    )

    points = Integer(
        display_name=ugettext_lazy("Maximum grade"),
        help=(ugettext_lazy("Maximum grade of the external activity.")),
        default=10,
        scope=Scope.settings
    )

    weight = Float(
        display_name="Problem Weight",
        help=("Defines the number of points each problem is worth. "
              "If the value is not set, the problem is worth the sum of the "
              "option point values."),
        values={"min": 0, "step": .1},
        scope=Scope.settings
    )

    editable_fields = ('points',)

    usernames = {} #: A dict used to avoid multiple calls to db {'username' : models.User , ...}.

    max_assessment_file_lines = 1000 #: The limit of csv lines in the uploded assessment file.

    def student_view(self, context=None):
        """Display the student assessment (score and comment).

        Note:
            The LMS Runtime only calls the XBlock.student_view. In order to get two different
            views, depending on the runtime user being a staff member or a student, we check inside the student_view
            if the user is a staff and call the staff_view accordingly.
        """
        if self.is_course_staff():
            return self.staff_view()
        gea_assessment = GeaAssessment(User.objects.get(id=self.xmodule_runtime.user_id), self)
        frag = Fragment(loader.render_template("templates/edx_gea/student.html",
                                               {'score' : gea_assessment.score,
                                                'comment' : gea_assessment.comment}))
        return frag

    def staff_view(self):
        """Display the form for uploading the assessement file."""
        spinner_url = self.runtime.local_resource_url(self, 'public/static/images/spinner.gif')
        frag = Fragment(loader.render_template("templates/edx_gea/staff.html",
                                               {'upload_assessment_file_form' : UploadAssessmentFileForm(auto_id=True),
                                                'spinner_url' : spinner_url,
                                                'max_assessment_file_lines' : self.max_assessment_file_lines}))
        frag.add_css(loader.load_unicode("static/css/gea.css"))
        frag.add_javascript(loader.load_unicode("static/js/src/gea.js"))
        frag.initialize_js('GeaXBlock')
        return frag

    @XBlock.handler
    def upload_assessments(self, request, context=None):
        """Called when a staff has submitted an assessment file.

        Perform the file validation. If the file is valid grade students, otherwise
        return the list of errors and offer the staff to upload a new file.
        """
        if not self.is_course_staff():
            raise PermissionDenied

        uploaded_file = request.POST['file'].file
        form = UploadAssessmentFileForm(request.POST, files={'assessment_file' : uploaded_file},
                                        auto_id=True, gea_xblock=self)

        if form.is_valid():
            self.handle_assessment_file(uploaded_file)
            return Response(u"<p class='gea_success'>{}</p>".format(_("Thank you, the students assessment has been done.")))
        else:
            return Response(loader.render_template("templates/edx_gea/form_errors.html",
                                                   {'upload_assessment_file_form' : form}))

    def handle_assessment_file(self, file):
        """Read the file and set score and comment through the GeaAssessment class.

        Note:
            We expect a csv file following this structure:
                +----------+----+------------+
                | student1 | 10 | Good work. |
                +----------+----+------------+
                | student2 | 20 | Bad work.  |
                +----------+----+------------+
        Args:
            file: The assessment file.
        """
        assessment_file = csv.DictReader(file, ['username', 'score', 'comment'])
        for row in assessment_file:
            gea_assessment = GeaAssessment(self.usernames[row['username']], self)
            gea_assessment.comment = row['comment']
            gea_assessment.score = Score(row['score'], self.max_score())

    def is_course_staff(self):
        return getattr(self.xmodule_runtime, 'user_is_staff', False)

    def max_score(self):
        return self.points

