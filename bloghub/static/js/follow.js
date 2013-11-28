function btnChange(){
	$(".btn.icon.follow").css("background","green")
	$(".btn.icon.follow").attr("text","Unfollow")
}

$(document).ready(function(){
	$(".btn.icon.follow").click(function(){
		var url = "/friend/add/";
		var	username = $("div").data("username");
		var	data = {
				"username": username
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
