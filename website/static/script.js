function change(){
    element = document.getElementById("am_pm")
    if (element.innerHTML =="PM"){
        element.innerHTML = "AM"
        document.getElementById("per_of_day").value = "am"
    }else{
        element.innerHTML = "PM"
        document.getElementById("per_of_day").value = "pm"

    }
}
function deletesched(schedid){
    fetch("/delete-sched", {
        method: "POST",
        body: JSON.stringify({ schedId: schedid }),
      }).then((_res) => {
        window.location.href = "/schedules";
      });
    }

function runsched(){
  console.log("heyyy")
  fetch("/runsched", {
    method: "POST"}).then((_res) => {
      window.location.href = "/";
    });
    }
