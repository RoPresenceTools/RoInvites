let params = new URLSearchParams(document.location.search);
let placeId = params.get("placeId");
let gameInstanceId = params.get("gameInstanceId");

function join() {
    if (placeId == undefined && gameInstanceId == undefined) {
        alert("A valid placeId and/or gameInstanceId must be given as URL parameters.");
    } else if (placeId == undefined) {
        alert("A valid placeId must be given as a URL parameter.");
    } else if (gameInstanceId == undefined) {
        location.href = "roblox://experiences/start?placeId=" + placeId;
    } else {
        location.href = "roblox://experiences/start?placeId=" + placeId + "&gameInstanceId=" + gameInstanceId;
    }
}

window.onload = function(){
    requestAnimationFrame(() => {
        setTimeout(function(){join()}, 0);
    });
}