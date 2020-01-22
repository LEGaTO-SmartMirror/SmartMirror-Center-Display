'use strict';
const NodeHelper = require('node_helper');

const {PythonShell} = require('python-shell');
var pythonStarted = false


//var websockets = require("websockets");

module.exports = NodeHelper.create({

	python_start: function () {
		const self = this;
		console.log("[" + self.name + "] starting python");
    	self.pyshell = new PythonShell('modules/' + this.name + '/python_scripts/center-display-combine-threaded2.py', {pythonPath: 'python3', args: [JSON.stringify(this.config)]});

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

	// Subclass socketNotificationReceived received.
  socketNotificationReceived: function(notification, payload) {
	const self = this;
	if(notification === 'CONFIG') {
      this.config = payload
      this.python_start(); 
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
