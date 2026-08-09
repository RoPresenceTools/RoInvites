let params = new URLSearchParams(document.location.search);
let placeId = params.get("placeId");
let gameInstanceId = params.get("gameInstanceId");

if (gameInstanceId == undefined) {
    gameInstanceId = "";
}

function join() {
    location.href = "roblox://experiences/start?placeId=" + placeId + "&gameInstanceId=" + gameInstanceId
}

join();