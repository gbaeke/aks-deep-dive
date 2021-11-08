
const axios = require('axios');

const daprPort = process.env.DAPR_HTTP_PORT || 3500;
const topicName = process.env.TOPIC_NAME || "sampletopic";
const publishURL = `http://localhost:${daprPort}/v1.0/publish/pubsub/${topicName}`;

var counter=0

var publishLoop = setInterval(function(){
    axios.post(publishURL, {
        operation: counter
    })
    .then(function(response) {
        console.log('Message posted. Status = ' + response.status);
    })
    .catch(function (error){
        console.log(error);
    })

    
    counter++;
}, 5000);
