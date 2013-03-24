// ####################################################################
// ###################### Cube Rendering ##############################
// ####################################################################

function hex_digit_from_int(num) {
    return num.toString(16);
}

function hex_from_float(num) {
  var i = Math.floor( num * 255 );
  var result = hex_digit_from_int( Math.floor(i/16) );
  result += hex_digit_from_int( i % 16 );
  return result;
}

function hex_colorstring_from_array( colorvec ) 
{
    return "#" 
            + hex_from_float(colorvec[2])
            + hex_from_float(colorvec[1])
            + hex_from_float(colorvec[0]);
}


var svg_polygons = [];

//-----------------------------------------------------------------------------
// This draws a quad, projecting it from world space to screenspace, and then rendering it.
// Arguments:
// viewProj: a matrix which concatenates the view + projection matrices
// viewProjViewport: a matrix which concatenates the view, projection, and viewport matrices
// 
//-----------------------------------------------------------------------------             
function drawQuad( ctx, viewProj, viewProjViewport, p1, p2, p3, p4, color, ndx ) 
{
    //TODO: a bunch of this vector math can be optimized out if we're
    // just rendering SVG and not canvas.
    // In fact, it should be asbracted out and cached only on view rotation.

    // Backface cull first
    var b1 = vectorMultiplyProjective( viewProj, p1 );
    var b2 = vectorMultiplyProjective( viewProj, p2 );
    var b3 = vectorMultiplyProjective( viewProj, p3 );
    var e1 = vectorSubtract( b2, b1 );
    var e2 = vectorSubtract( b3, b1 );
    var c = vectorCross( e1, e2 );
    if ( c.v[2] <= 0.0 )
    {
        if( RENDER_WITH_SVG ) {
            // Make sure it is hidden. This is actually not needed b/c clear_svg() takes care of it.
            if( svg_polygons[ndx] ) {
                clog("Hiding face " + ndx);
                $( svg_polygons[ndx] ).animate( {svgFillOpacity:0}, 0);
                svg_polygons[ndx] = 0;
            }
        }
        return;
    }

    //color = "rgba(" + Math.round(255.0*color[2]) + "," + Math.round(255.0*color[1]) + "," + Math.round(255.0*color[0]) + ",1)";
    // SVG rendering on ipad does not understand rgba colors!
    color = hex_colorstring_from_array(color);


    // Transform all points into viewport space
    var vp1 = vectorMultiplyProjective( viewProjViewport, p1 );  
    var vp2 = vectorMultiplyProjective( viewProjViewport, p2 );  
    var vp3 = vectorMultiplyProjective( viewProjViewport, p3 );  
    var vp4 = vectorMultiplyProjective( viewProjViewport, p4 );

    if( RENDER_WITH_CANVAS ) {
        ctx.fillStyle = color;
        ctx.globalAlpha = 1.0; 
         
        // Draw a filled quad  
        ctx.beginPath();   
        ctx.moveTo(vp1.v[0], vp1.v[1]);   
        ctx.lineTo(vp2.v[0], vp2.v[1]);   
        ctx.lineTo(vp3.v[0], vp3.v[1]);   
        ctx.lineTo(vp4.v[0], vp4.v[1]);   
        ctx.closePath();   
        ctx.fill();
    }

    if( RENDER_WITH_SVG ) {
        if( svg ) {
            // Does this facet exist already?
            if( svg_polygons[ndx] ) {
                // Yes.  Just update the color.
                $( svg_polygons[ndx] ).animate( {svgFill: color}, SVG_ANIMATION_SPEED );
                //clog("Animating svg face "+ndx);
            } else {
                //clog("Drawing svg face "+ndx + " with color " + color);
                // The polygon doesnt exist yet.  Create it.
                //svg_polygons[ndx] = svg.polygon([
                pg = svg.polygon([
                    [vp1.v[0], vp1.v[1]],
                    [vp2.v[0], vp2.v[1]],
                    [vp3.v[0], vp3.v[1]],
                    [vp4.v[0], vp4.v[1]]
                    ],  
                        {fill: color, strokeWidth: 0});
                svg_polygons[ndx] = pg;
            }
        }
    }
}   

//-----------------------------------------------------------------------------
// This returns true if the specified point in screen space is inside the
// quad specified in world space.
// Arguments:
// viewProj: a matrix which concatenates the view + projection matrices
// viewProjViewport: a matrix which concatenates the view, projection, and viewport matrices
//-----------------------------------------------------------------------------
function isPointInQuad( ctx, viewProj, viewProjViewport, p1, p2, p3, p4, point )
{
    // Backface cull first, ignore backfaced triangles
    var b1 = vectorMultiplyProjective( viewProj, p1 );
    var b2 = vectorMultiplyProjective( viewProj, p2 );
    var b3 = vectorMultiplyProjective( viewProj, p3 );
    var e1 = vectorSubtract( b2, b1 );
    var e2 = vectorSubtract( b3, b1 );
    var c = vectorCross( e1, e2 );
    if ( c.v[2] <= 0.0 )
    {
        return;
    }

    // Transform all points into viewport space
    var vp1 = vectorMultiplyProjective( viewProjViewport, p1 );
    var vp2 = vectorMultiplyProjective( viewProjViewport, p2 );
    var vp3 = vectorMultiplyProjective( viewProjViewport, p3 );
    var vp4 = vectorMultiplyProjective( viewProjViewport, p4 );

    // Now do a point in polygon test
    // See http://local.wasp.uwa.edu.au/~pbourke/geometry/insidepoly/  Solution 3 (2D)
    var i1 = (point.v[1] - vp1.v[1]) * (vp2.v[0] - vp1.v[0]) - (point.v[0] - vp1.v[0]) * (vp2.v[1] - vp1.v[1]);
    var i2 = (point.v[1] - vp2.v[1]) * (vp3.v[0] - vp2.v[0]) - (point.v[0] - vp2.v[0]) * (vp3.v[1] - vp2.v[1]);
    var i3 = (point.v[1] - vp3.v[1]) * (vp4.v[0] - vp3.v[0]) - (point.v[0] - vp3.v[0]) * (vp4.v[1] - vp3.v[1]);
    var i4 = (point.v[1] - vp4.v[1]) * (vp1.v[0] - vp4.v[0]) - (point.v[0] - vp4.v[0]) * (vp1.v[1] - vp4.v[1]);

    if ( ( i1 == 0 ) || ( i2 == 0 ) || ( i3 == 0 ) || ( i4 == 0 ) )
    {
        return 1;
    }

    if ( i1 > 0 )
    {
        return ( i2 > 0 ) && ( i3 > 0 ) && ( i4 > 0 );
    }

    return ( i2 < 0 ) && ( i3 < 0 ) && ( i4 < 0 );
}


// returns a hashmap with .ctx, .viewProj and .viewProjViewport
function build_view_context( ) {
    var canvas = document.getElementById("canvas");   
    var ctx = canvas.getContext("2d");   
    var altitude = $("#slide_alt").val() / 100.0;
    var azimuth = $("#slide_azi").val() / 100.0;

    var height = $('#canvas').attr('height');
    var width = $('#canvas').attr('width');
    var distance = 15;


    // Build the projection matrix
    // Note that the camera looks down -z in view space and the viewplane is at z = -1
    var aspectRatio = height / width;    
    var proj = buildProjectionMatrix( -0.3, 0.3, -0.3 * aspectRatio, 0.3 * aspectRatio, 1.0, 50.0 );

    // Build the view matrix
    var center = new vec4;
    var up = new vec4;

 	up.v[0] = up.v[1] = up.v[2] = 1.0;
	var start = new vec4;
	start.v[0] = start.v[1] = 1.0; start.v[2] = -1.0; start.v[3] = 0.0;
	var eyeUnnormalized = rotateVectorAboutAxisAndAngle( start, up, azimuth );
	var eye = vectorMultiplyScalar( vectorNormalize( eyeUnnormalized ), distance );

   	eye.v[3] = center.v[3] = up.v[3] = 0.0;   
    var view = buildViewMatrix( eye, center, up );    

    // Build the viewport transform
    var viewport = buildViewportTransform( width, height );
   
    // viewProjViewport matrix will transform all points from world space to screen space
    var viewProj = multiplyMatrix( proj, view );
    var viewProjViewport = multiplyMatrix( viewport, viewProj );    

    return { 'ctx': ctx,
             'viewProj': viewProj,
             'viewProjViewport': viewProjViewport
           };
}


// Returns a number 0-53 if the x,y point (relative to canvas) is one of the faces.
// Returns -1 if no match.
function whichFaceIsPointIn( x,y )
{
    var point = new vec4;
    point.v[0] = x;
    point.v[1] = y;

    var view_context = build_view_context();

    var quadlist = buildQuadList( view_context['ctx'], view_context['viewProj'], view_context['viewProjViewport'] );
    for( ndx=0; ndx<54; ndx++) {
        var quad = quadlist[ndx];
        if( isPointInQuad( view_context['ctx'], view_context['viewProj'], view_context['viewProjViewport'], quad[0], quad[1], quad[2], quad[3], point ) ) {
            // found it.  break out of loop.
            return ndx;
        }
    }
    return -1;
}


function buildQuadList( ctx, viewProj, viewProjViewport ) {
    // This code generates the 54 quads representing the 54 pixels of the cube    
    var crossAxis = [ [1, 2], [0, 2], [0, 1] ];
    var invertAxis = [ [false, false], [true, false], [true, false], [false, false], [false, false], [true, false] ];
    var gapSize = 0.08;
    var p = new vec4;
    var d = [ 0.0, 0.0, 0.0 ];
    var g = [ 0.0, 0.0, 0.0 ];

    var black = [ 0.0, 0.0, 0.0, 0.0 ];
    var quadlist = [];
    for ( var i = 0; i < 6; ++i )
    {
        var axis = i >> 1;
        p.v[axis] = 3.0;
        if ( i & 1 )
        {
            p.v[axis] *= -1.0;
        }
        d[axis] = 0.0;

        var a0 = crossAxis[ axis ][ 0 ];
        var a1 = crossAxis[ axis ][ 1 ];
        var s0 = 1.0;
        var s1 = 1.0;
        if ( invertAxis[ i ][ 0 ] )
        {
            s0 *= -1.0;
        }
        if ( invertAxis[ i ][ 1 ] )
        {
            s1 *= -1.0
        }
        d[a0] = ( 2.0 - 2.0 * gapSize ) * s0;
        d[a1] = ( 2.0 - 2.0 * gapSize ) * s1;
        g[a0] = gapSize * s0;
        g[a1] = gapSize * s1;
        p.v[a1] = -3.0 * s1 + g[a1];
        for ( var j = 0; j < 3; j++ )
        {
            p.v[a0] = -3.0 * s0 + g[a0]
            for ( var k = 0; k < 3; k++ )
            {           
                var p1 = vectorCopy( p );

                p.v[ a0 ] += d[ a0 ]
                var p2 = vectorCopy( p );

                p.v[ a1 ] += d[ a1 ];
                var p3 = vectorCopy( p );
                
                p.v[ a0 ] -= d[ a0 ];
                var p4 = vectorCopy( p );

                var ndx = i*9 + j*3 + k        
                quadlist[ ndx ] = [p1,p2,p3,p4];
                
                p.v[ a1 ] -= d[ a1 ];
                p.v[ a0 ] += d[ a0 ] + 2.0 * g[ a0 ];
            }                     
            p.v[ a1 ] += d[ a1 ] + 2.0 * g[ a1 ];
        }
    }           
    return quadlist;
}

//-----------------------------------------------------------------------------
//  This determines whether an arrow should be drawn, and/or should be 
//   available for click
//-----------------------------------------------------------------------------
function shouldDrawArrow( faceNum )
{
    // If we're in single player mode, verify that this arrow is intended for this player
    if ( ignore_clicks ){
		  return false;
		}

		if ( client_state == "MULT" )  
    {
			if (arrowRotation[faceNum][2] != position)
					return false;
    }

    // Verify that this is a facet that deserves an arrow in any condition
    return (arrowRotation[faceNum][0] != 0);

}

//-----------------------------------------------------------------------------
// This draws an arrow, projecting it from world space to screenspace, and then rendering it.
// Arguments:
// viewProj: a matrix which concatenates the view + projection matrices
// viewProjViewport: a matrix which concatenates the view, projection, and viewport matrices
// p1-p4: the 4 quad points to render in
// orientation: a number 0-3 indicating the orientation
//-----------------------------------------------------------------------------
function drawArrow( ctx, viewProj, viewProjViewport, p1, p2, p3, p4, orientation, color )
{
    // Backface cull first
    var b1 = vectorMultiplyProjective( viewProj, p1 );
    var b2 = vectorMultiplyProjective( viewProj, p2 );
    var b3 = vectorMultiplyProjective( viewProj, p3 );
    var e1 = vectorSubtract( b2, b1 );
    var e2 = vectorSubtract( b3, b1 );
    var c = vectorCross( e1, e2 );
    if ( c.v[2] <= 0.0 )
    {
        return;
    }

    ctx.fillStyle = "rgba(" + Math.round(255.0*color[2]) + "," + Math.round(255.0*color[1]) + "," + Math.round(255.0*color[0]) + ",1)";
    ctx.globalAlpha = 1.0;

    // Build basis
    var origin;
    var up;
    var right;
    if ( orientation == 0 )
    {
        origin = p1;
        up = vectorSubtract( p4, p1 );
        right = vectorSubtract( p2, p1 );
    }
    else if ( orientation == 1 )
    {
        origin = p2;
        up = vectorSubtract( p1, p2 );
        right = vectorSubtract( p3, p2 );
    }
    else if ( orientation == 2 )
    {
        origin = p3;
        up = vectorSubtract( p2, p3 );
        right = vectorSubtract( p4, p3 );
    }
    else if ( orientation == 3 )
    {
        origin = p4;
        up = vectorSubtract( p3, p4 );
        right = vectorSubtract( p1, p4 );
    }

    // Build arrow points
    var borderAmount = 0.1;
    var baseAmount = 0.3;
    var arrowVertAmount = 0.4;

    var a1 = vectorMultiplyAdd2( origin, up, borderAmount, right, baseAmount );
    var a2 = vectorMultiplyAdd2( origin, up, borderAmount, right, 1.0 - baseAmount );
    var a3 = vectorMultiplyAdd2( origin, up, arrowVertAmount, right, 1.0 - baseAmount );
    var a4 = vectorMultiplyAdd2( origin, up, arrowVertAmount, right, 1.0 - borderAmount );
    var a5 = vectorMultiplyAdd2( origin, up, 1.0 - borderAmount, right, 0.5 );
    var a6 = vectorMultiplyAdd2( origin, up, arrowVertAmount, right, borderAmount );
    var a7 = vectorMultiplyAdd2( origin, up, arrowVertAmount, right, baseAmount );

    // Transform all points into viewport space
    var vp1 = vectorMultiplyProjective( viewProjViewport, a1 );
    var vp2 = vectorMultiplyProjective( viewProjViewport, a2 );
    var vp3 = vectorMultiplyProjective( viewProjViewport, a3 );
    var vp4 = vectorMultiplyProjective( viewProjViewport, a4 );
    var vp5 = vectorMultiplyProjective( viewProjViewport, a5 );
    var vp6 = vectorMultiplyProjective( viewProjViewport, a6 );
    var vp7 = vectorMultiplyProjective( viewProjViewport, a7 );

    // Draw a filled quad
    ctx.beginPath();
    ctx.moveTo(vp1.v[0], vp1.v[1]);
    ctx.lineTo(vp2.v[0], vp2.v[1]);
    ctx.lineTo(vp3.v[0], vp3.v[1]);
    ctx.lineTo(vp4.v[0], vp4.v[1]);
    ctx.lineTo(vp5.v[0], vp5.v[1]);
    ctx.lineTo(vp6.v[0], vp6.v[1]);
    ctx.lineTo(vp7.v[0], vp7.v[1]);
    ctx.closePath();
    ctx.fill();
}

// x = 1,-1 y = 2,-2 z = 3,-3 !rotate = 0
// Second ordinal is the row #
arrowRotation = [
		 [2,2,3],[0,0,3],[-2,2,3],[2,1,3],[0,0,3],[-2,1,3],[2,0,3],[0,0,3],[-2,0,3],  
		 [2,2,3],[0,0,3],[-2,2,3],[2,1,3],[0,0,3],[-2,1,3],[2,0,3],[0,0,3],[-2,0,3], 

		 [3,0,1],[3,1,1],[3,2,1],[0,0,1],[0,0,1],[0,0,1],[-3,0,1],[-3,1,1],[-3,2,1],
		 [-3,2,1],[-3,1,1],[-3,0,1],[0,0,1],[0,0,1],[0,0,1],[3,2,1],[3,1,1],[3,0,1],

		 [1,2,2],[0,0,2],[-1,2,2],[1,1,2],[0,0,2],[-1,1,2],[1,0,2],[0,0,2],[-1,0,2],
		 [1,2,2],[0,0,2],[-1,2,2],[1,1,2],[0,0,2],[-1,1,2],[1,0,2],[0,0,2],[-1,0,2],
];

// x[],y[],z[] then
// +x,-x,+y,-y,+z,-z
rotToOrient = [[ -1, -1, 1, 3, 1, 1 ],
               [ 1, 1, -1, -1, 0, 0 ], 
               [ 2, 2, 2, 0, -1, -1 ]];


function clear_svg() {
    if( RENDER_WITH_SVG ) {
        if( svg ) {
            svg.clear();
        }
    }
    svg_polygons = [];
}

function drawCube( ctx, viewProj, viewProjViewport, colors )
{
	var red = [ 0.0, 0.7, 1.0 ];
    var quadlist = buildQuadList( ctx, viewProj, viewProjViewport );
    for( ndx=0; ndx<54; ndx++) {
        var quad = quadlist[ndx];

        // draw the arrow slightly darker than the actual color
        var darkcolor = [ colors[ndx][0]*.6, colors[ndx][1]*.6, colors[ndx][2]*.6 ]
        drawQuad( ctx, viewProj, viewProjViewport, quad[0], quad[1], quad[2], quad[3], colors[ndx], ndx );
		var arrowDirection = -1;
		if (shouldDrawArrow(ndx)) {
            var sign = arrowRotation[ndx][0] < 0;
            arrowDirection = rotToOrient[Math.abs(arrowRotation[ndx][0]) - 1][Math.floor(ndx / 9)]
            if (sign) {
              arrowDirection = (2 + arrowDirection) % 4
            }
            //clog(arrowRotation[ndx], Math.floor(ndx/9), sign, arrowDirection)
            if (arrowDirection >= 0) 
			{
			    if( INCLUDE_ARROWS ) 
				{
              		drawArrow( ctx, viewProj, viewProjViewport, quad[0], quad[1], quad[2], quad[3], arrowDirection, darkcolor );
            	}
			}
        }

		if ( ( lastFaceClicked >= 0 ) && (lastFaceClicked == ndx ) )
		{
       		if (arrowDirection >= 0) 
			{
	             drawArrow( ctx, viewProj, viewProjViewport, quad[0], quad[1], quad[2], quad[3], arrowDirection, red );
	        }
			renderClickedFaceCount--;
			if ( renderClickedFaceCount <= 0 )
			{
				lastFaceClicked = -1;
			}
		}
    }           
}


    // Initialize the cube with gray until it connects to the server.
    var current_cube_colors = new Array( 54 );
    var index = 0;
    for ( var i = 0; i < 6; ++i )
    {
        for ( var j = 0; j < 9; ++j )
        {
            current_cube_colors[index] = [0.2, 0.2, 0.2];
            index++;            
        }
    }


function render_view( width, height, altitude, azimuth, distance ) 
{ 
    var canvas = document.getElementById("canvas");   
    var ctx = canvas.getContext("2d");   

    // Clear to black
    ctx.save();   
    ctx.fillStyle = "black";   
    ctx.fillRect( 0, 0, width, height );   
    ctx.restore();   
    
    var view_context = build_view_context();
    drawCube( view_context['ctx'], view_context['viewProj'], view_context['viewProjViewport'], current_cube_colors );
}

