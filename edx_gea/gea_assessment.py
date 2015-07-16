from collections import namedtuple

from student.models import anonymous_id_for_user
from submissions import api as submissions_api

Score = namedtuple('Score', ['points_earned', 'points_possible'])
"""A Score contains the student grade (points_earned) and the max score (points_possible)."""

class GeaAssessment(object):
    """Handle communication with the submissions_api."""

    def __init__(self, user, gea_xblock):
        self.submission_id = {"item_id": gea_xblock.location,
                              "item_type": 'gea',
                              "course_id": gea_xblock.course_id,
                              "student_id": anonymous_id_for_user(user,
                                                                  gea_xblock.course_id)}
        """dict: Used to determine which course, student, and location a submission belongs to."""

    @property
    def score(self):
        """Score: The student score."""
        api_score = submissions_api.get_score(self.submission_id)
        if api_score:
            return Score(api_score['points_earned'], api_score['points_possible'])

    @score.setter
    def score(self, score):
        submissions_api.set_score(self.submission['uuid'], score.points_earned, score.points_possible)

    @property
    def comment(self):
        """str: The staff comment."""
        submissions = submissions_api.get_submissions(self.submission_id)
        if submissions:
            return submissions[0]['answer']['comment']

    @comment.setter
    def comment(self, comment):
        self.submission = submissions_api.create_submission(self.submission_id,
                                                            {'comment' : comment})
