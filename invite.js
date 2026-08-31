let params = new URLSearchParams(document.location.search);
let placeId = params.get("placeId");
let gameInstanceId = params.get("gameInstanceId");

function hasNoSpaces(str) {
    if (str.trim() === "") return false;
    return str.replace(/\s/g, "") === str; 
}

function isPosNumber(str) {
    if (str.trim() === "") return false;
    return (!isNaN(Number(str)) && Number(str) > 0);
}

function join() {
    if (placeId == undefined && gameInstanceId == undefined) {
        alert("A valid placeId and gameInstanceId must be given as URL parameters.");
    } else if (placeId == undefined || !isPosNumber(placeId)) {
        alert("A valid placeId must be given as a URL parameter.");
    } else if (gameInstanceId == undefined) {
        location.href = "roblox://experiences/start?placeId=" + placeId;
    } else if (!hasNoSpaces(gameInstanceId)) {
        alert("A valid gameInstanceId must optionally be given as a URL parameter.");
    } else {
        location.href = "roblox://experiences/start?placeId=" + placeId + "&gameInstanceId=" + gameInstanceId;
    }
}

window.onload = function(){
    requestAnimationFrame(() => {
        setTimeout(function(){join()}, 0);
    });
}