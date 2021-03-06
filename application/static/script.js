$(document).ready(function () {
  $("#new-application-form, #edit-stage-form, #new-stage-form").submit(function (event) {
    if (checkBothStatuses() === false || checkBothDateTime() === false || checkTimeFormat() === false) {
      event.preventDefault();
      return false;
    }
  });

  $("#default-status, #custom-status").on("change", function (event) {
    $("#default-status")[0].setCustomValidity("");
    $("#default-status")[0].reportValidity();
  });

  $(".stage-date").on("change", function (event) {
    this.setCustomValidity("");
    this.reportValidity();
  });

  $(".stage-time").on("change", function (event) {
    this.setCustomValidity("");
    this.reportValidity();
    checkTimeFormat();
  });

  $("#company-name").on("input", function (event) {
    if ($(this).val() != "") {
      checkIfCompanyExists();
    }
  });
});

function checkBothStatuses() {
  var defaultStatus = $("#default-status");
  var customStatus = $("#custom-status");
  if (defaultStatus.val() == null && customStatus.val() == "") {
    defaultStatus[0].setCustomValidity("Please choose a default status or write a custom one.");
    defaultStatus[0].reportValidity();
    return false;
  }
  return true;
}

function checkBothDateTime() {
  var date = $(".stage-date");
  var time = $(".stage-time");
  if ((date.val() != "" && time.val() == "") || (date.val() == "" && time.val() != "")) {
    time[0].setCustomValidity("Please input a time too");
    time[0].reportValidity();
    return false;
  }
  return true;
}

function checkTimeFormat() {
  var time = $(".stage-time");
  if (time.val() == "" || checkTimeRegex(time.val())) {
    time.removeClass("is-invalid");
    return true;
  }
  time.addClass("is-invalid");
  return false;
}

// https://adamprescott.net/2014/01/08/validate-time-entry-with-javascript/
function checkTimeRegex(time) {
  var regex = /^\s*([01]?\d|2[0-3]):[0-5]\d\s*$/i;
  return time.match(regex);
}

function checkIfCompanyExists() {
  var name = $("#company-name").val();
  var ajax = new XMLHttpRequest();
  ajax.onreadystatechange = function () {
    if (ajax.readyState === 4 && ajax.status === 200) {
      var response = JSON.parse(ajax.response);
      $("#company-suggestion").empty();
      if (response != null) {
        response.forEach(function (item) {
          $("#company-suggestion").append(new Option(item.company_name));
        });
      }
    }
  };
  ajax.open("POST", "/check_existing_" + name + "_for_" + project_id, true);
  ajax.send();
}