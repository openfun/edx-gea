import csv
import os

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.utils.translation import get_language, ugettext_lazy, ugettext as _

from student.models import CourseEnrollment

def validate_file_extension(file):
    ext = os.path.splitext(file.name)[1]
    valid_extensions = ['.csv']
    if not ext in valid_extensions:
        raise ValidationError(_('Unsupported file extension.'))

def get_default_delimiter():
    """Get the default csv delimiter according to the user's language."""
    return ';' if get_language() == 'fr' else ','

class UploadAssessmentFileForm(forms.Form):
    assessment_file = forms.FileField(label=ugettext_lazy("Assessment file"), validators=[validate_file_extension])
    csv_delimiter = forms.ChoiceField(label=ugettext_lazy("CSV delimiter"),
                                      choices=((';', ugettext_lazy("Semicolon")),
                                               (',', ugettext_lazy("Comma"))))
    def __init__(self, *args, **kwargs):
        self.gea_xblock = kwargs.pop('gea_xblock', None)
        super(UploadAssessmentFileForm, self).__init__(*args, **kwargs)
        #http://stackoverflow.com/questions/657607/setting-the-selected-value-on-a-django-forms-choicefield
        if 'csv_delimiter' in self.initial:
            self.fields['csv_delimiter'].inital = self.initial['csv_delimiter']

    def clean_assessment_file(self):
        assessment_file = csv.DictReader(self.cleaned_data['assessment_file'],
                                         ['username', 'score', 'comment'],
                                         delimiter=str(self.gea_xblock.csv_delimiter))
        for line, row in enumerate(assessment_file):
            if line > self.gea_xblock.max_assessment_file_lines:
                self.add_form_error(line, _(u"The csv file has more than %s lines.") % self.gea_xblock.max_assessment_file_lines)
                return
            if self.is_user(line, row['username']):
                self.check_user_enrollment(line, row['username'])
            if row['score']:
                self.check_score(line, row['score'])
            else:
                self.add_form_error(line, _(u"Student needs a score to be graded."))

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
            score = int(score)
        except ValueError:
            self.add_form_error(line, _(u"Score %s is not an integer.") % score)
        else:
            if not 0 <= score <= self.gea_xblock.max_score():
                self.add_form_error(line, _(u"Score %s is outside score limits.") % score)

    def add_form_error(self, line, error_description):
        if not self._errors.get('assessment_file'):
            self._errors['assessment_file'] = ErrorList()
        error_msg = _(u"Line %(line)s: %(error_description)s") % {'line' : line, 'error_description' : error_description}
        self._errors['assessment_file'].append(error_msg)
    
