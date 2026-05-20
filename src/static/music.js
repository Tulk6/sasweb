function play_audio(element){
    var audio_element = element.nextElementSibling;
    if (audio_element.paused){
        audio_element.play();
        element.innerHTML = "&#9208; playing....";
    }else{
        audio_element.pause()
        element.innerHTML = "&#9205; click to play";
    }
}
