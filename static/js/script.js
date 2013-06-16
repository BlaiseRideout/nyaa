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
      $(".description").remove();
    }
    else {
      $this.text("▲");


      var nyaaLink = $this.parent().find("a");
      var nyaaURL = nyaaLink.attr("href").replace('download','view');
      var title = nyaaLink.text();

      $this.parent().append("<div class='description center'><a target='_blank' href='" + nyaaURL + "'>" + title + "</a></div>");

      $.ajax({
        url: nyaaURL,
        success: function (data) {
          console.log(data);
          var description = $(data).filter("div.viewdescription").text();
          alert(description);
          $this.parent().append("<div class='description center'>" + description + "</div>");
        }
      });
    }
  });
});
