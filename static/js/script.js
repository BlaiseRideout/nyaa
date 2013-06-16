var nyaaURL;
google.load("jquery", "1.6.4");
google.setOnLoadCallback(function() {
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
      var nyaaURL = nyaaLink.attr("href").replace('http://www.nyaa.eu/?page=download&tid=','/description/');
      var title = nyaaLink.text();

      //$this.parent().append("<div class='description center'><a target='_blank' href='" + nyaaURL + "'>" + title + "</a></div>");
      $this.parent().append("<div style='display: none;' class='description center'></div>").slideDown("slow");
      $this.parent().find(".description").load(nyaaURL +  " .viewdescription", function(response, status, xhr) {
        if (status == "error") {
          $this.parent().find(".description").text(xhr.status + " " + xhr.statusText);
        }
        $this.parent().find(".description").slideDown(500);
      });
    }
  });
});
