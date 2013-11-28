// $("button.btn btn-success").click(function(){
//     $.post("{% url blogpost_detail draft.id %}",
//         {{ draft }},
//         function(){
//             alert("Draft published!");
//         }
//     );
// });
function goBack(){
    window.history.back()
}

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
    $("#publish").click(function(){
        var title = $("h1").text(),
            body = $("p").text(),
            tags = $('a.post-tag').map(function(){
                return this.text;
            }).get();
            url = $("#publish").attr('action');
        $.post(url,{'title': title,
                    'body': body,
                    'tags': tags,
                    'csrfmiddlewaretoken': csrftoken
                    },
                    function(){
                        window.location.assign(url)
                    });
    });    
});