"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

from django.utils.translation import ugettext as _

class GradeExternalActivityXBlock(XBlock):
    """
    """

    display_name = String(
        default=_('External Activity'), scope=Scope.settings,
        help="This name appears in the horizontal navigation at the top of "
             "the page."
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""

        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the GeaXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/gea.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/gea.css"))
        frag.add_javascript(self.resource_string("static/js/src/gea.js"))
        frag.initialize_js('GeaXBlock')
        return frag

    def is_course_staff(self):
        return getattr(self.xmodule_runtime, 'user_is_staff', False)
