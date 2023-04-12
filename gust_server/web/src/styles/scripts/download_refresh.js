var interval = setInterval(function(){Update_Progress(); Downloads_Progress();}, 100);
function Update_Progress(){
    $.getJSON("/_download_Progress",
    function(data) {
        for (let row in data){
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
        for (let row in data){
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
