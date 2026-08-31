let params = new URLSearchParams(document.location.search);
let placeId = params.get("placeId");
let gameInstanceId = params.get("gameInstanceId");

function isNumber(str) {
    if (typeof str !== 'string' || str.trim() === '') return false;
    return !isNaN(Number(str));
}

function join() {
    if (placeId == undefined && gameInstanceId == undefined) {
        alert("A valid placeId and gameInstanceId must be given as URL parameters.");
    } else if (placeId == undefined || !isNumber(placeId)) {
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