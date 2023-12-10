function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

document.getElementById("run-btn").addEventListener("click", function () {
  var script = document.getElementById("script").value;
  var language = document.getElementById("language").value;
  var versionIndex = "0"; // Adjust if needed

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/job/run-code/", true);
  xhr.setRequestHeader("Content-Type", "application/json");

  var csrftoken = getCookie("csrftoken");
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        document.getElementById("output").value = response.output;
        document.getElementById("output-container").style.display = "block";
      } else {
        console.error("Error occurred:", xhr.statusText);
      }
    }
  };

  var data = {
    script: script,
    language: language,
    version_index: versionIndex,
  };

  xhr.send(JSON.stringify(data));
});
