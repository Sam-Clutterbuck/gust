

function Overlay_Pull_Down(ID){
    document.getElementById(ID).style.height = '100%';
}

function Overlay_Push_Up(ID){
    document.getElementById(ID).style.height = '0%';
}

function Auto_Login_Open(ID){

    if (document.TEST == "True"){
        document.getElementById(ID).style.height = '100%';
    }

}

function Invalid_Login() {
    document.TEST = "True"
  }

function Replace_Delete_Text(Text_ID, Form_ID, Source){
    let text = document.getElementById(Text_ID).innerHTML; 
    document.getElementById(Text_ID).innerHTML = text.replace(text.valueOf(),Source);
    let value = document.getElementById(Form_ID).value; 
    document.getElementById(Form_ID).value = value.replace(value.valueOf(), Source);
    }

function Auto_Select_Dropdown(ID, Value){
    let element = document.getElementById(ID);
    element.value = Value;
}

var interval = setInterval(function(){Update_Progress(); Downloads_Progress();}, 100);
function Update_Progress(){
    $.getJSON("/_download_Progress",
    function(data) {
        for (row in data){
            let id = data[row][0];
            let percentage = data[row][1];   
            let elem = document.getElementById(id+'_progressbar');        
            elem.style.width= percentage + '%';
        }
        //console.log(data)
    });
}

function Downloads_Progress(){
    $.getJSON("/_download_Progress",
    function(data) {
        var files = 0;
        var downloaded = 0;
        for (row in data){
            files += 1;
            let percentage = data[row][1];
            if (percentage == 100){
                downloaded += 1;
            }
        }
        var percentage = (downloaded / files) * 100;
        $('#progress_status').text(downloaded+' / '+files);
        document.getElementById('progressbar').style.width= percentage + '%';
    });
}


