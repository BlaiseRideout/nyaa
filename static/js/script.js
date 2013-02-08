google.load("jquery", "1.6.4");
google.setOnLoadCallback(function() {
	$("#searchf").submit(function (event) {
		event.preventDefault();

		window.location.href = "/search/" + $("#filter").val() + "/" + $("#category").val() + "/" + $("#search").val();

		return false;
	});
});
