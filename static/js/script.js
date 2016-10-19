$(function() {
	$("#searchf").submit(function (event) {
		event.preventDefault();

		window.location.href = "/search/" + $("#filter").val() + "/" + $("#category").val() + "/" + $("#search").val();

		return false;
	});

  $(".expand").click(function (event) {
    $this = $(this);
    if($this.text() == "▲") {
      $this.text("▼");
      $this.parent().find(".description").slideUp(500, function () {
        $(this).remove();
      });
    }
    else {
      $this.text("▲");

      var nyaaLink = $this.parent().find("a");
			var nyaaURL = "/description/" + getParameterByName("tid", nyaaLink.attr("href"));
      var title = nyaaLink.text();

      $this.parent().append("<div style='display: none;' class='description center'></div>").slideDown();
      $this.parent().find(".description").load(nyaaURL +  " .viewdescription", function(response, status, xhr) {
        if (status == "error") {
          $this.parent().find(".description").text(xhr.status + " " + xhr.statusText);
        }
        $this.parent().find(".description").slideDown(500);
      });
    }
  });
	function getParameterByName(name, url) {
			if (!url) url = window.location.href;
			name = name.replace(/[\[\]]/g, "\\$&");
			var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
					results = regex.exec(url);
			if (!results) return null;
			if (!results[2]) return '';
			return decodeURIComponent(results[2].replace(/\+/g, " "));
	}
});
