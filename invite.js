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
        document.getElementById("placeId").textContent = "Place ID: Invalid";
        document.getElementById("gameInstanceId").textContent = "Game Instance ID: Place ID must be valid";
    } else {
        document.getElementById("placeId").textContent = "Place ID: " + placeId;
        if (gameInstanceId.trim() === "") {
            document.getElementById("gameInstanceId").textContent = "Game Instance ID: Not Provided";
        } else if (!hasNoSpaces(gameInstanceId)) {
            document.getElementById("gameInstanceId").textContent = "Game Instance ID: Invalid";
        } else {
            document.getElementById("gameInstanceId").textContent = "Game Instance ID: " + gameInstanceId;
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