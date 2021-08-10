var dragItem = document.querySelector("#item");
var container = document.querySelector("#container");

var active = false;
var currentX;
var currentY;
var initialX;
var initialY;
var xOffset = 0;
var yOffset = 0;

var initial = Date.now()
var current = 0;

var divArray = [];
var divNum = 0;

var spaceDown = false;

let rawPath = [];
let path = [];

var firstRun = true;

var yLimit = 0;
var xLimit = 0;

container.addEventListener("touchstart", dragStart, false);
container.addEventListener("touchend", dragEnd, false);
container.addEventListener("touchmove", drag, false);

container.addEventListener("mousedown", dragStart, false);
container.addEventListener("mouseup", dragEnd, false);
container.addEventListener("mousemove", drag, false);

document.addEventListener("keydown", event => {
        if(event.code === 'Space' && spaceDown == false){
            spaceDown = true;
            sendPosition('pen_down', 'pen_down');
        }
});

document.addEventListener("keyup", event => {
    if(event.code === 'Space' && spaceDown == true){
        spaceDown = false;
        sendPosition('pen_up', 'pen_up');
    }
});

function dragStart(e){
    if(e.type === "touchstart"){
        initialX = e.touches[0].clientX - xOffset;
        initialY = e.touches[0].clientY - yOffset;
    }else{
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
    }
    if(e.target === dragItem){
        active = true;
    }
}

function dragEnd(e){
    initialX = currentX;
    initialY = currentY;
    active = false;
}

function drag(e){
    if(active){
        current = Date.now();
        e.preventDefault();
        

        if(e.type === "touchmove"){
            currentX = e.touches[0].clientX - initialX;
            currentY = e.touches[0].clientY - initialY;
        }else{
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
        }

        xOffset = currentX;
        yOffset = currentY;

        var pos = convertPos(currentX, currentY);
        var x = pos[0];
        var y = pos[1];

        if((current - initial) > 5){
            if(spaceDown == true){
                path.push([0, 0]);
                sendPosition(x, y);
                createDiv(currentX, currentY);
                collectPos(currentX, currentY, x, y);
                storeData();
            }
            initial = Date.now();
        }

        document.getElementById("xpos").innerHTML = x; 
        document.getElementById("ypos").innerHTML = y; 
        document.getElementById("udrawing").innerHTML = spaceDown;
        setTranslate(currentX, currentY, dragItem);
    }
}

document.getElementById('dbtn').onclick = () => {
    sessionStorage.setItem('reloading', 'true')
        sessionStorage.setItem('regenDivs', 'true');
}
document.getElementById('rbtn').onclick = () => {
    sessionStorage.setItem('reloading', 'true');
    sessionStorage.setItem('resetPath', 'true');
}

document.getElementById('hbtn').onclick = () => {
    sessionStorage.setItem('reloading', 'true');
    sessionStorage.setItem('regenDivs', 'true');
}

$(document).ready(function() {
    console.log("page loaded");
    var reloading = sessionStorage.getItem("reloading");
    console.log(sessionStorage.getItem("regenDivs"), sessionStorage.getItem("resetPath"));

    if(reloading){
        sessionStorage.removeItem("reloading");

        if(sessionStorage.getItem("regenDivs") == 'true'){
            regenDivs();
            sessionStorage.removeItem("regenDivs");
        }
        if(sessionStorage.getItem("resetPath") == 'true'){
            resetPath();
            sessionStorage.removeItem("resetPath");
        }
    }

});

document.body.onload = createDiv;
let containerDiv = document.getElementById("item");
let parentDiv = containerDiv.parentNode;

function createDiv(cX, cY){
    divArray[divNum] = document.createElement("div" + divNum);
    divArray[divNum].className = 'paint';
    parentDiv.insertBefore(divArray[divNum], containerDiv);

    if(divNum == 0){
        removeBadDiv();
    }else{
        const d = document.getElementsByTagName("div" + divNum)[0];
        d.style.top = cY + 320 + "px";
        d.style.left = cX + 640 + "px";
    }
    divNum++;
}

function removeBadDiv(){
    var el = document.getElementsByTagName("div0")[0];
    el.remove();
}   

function regenDivs(){
    console.log("starting regen");
    var storedPath = JSON.parse(sessionStorage.getItem("path"));
    var storedRawPath = JSON.parse(sessionStorage.getItem("rawPath"));

    if(storedRawPath == null){
        console.log("path null");
        storedRawPath = [[0, 160]];
        return 0;
    }else{
        console.log(storedRawPath.toString());
    }

    for(let i = 0; i < storedRawPath.length; i++){
        createDiv(storedRawPath[i][0], storedRawPath[i][1]);
        console.log("Created div at: " + storedRawPath[i][0] + ", " + storedRawPath[i][1]);
    }

    path = storedPath;
    rawPath = storedRawPath;
}

function resetPath(){
    clearDivs();
    sessionStorage.removeItem("rawPath");
    sessionStorage.removeItem("path");
    sessionStorage.removeItem("numDivs");
    path = [];
    rawPath = [];
    divArray = [];
    numDivs = 0;
}

function clearDivs(){
    for(let i = 0; i < parseInt(sessionStorage.getItem("numDivs")); i++){
        try{
            var el = document.getElementsByTagName("div" + i)[0];
            el.remove();
            console.log("removed div" + i);
        }catch(err){
            console.log("error on div" + i + ", continuing");
        }
    }
} 

function penUpDown(state){
    if(state == 'down'){
        sendPosition('pen_down', 'pen_down');
    }else{
        sendPosition('pen_up', 'pen_up');
    }
}       

function storeData(){
    if(typeof(Storage) !== "undefined"){
        sessionStorage.setItem("path", JSON.stringify(path));
        sessionStorage.setItem("rawPath", JSON.stringify(rawPath));
        sessionStorage.setItem("numDivs", divNum);
    }else{
        console.log("error");
    }
}

function collectPos(rcX, rcY, cX, cY){
    rawPath.push([rcX, rcY]);
    path.push([cX, cY]);
}

function sendPosition(cX, cY){
    var position = {
        'x': cX,
        'y': cY            
    }
    $.ajax({
        url: Flask.url_for('getPosition'),
        type: 'POST',
        data: JSON.stringify(position),
        dataType: "json",
        contentType: "application/json",
        success: function(response){
        console.log(response);
        },
        error: function(err){
            console.log(err);
        }
    });
}

function convertPos(cX, cY){
    return [Math.round(cX / 2), Math.round((cY * -1 + 320) / 2)];
}

function setTranslate(xPos, yPos, el){
    el.style.transform = "translate3d(" + xPos + "px, " + yPos + "px, 0)";
}

