// $(document).ready(function(){
// 	$(document).on("click", ".delete", function(){
// 		var id = $(this).attr("id");
// 		var item = $(this).parents(".post-item");
// 		// var url = '/blogpost/delete/';
// 		var url = '/blogpost/delete/'+encodeURIComponent(id)+'/';
// 		$.get(url, function(){
// 			item.remove();
// 		});
// 	});
// });

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

$(document).ready(function(){
	$(document).on("click", ".delete", function(){
		if (!confirm('Are you sure you want to delete?')) { return; }
		var id = $(this).attr("id");
		var item = $(this).parents(".post-item");
		// var url = $(this).attr("href");
		var url = '/blogpost/delete/'+id+'/';
		$.post(url, {
			'id': id,
			'csrfmiddlewaretoken': csrftoken
			},
			function(){
			item.fadeOut();
		});
	});
});