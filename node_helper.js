'use strict';
const NodeHelper = require('node_helper');
const { spawn, exec } = require('child_process');
const {PythonShell} = require('python-shell');
var pythonStarted = false

var cAppStarted = false
//var websockets = require("websockets");

module.exports = NodeHelper.create({

	python_start: function () {
		const self = this;
		console.log("[" + self.name + "] starting python");
    	self.pyshell = new PythonShell('modules/' + this.name + '/python_scripts/center-display-combine.py', {pythonPath: 'python3', args: [JSON.stringify(this.config)]});

		self.pyshell.on('message', function (message) {
			try {
				var parsed_message = JSON.parse(message)
				//console.log("[MSG " + self.name + "] " + parsed_message);
      				if (parsed_message.hasOwnProperty('status')){
      					console.log("[" + self.name + "] " + JSON.stringify(parsed_message.status));
      				}if (parsed_message.hasOwnProperty('error')){
      					console.log("ERROR! [" + self.name + "] " + parsed_message.error);
      				}if (parsed_message.hasOwnProperty("CENTER_DISPLAY_FPS")){
						self.sendSocketNotification('CENTER_DISPLAY_FPS', parsed_message.CENTER_DISPLAY_FPS);
					}

	
			}
			catch(err) {
				//console.log("[" + self.name + "] a non json message received");
				console.log("[" + self.name + "] message received: " + message);
				//console.log(err);
			}
    		});

	},
	cApp_start: function () {
		const self = this;
		self.centerDisplay = spawn('modules/' + this.name + '/cplusplus/build/center_display',['modules/' + this.name + '/build/center_display', self.config]);
		self.centerDisplay.stdout.on('data', (data) => {
			try{
				var parsed_message = JSON.parse(`${data}`)

				if (parsed_message.hasOwnProperty('DETECTED_OBJECTS')){
					//console.log("[" + self.name + "] detected object: " + parsed_message.detected.name + " center in "  + parsed_message.detected.center);
					self.sendSocketNotification('DETECTED_OBJECTS', parsed_message);
				}else if (parsed_message.hasOwnProperty('OBJECT_DET_FPS')){
					//console.log("[" + self.name + "] object detection fps: " + JSON.stringify(parsed_message));
					self.sendSocketNotification('OBJECT_DET_FPS', parsed_message.OBJECT_DET_FPS);
				}else if (parsed_message.hasOwnProperty('STATUS')){
					console.log("[" + self.name + "] status received: " + JSON.stringify(parsed_message));
				}
			}
			catch(err) {
				
				//console.log(err)
			}
  			//console.log(`stdout: ${data}`);
		});	
		exec(`renice -n 20 -p ${self.objectDet.pid}`,(error,stdout,stderr) => {
				if (error) {
					console.error(`exec error: ${error}`);
  				}
			});

  	},
	  


	// Subclass socketNotificationReceived received.
  socketNotificationReceived: function(notification, payload) {
	const self = this;
	if(notification === 'CONFIG') {
      this.config = payload
	  this.python_start(); 
	  if (!cAppStarted){
		this.cApp_start();
		cAppStarted = true;
	  }  
	  
    }else if(notification === 'CENTER_DISPLAY'){
		var data = {"SET": payload};
		self.pyshell.send(JSON.stringify(data));
	}else if (notification === 'DETECTED_GESTURES'){
		self.pyshell.send(JSON.stringify(payload));
	}else if (notification === 'DETECTED_OBJECTS'){
		self.pyshell.send(JSON.stringify(payload));
	}else if (notification === 'DETECTED_FACES'){
		self.pyshell.send(JSON.stringify(payload));
	}else if (notification === 'RECOGNIZED_PERSONS'){
		self.pyshell.send(JSON.stringify(payload));
	}else if (notification === 'GESTURE_DET_FPS'){
		var data = {"GESTURE_DET_FPS": payload};
		self.pyshell.send(JSON.stringify(data));
	}else if (notification === 'OBJECT_DET_FPS'){
		var data = {"OBJECT_DET_FPS": payload};
		self.pyshell.send(JSON.stringify(data));
	}else if (notification === 'FACE_DET_FPS'){
		var data = {"FACE_DET_FPS": payload};
		self.pyshell.send(JSON.stringify(data));
	};
  },

	stop: function() {
		const self = this;
		self.pyshell.childProcess.kill('SIGINT');
		self.pyshell.end(function (err) {
           	if (err){
        		//throw err;
    		};
    		console.log('finished');
		});
		self.pyshell.childProcess.kill('SIGKILL');
	}

});
