

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



