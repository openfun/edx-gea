function GeaXBlock(runtime, element) {
    var uploadUrl = runtime.handlerUrl(element, 'upload_assessments');
    var xblock_selector = 'div[data-usage-id="' + element.dataset.usageId +  '"] ';
    var assessmentFile;
    
    $(function ($) { // On load.
	assessmentFile = $(xblock_selector + '#assessment_file');
	assessmentFile.change(upload_file);
        var uploadUrl = runtime.handlerUrl(element, 'upload_assessments');
    });

    function upload_file() {
	var xhr = new XMLHttpRequest();
	var form = new FormData();
	
	$(xblock_selector + '.waiting').show();
	
	xhr.open('POST', uploadUrl);
	xhr.setRequestHeader("X-CSRFToken", csrftoken);
	form.append('file', assessmentFile.prop('files')[0]);
	
	xhr.send(form);
	xhr.onload = DisplayUploadAssessmentsResponse;
    }
    
    function DisplayUploadAssessmentsResponse() {
	$(xblock_selector + '.waiting').hide();
	$(xblock_selector + '.upload_assessments_response').html(this.response);
    }
    
    // Get the csrf token from the cookie (https://docs.djangoproject.com/en/1.4/ref/contrib/csrf/#ajax).
    function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
	    var cookies = document.cookie.split(';');
	    for (var i = 0; i < cookies.length; i++) {
		var cookie = jQuery.trim(cookies[i]);
		// Does this cookie string begin with the name we want?
		if (cookie.substring(0, name.length + 1) == (name + '=')) {
		    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		    break;
		}
	    }
	}
	return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
}
