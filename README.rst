Grade External Activity XBlock
==============================

This XBlock provides a way to grade external activity in edx-platform.
The course staff will upload a simple csv containing usernames, grades and optional comments.
Then through the same XBlock students will see their evaluation.

Installation
~~~~~~~~~~~~

1. Install edx-gea
	
     .. code:: sh
   
          git clone https://github.com/openfun/edx-gea.git
	  cd edx-gea
	  pip install .
	  
2. Add edx\_gea to installed Django apps

   - In ``/edx/app/edxapp/edx-platform/cms/envs/common.py``, add ``'edx_gea'``
     to OPTIONAL_APPS

   - In ``/edx/app/edxapp/edx-platform/lms/envs/common.py``, add ``'edx_gea'``
     to OPTIONAL_APPS

3. Enable the GEA component in LMS and Studio (CMS).

   -  In ``/edx/app/edxapp/edx-platform/cms/envs/common.py``, add ``'edx_gea',`` to ``ADVANCED_COMPONENT_TYPES``

Create the GEA XBlock in edX Studio
-----------------------------------
#. Since the Grade External Activity doesn't support text within the problem, 
   it is recommended to precede the GEA XBlock with a Text or HTML XBlock with 
   instructions for the student describing the external activity.
   
   .. figure:: _static/images/gea-assessment-cms.png
	       :alt: Studio view of the Gea XBlock
   
#. Set the `Maximum Grade` setting.

   +----------------+-----------------------------------------------------------------+
   | Maximum Grade  | Maximum grade of the external activity.                         |
   +----------------+-----------------------------------------------------------------+

   .. figure:: _static/images/gea-assessment-cms_settings.png
	       :alt: Studio settings.


Staff Grading
-------------

#. Write your assessment file. The file has to be a **csv** file with the following structure:
   
   +----------+-------+----------+
   | username | grade | comment  |
   +----------+-------+----------+
   
   An example:
   
	.. figure:: _static/images/gea-assessment-file.png
	   :alt: Csv assessment file.

   .. note:: Comments are optionnal.

#. Navigate to the student view (LMS) of the course and find your Grade External Activity block. (If you are in Studio, click "View Live").
   
#. If you are Course Staff or an Instructor for the course, you will see the interface
   for submitting the assessment file.
   
   .. figure:: _static/images/gea-assessment-lms.png
      :alt: Staff view of LMS interface

#. Upload the file, and wait for a few seconds. In case of errors in the assessment file,
   a list of errors will be displayed. Correct the file and upload it again.
   
   .. figure:: _static/images/gea-assessment-lms-error.png
      :alt: Errors in assessment file.

#. You are done. All students have just been graded !
   
   .. figure:: _static/images/gea-assessment-lms-good.png
      :alt: Success assessment done.
	    
.. toctree::
   :maxdepth: 2

   references

Student LMS Interface
---------------------
Students will see their assessments in the same XBlock:

  .. figure:: _static/images/gea-assessment-lms_student.png
     :alt: Student view GEA XBlock.

.. note:: The grade is also displayed in the Progress page of the course.
