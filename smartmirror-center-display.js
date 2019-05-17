/**
 * @file smartmirror-center-display.js
 *
 * @author nkucza
 * @license MIT
 *
 * @see  https://github.com/NKucza/smartmirror-center-display
 */

Module.register('smartmirror-center-display',{

	defaults: {
		height: 540,
		width: 960,
		port: 5003,
		forgroundFPS: 30,
		backgroundFPS: 5
	},

	start: function() {
		self = this;
		this.is_shown = false;
		this.is_already_build = false;
		
		this.sendSocketNotification('CENTER_DISPLAY_CONFIG', this.config);	

		Log.info('Starting module: ' + this.name);

	},

	getDom: function () {

		Log.info('REFRESH DOM:  ' + this.name);
		var wrapper = document.createElement("div");
		wrapper.className = "video";

		if(this.is_shown) {
            wrapper.innerHTML = "<iframe width=\"" + this.config.width + "\" height=\"" + this.config.height + "\" src=\"http://0.0.0.0:"+ this.config.port +"\" frameborder=\"0\" allowfullscreen></iframe>";
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
		}
    },

    getStyles: function () {
        return ['style.css'];
    }

});
