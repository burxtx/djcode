function btnChange(){
	if ($("a").hasClass("follow")){
		// $(".follow").on("click", function(){
		// 	$(this).css("background-color", "red");
		// });
		// $(".btn.icon.follow").replaceWith($(".btn.icon.unfollow"))
		$(".follow").replaceWith('<a class="btn unfollow" href="javascript:void(0)">Unfollow</a>')
	}else{
		// $(".unfollow").on('click', function(){
		// 	$(this).css("background-color", "green");
		// });
		// $(".btn.icon.unfollow").replaceWith($(".btn.icon.follow"))
		$(".unfollow").replaceWith('<a class="btn btn-success follow" href="javascript:void(0)">Follow</a>')
	}
}

$(document).ready(function(){
	$(document).on("click", ".follow", function(){
		var url = "/friend/add/";
		var	username = $("body").data("username");
		var	data = {
				"username": username
			};
		$.get(url, data, btnChange());
	});
	$(document).on("click", ".unfollow", function(){
		var url = "/friend/remove/";
		var	username = $("body").data("username");
		var	data = {
				"username": username,
			};
		$.get(url, data, btnChange());
	});
});
// $(document).ready(function(){
// 	$(".btn.icon.follow").click(function(){
// 		var url = ".",
// 			href = $(".btn.icon.follow").attr("href"),
// 			data = href.match("^?username=[a-z,0-9,A-Z]/$");
// 		$.get(url, {'username':data});
// 	});
// }); 
