/**
 * @file smartmirror-center-display.js
 *
 * @author nkucza
 * @license MIT
 *
 * @see  https://github.com/NKucza/smartmirror-center-display
 */

Module.register('SmartMirror-Center-Display',{

	defaults: {
		image_height: 1080,
		image_width: 1920,
		height: 540,
		width: 960,
		port: 5003,
		forgroundFPS: 30,
		backgroundFPS: 5,
		ai_art_mirror: true		
	},

	start: function() {
		self = this;
		this.is_shown = false;
		this.is_already_build = false;
		
		this.sendSocketNotification('CONFIG', this.config);	

		Log.info('Starting module: ' + this.name);

	},

	getDom: function () {

		Log.info('REFRESH DOM:  ' + this.name);
		var wrapper = document.createElement("div");
		wrapper.className = "video";

		if(this.is_shown) {
            wrapper.innerHTML = "<iframe width=\"" + this.config.image_width + "\" height=\"" + this.config.image_height + "\" src=\"http://0.0.0.0:"+ this.config.port +"\" frameborder=\"0\" allowfullscreen></iframe>";
            //wrapper.innerHTML = "<iframe width=\"" + this.config.width +"\" height=\"" + this.config.height + "\" src=\"http://0.0.0.0:5000/video_feed\" frameborder=\"0\" allowfullscreen></iframe>";
		};

		return wrapper;

	},

	suspend: function(){
		//this.sendNotification(this.config.publischerName + "SetFPS", this.config.backgroundFPS);
	},

	resume: function(){
		//this.sendNotification(this.config.publischerName + "SetFPS", this.config.forgroundFPS);
		this.is_shown = true;
		if(!this.is_already_build) {
            this.updateDom();
            this.is_already_build = true;
        };
	},

    notificationReceived: function(notification, payload) {
		if(notification === 'CENTER_DISPLAY') {
			this.sendSocketNotification('CENTER_DISPLAY', payload);
		}else if (notification === 'DETECTED_GESTURES') {
			this.sendSocketNotification('DETECTED_GESTURES', payload);
		}else if (notification === 'DETECTED_FACES') {
			this.sendSocketNotification('DETECTED_FACES', payload);
		}else if (notification === 'DETECTED_OBJECTS') {
			this.sendSocketNotification('DETECTED_OBJECTS', payload);
		}else if (notification === 'GESTURE_DET_FPS') {
			this.sendSocketNotification('GESTURE_DET_FPS', payload);
		}else if (notification === 'OBJECT_DET_FPS') {
			this.sendSocketNotification('OBJECT_DET_FPS', payload);
		}else if (notification === 'FACE_DET_FPS') {
			this.sendSocketNotification('FACE_DET_FPS', payload);
		}else if (notification === 'RECOGNIZED_PERSONS') {
			this.sendSocketNotification('RECOGNIZED_PERSONS', payload);
		}
    },
	
	// Override socket notification handler.
	socketNotificationReceived: function(notification, payload) {
		if (notification === 'CENTER_DISPLAY_FPS') {
			this.sendNotification('CENTER_DISPLAY_FPS', payload);
		}
	},


    getStyles: function () {
        return ['style.css'];
    }

});
