
// ChatProject>static>js>online_status.js

const user = "{{ user }}"; // Assuming 'user' is available in your template

const online_status = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/'
    + 'online/'
)

online_status.onopen = function(e){
    console.log("CONNECTED TO ONLINE CONSUMER");
    online_status.send(JSON.stringify({
        'username': user, // Using the 'user' variable directly
        'type': 'open'
    }))
}

window.addEventListener("beforeunload", function(e){
    online_status.send(JSON.stringify({
        'username': user, // Using the 'user' variable directly
        'type': 'offline'
    }))
})

online_status.onclose = function(e){
    console.log("DISCONNECTED FROM ONLINE CONSUMER")
}

online_status.onmessage = function(e){
    var data = JSON.parse(e.data)
    if(data.username != user){ // Using the 'user' variable directly
        var user_to_change = document.getElementById(`${data.username}_status`)
        var small_status_to_change = document.getElementById(`${data.username}_small`)
        if(data.online_status == true){
            user_to_change.style.color = 'green'
            small_status_to_change.textContent = 'Online'
        }else{
            user_to_change.style.color = 'grey'
            small_status_to_change.textContent = 'Offline'
        }
    }
}