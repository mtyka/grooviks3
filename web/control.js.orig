// ####################################################################
// ######################## SoundManager2 #############################
// ####################################################################
{% include "soundmanager2-nodebug-jsmin.js" %}





var client_state = "IDLE";
var game_state = "UNBOUND";
var active_position = 0;


var ignore_clicks = false;
var locked_buttons=false;
var menustate = 0;
var interrupt_ok=true;
// 0 = no menu
// 1 = mode menu
// 2 = level menu
// 3 = timeout menu
// 4 = join    menu
// 5 = waiting menu



soundManager.url = 'static';
//soundManager.preferFlash = false;
soundManager.useHTML5Audio = false;
soundManager.flashVersion = 9;
soundManager.useFastPolling = true;
soundManager.useHighPerformance = true;
soundManager.onload = function(){
    soundManager.createSound({
        id: 'column1_1',
        url: '/static/synth_8bit_low_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column1_2',
        url: '/static/synth_8bit_med_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column1_3',
        url: '/static/synth_8bit_high_001.mp3',
        autoLoad: true 
    }); 

     soundManager.createSound({
        id: 'column2_1',
        url: '/static/synth_tal_low_002.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column2_2',
        url: '/static/synth_tal_med_002.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column2_3',
        url: '/static/synth_tal_high_002.mp3',
        autoLoad: true
    });    
    
    soundManager.createSound({
        id: 'column3_1',
        url: '/static/vocoder_low_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column3_2',
        url: '/static/vocoder_med_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'column3_3',
        url: '/static/vocoder_high_001.mp3',
        autoLoad: true
    });
    soundManager.createSound({
        id: 'gear1',
        url: '/static/gear_001.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'gear2',
        url: '/static/gear_002.mp3',
        autoLoad: true
    });

    soundManager.createSound({
        id: 'gear3',
        url: '/static/gear_003.mp3',
        autoLoad: true
    });
};

function playFaceClickSound(frame){
	var playerNumber = Math.floor(frame.payload[1]/ 3) + 1;
	var columnNumber = (frame.payload[1] % 3) + 1;
        var faceSound = soundManager.getSoundById('column'+ playerNumber  + '_' + columnNumber);
	soundManager.stopAll();
	faceSound.play();
}

function playRotationSound(rotationStep){
	clog(rotationStep);
        if(rotationStep ){
            var gearSound = soundManager.getSoundById('gear' + rotationStep );
	    //soundManager.stopAll();
            gearSound.play();
        }
}

// ####################################################################
// ######################## Control Logic #############################
// ####################################################################


// safe way to log things on webkit and not blow up firefox
function clog(msg) {
    if( window.console ) {
        console.log(msg);
    }
}


var previous_datagram = null;

function on_message_pushed( datagram ) {
     $('#cube_status').html('Begin play.');
     $('#cube_status').animate({'opacity': 0}, 4000 );

     //clog("Got message published");
     //clog( datagram );
     if ( client_state != "MULT" && client_state != "SING" ) {
         current_cube_colors = decompress_datagram( datagram );
         if( previous_datagram != datagram ) {
            reset_arrow_timer();
            previous_datagram = datagram;
         }
         update_view();  // calls into the renderer code
     }
}


function set_grey() {
    for(var i=0; i<54; i++ ) {
        current_cube_colors[i] = [0.5,0.5,0.5];
    }
    update_view();
}

function on_game_state_change(newState, activePosition, clientstate) {
//     game_state = newState
     $('#game_state').val( newState )
     $('#active_position').val( activePosition )
     
		 new_client_state = clientstate[position-1];

		 clog("Server: NewState:" + new_client_state + "OldState: " + client_state ); 
		 // is there a change in client state ? 
		 if ( new_client_state != client_state ){
			 client_state = new_client_state;
			 if ( client_state == "IDLE" ){
				 goto_idle_screen();
			 } else
			 if ( client_state == "HOME" ){
				 goto_mode_screen();
			 } else
			 if ( client_state == "SING" ){
                 set_grey();
				 clear_screen();
			 } else
			 if ( client_state == "MULT" ){
                 set_grey();
				 clear_screen();
			 } else
			 if ( client_state == "VICT" ){
				 clear_screen();
			 }else{
				 clog("Unknown client_state:" + client_state );
			 }
		}


		new_game_state = newState;

		clog("Server: NewGameState:" + new_game_state + "OldGameState: " + game_state ); 
		if ( new_game_state != game_state ){
			game_state = new_game_state;
			 if ( client_state == "IDLE" ) { }
			 if ( client_state == "HOME" ){
			 } else
			 if ( client_state == "SING" ){
				 if( game_state == "SINGLE_INVITE" ){
           goto_join_screen();
				 } else
				 if( game_state == "SINGLE" ){
           clear_screen();
				 } else
				 if( game_state == "VICTORY" ){
           clear_screen();
				 }
			 } else {
			 if ( client_state == "MULT" ){
				 if( game_state == "SINGLE_INVITE" ){
           goto_waiting_screen();
				 } else
				 if( game_state == "MULTIPLE" ){
           clear_screen();
				 } else
				 if( game_state == "VICTORY" ){
           clear_screen();
				 }
			 } 
			}

		}

}


// Converts a long hex string into an array of 54 RGB-float-triples
function decompress_datagram(datagram) {
    //clog("decompressing...");
    //clog(datagram);
    var output = [];

    while( datagram.length > 0 ) {
        var rgb = datagram.substring(0,6);
        datagram = datagram.substring(6);
        output[output.length] = parse_hex_rgb(rgb);
    }
    //clog("decompressed to...");
    //clog(output);
    return output;
}

function parse_hex_rgb(hexstring) {
    var rgb_floats = [];
    for(i=0; i<3; i++) {
      var rgbhex = hexstring.substring(i*2, 2 + i*2);
      var rgbint = parseInt(rgbhex,16);
      rgb_floats[i] = rgbint / 255.0;
    }
    return rgb_floats;
}



//
// Logic to turn arrows off when moving
//

var INCLUDE_ARROWS = false;

var enable_arrows_timeout = null;


function reset_arrow_timer() {
    INCLUDE_ARROWS = false;
    clearTimeout( enable_arrows_timeout );
    enable_arrows_timeout = setTimeout( show_arrows, HOW_LONG_STABLE_BEFORE_SHOWING_ARROWS );
}

function show_arrows() {
    INCLUDE_ARROWS = true;
    update_view();
}



//
// rendering stuff
//


function update_view() {
   // looks at the view sliders and renders-the cube with that and the current color-state
   var altitude = $("#slide_alt").val() / 100.0;
   var azimuth = $("#slide_azi").val() / 100.0;
   var height = $('#canvas').attr('height');
   var width = $('#canvas').attr('width');
   render_view(height, width, altitude, azimuth, 15 );
   //window.setTimeout( update_view, 50 );

   frames_rendered ++;
}





function set_ignore_clicks( value ){
	ignore_clicks = value;
}

function rotate_view() {
    clear_svg();
    update_view();
}

 $(document).ready( function() {
    // Draw the cube in its default state when the page first loads
    update_view();

		$("body").click( function( eventObj ) {
			if( !ignore_clicks ){
				 //var x = eventObj.pageX;
				 //var y = eventObj.pageY;
				 //clog("local click at absolute ("+x+","+y+")");

				 var top_left_canvas_corner = $("#canvas").elementlocation();
				 var x = eventObj.pageX - top_left_canvas_corner.x;
				 var y = eventObj.pageY - top_left_canvas_corner.y;

				 //clog("local click at relative ("+x+","+y+")");

				 cube_got_clicked_on(x,y);
			
				 return true;
			}
		});
});

var faceclick_subscription;
var lastFaceClicked = -1;
var renderClickedFaceCount = 0;

function cube_got_clicked_on(x,y) 
{
    facenum = whichFaceIsPointIn(x,y);
    if( facenum < 0 )
	{
     	// not on a cube face
     	clog("Local click not on cube face.");
     	return;
    }
    //faceclick_subscription.publish( facenum );  // docs say this should work but it doesn't
    if (shouldDrawArrow(facenum)) {
        clog("Publishing local click on face "+facenum);
      	var rotation_direction = arrowRotation[facenum][0] > 0;
      	// See QueueRotation in groovik.py
      	// TODO(bretford): mapping is weird, fix
      	var rotation_index = arrowRotation[facenum][1] + (Math.abs(arrowRotation[facenum][0]))%3*3;
      	hookbox_conn.publish('faceclick', [facenum, rotation_index, rotation_direction] );
    
		if ( INCLUDE_ARROWS )
		{
			lastFaceClicked = facenum;
			renderClickedFaceCount = 5;
		}
	}
}

function reset_gamestate(position, difficulty) {
    clog("Resetting gamestate: " + difficulty);
    hookbox_conn.publish('clientcommand', {'position' : position, 'command' : 'SELECT_DIFFICULTY', 'difficulty' : difficulty});
}


// ####################################################################
// #################### Communications Setup ##########################
// ####################################################################

var hookbox_conn = null;
var subscription = null;


function establish_hookbox_connections() {
    if( !is_hookbox_loaded ) {
        alert("Failed to connect to hookbox server.");
    }

    // create a connection object and setup the basic event callbacks.
    hookbox_conn = hookbox.connect(server);
    //hookbox_conn.onOpen = function() { alert("connection established!"); };
    hookbox_conn.onError = function(err) { alert("Failed to connect to hookbox server: " + err.msg); };

    subscription = null;
    hookbox_conn.onSubscribed = function(channelName, _subscription) {
        if( channelName == 'iframe' ) {
            subscription = _subscription;                
            subscription.onPublish = function(frame) {
                on_message_pushed( frame.payload );
            };  
        }
        if( channelName == 'faceclick' ) {
            faceclick_subscription = _subscription;                
            faceclick_subscription.onPublish = function(frame) {
                playFaceClickSound(frame);
                clog('Heard about click on face ' + frame.payload);
            };  
        }
        if( channelName == 'gameState' ) {
        	gamestate_subscription = _subscription;
            gamestate_subscription.onPublish = function(frame) {
                on_game_state_change(frame.payload["gamestate"], frame.payload["active_position"], frame.payload["clientstate"]);
            };  
        }
        if( channelName == 'rotationStep' ) {
            rotation_subscription = _subscription;
            rotation_subscription.onPublish = function(frame) {
                playRotationSound(frame.payload);
            }
        }
    };

   // Subscribe to the pubsub channel with the colors
   hookbox_conn.subscribe("iframe");
   hookbox_conn.subscribe("faceclick");
   hookbox_conn.subscribe("gamemode");
   hookbox_conn.subscribe("gameState");
   hookbox_conn.subscribe("rotationStep");
}



