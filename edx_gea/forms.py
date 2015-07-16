import csv
import os

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy, ugettext as _

from student.models import CourseEnrollment

def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1]
    valid_extensions = ['.csv']
    if not ext in valid_extensions:
        raise ValidationError(_('Unsupported file extension.'))

class UploadAssessmentFileForm(forms.Form):
    assessment_file = forms.FileField(label=ugettext_lazy("Assessment file"), validators=[validate_file_extension])

    def __init__(self, *args, **kwargs):
        self.gea_xblock = kwargs.pop('gea_xblock', None)
        super(UploadAssessmentFileForm, self).__init__(*args, **kwargs)

    def clean_assessment_file(self):
        assessment_file = csv.DictReader(self.cleaned_data['assessment_file'],
                                         ['username', 'score', 'comment'])
        for line, row in enumerate(assessment_file):
            if line > self.gea_xblock.max_assessment_file_lines:
                self.add_form_error(line, _(u"The csv file has more than %s lines.") % self.gea_xblock.max_assessment_file_lines)
                return
            if self.is_user(line, row['username']):
                self.check_user_enrollment(line, row['username'])
            self.check_score(line, row['score'])


    def is_user(self, line, username):
        try:
            self.gea_xblock.usernames[username] = User.objects.get(username=username)
        except User.DoesNotExist:
            self.add_form_error(line, _(u"User %s does not exist.") % username)
        else:
            return True

    def check_user_enrollment(self, line, username):
        if not CourseEnrollment.is_enrolled(self.gea_xblock.usernames[username],
                                            self.gea_xblock.course_id):
            self.add_form_error(line, _(u"User %s is not enrolled to this course.") % username)

    def check_score(self, line, score):
        try:
            score = float(score)
        except (ValueError, TypeError):
            self.add_form_error(line, _(u"Score %s is not a valid number.") % score)
        else:
            if not 0 <= score <= self.gea_xblock.max_score():
                self.add_form_error(line, _(u"Score %s is outside score limits.") % score)

    def add_form_error(self, line, error_description):
        if not self._errors.get('assessment_file'):
            self._errors['assessment_file'] = ErrorList()
        error_msg = _(u"Line %(line)s: %(error_description)s") % {'line' : line, 'error_description' : error_description}
        self._errors['assessment_file'].append(error_msg)
