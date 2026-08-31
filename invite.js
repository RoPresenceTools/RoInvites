let params = new URLSearchParams(document.location.search);
let placeId = params.get("placeId");
let gameInstanceId = params.get("gameInstanceId");

function hasNoSpaces(str) {
    if (str.trim() === "") return false;
    return str.replace(/\s/g, "") === str; 
}

function isPosNumber(str) {
    if (!hasNoSpaces(str)) return false;
    return (!isNaN(Number(str)) && Number(str) > 0);
}

function setParagraphElementValues() {
    if (!hasNoSpaces(placeId) || !isPosNumber(placeId)) {
        document.getElementById("placeId").textContent = "Invalid";
        document.getElementById("gameInstanceId").textContent = "Place ID must be valid";
    } else {
        document.getElementById("placeId").textContent = placeId;
        if (gameInstanceId.trim() === "") {
            document.getElementById("gameInstanceId").textContent = "Not Provided";
        } else if (!hasNoSpaces(gameInstanceId)) {
            document.getElementById("gameInstanceId").textContent = "Invalid";
        } else {
            document.getElementById("gameInstanceId").textContent = gameInstanceId;
        }
    }
}

function join() {
    if ((placeId == undefined && gameInstanceId == undefined) || !hasNoSpaces(placeId)) {
        return;
    } else if (gameInstanceId == undefined && isPosNumber(placeId)) {
        location.href = "roblox://experiences/start?placeId=" + placeId;
    } else if (hasNoSpaces(gameInstanceId)) {
        location.href = "roblox://experiences/start?placeId=" + placeId + "&gameInstanceId=" + gameInstanceId;
    }
}

window.onload = function(){
    setParagraphElementValues();
    requestAnimationFrame(() => {
        setTimeout(function(){join()}, 0);
    });
}