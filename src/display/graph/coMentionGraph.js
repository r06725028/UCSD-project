  // <!-- Some credits to: @eyaler forked from http://bl.ocks.org/eyaler/10586116 -->
    
  var w = window.innerWidth;
  var h = window.innerHeight;
  
  var focus_node = null,
  highlight_node = null;
  
  // var text_center = true;
  var outline = false;
  
  var min_score = 0;
  var max_score = 1;

  // Chunnan changed this to Color Universal Design (CUD) Colorblind barrier-free pallette
  // http://people.apache.org/~crossley/cud/cud.html
  var color = {
    0:'#e69f00',
    1:'#56b4e9',
    2:'#009e73',
    3:'#f0e442',
    4:'#0072b2',
    5:'#d55e00',
    6:'#cc79a7',
    7:'#cc79a7',  // not following CUD from here by Chunnan
    8:'#666666',
    9: '#666666',
    10: '#666666',
    11: '#666666',
    12: '#666666',
    13: '#666666',
    14: '#666666',
    15: '#666666',
    16: '#666666',
    17: '#666666',
    18: '#666666',
    19: '#666666',
    20: '#666666',
    21: '#666666',
    22: '#666666',
    23: '#666666',
    24: '#666666',
    25: '#666666',
    26: '#666666',
    27: '#666666',
    28: '#666666',
    29: '#666666',
    30: '#666666',
  };
  
  var highlight_color = '#265a6e'; // "blue"; Chunnan changed here...
  var highlight_trans = 0.1;
  
  var size = d3.scale.pow().exponent(1)
  .domain([1, 100])
  .range([8, 24]);
  
  var force = d3.layout.force()
  .linkDistance(500)
  .charge(-400)
  .size([w, h]);
  
  var default_node_color = "#ccc";
  var default_link_color = "#888";
  var nominal_base_node_size = 8;
  var nominal_text_size = 14;
  var max_text_size = 24;
  var nominal_stroke = 1.5;
  var max_stroke = 4.5;
  var max_base_node_size = 36;
  var min_zoom = 0.1;
  var max_zoom = 7;
  var svg = d3.select("body").append("svg");
  var zoom = d3.behavior.zoom().scaleExtent([min_zoom, max_zoom])
  var g = svg.append("g");
  svg.style("cursor", "move");
      
  var linkedByIndex = {};

  graph.links.forEach(function (d) {
    linkedByIndex[d.source + "," + d.target] = true;
  });

function isMaster(name) {
   return name.split(' ')[0].replace(/SCR_0*/g, '') == master_id
}

  function isConnected(a, b) {
    return linkedByIndex[a.index + "," + b.index] || linkedByIndex[b.index + "," + a.index] || a.index == b.index;
  }
  
  function hasConnections(a) {
    for (var property in linkedByIndex) {
      s = property.split(",");
      if ((s[0] == a.index || s[1] == a.index) && linkedByIndex[property]) return true;
    }
    return false;
  }
      
  force
    .nodes(graph.nodes)
    .links(graph.links)
    .start();
      
  var link = g.selectAll(".link")
    .data(graph.links)
    .enter().append("line")
    .attr("class", "link")
    .style("stroke-width", function(d) { return Math.sqrt(d.value); })
    .style("stroke", function (d) {
      if(d.source.name.split(' ')[0].replace(/SCR_0*/g, '') == master_id || 
        d.target.name.split(' ')[0].replace(/SCR_0*/g, '') == master_id) {
        return 'black' // <== master node link color
      }

      return default_link_color;
    })
      
      
  var node = g.selectAll(".node")
    .data(graph.nodes)
    .enter().append("g")
    // add id for JQuery trigger event
    .attr("id", function(n){ return n.id;  })
    .attr("class", "node")
    .call(force.drag)
      
  node.on("dblclick.zoom", function (d) {
    d3.event.stopPropagation();
    var dcx = (window.innerWidth / 2 - d.x * zoom.scale());
    var dcy = (window.innerHeight / 2 - d.y * zoom.scale());
    zoom.translate([dcx, dcy]);
    g.attr("transform", "translate(" + dcx + "," + dcy + ")scale(" + zoom.scale() + ")");
  });
      
  var tocolor = "fill";
  var towhite = "stroke";
  if (outline) {
    tocolor = "stroke"
    towhite = "fill"
  }
      
      var circle = node.append("path")
        .attr("d", d3.svg.symbol()
          .size(function (d) {
            return Math.PI * Math.pow(d.value * 8, 2);
          })
        )
        // Chunnan changed: Set master node color here... unnecessary!!!!
        .style(tocolor, function (d) {
        //  if(d.name.split(' ')[0].replace(/SCR_0*/g, '') == master_id) {
        //    return 'black'  
        //  }
          return color[d.group];
        })
        // .style("stroke-width", function(d) { return Math.sqrt(d.value); })
        // .style(towhite, "white")
        // <== Chunnan changed to add outter ring for master nodes
        .style(towhite, function(d) {
            if(isMaster(d.name)) {
            return "#444" // <== color of master node ring
          }
          return "white"
        })
        .style("stroke-width", function(d) {
            if(isMaster(d.name)) { 
              return d.value < 3.0 ? "10px" : "15px" // <== size of the master node ring
          }
        })
        // <== Chunnan added ends here...

      

      // put text into g node
      var text = node.append("text")
        .attr("dy", ".35em")
        .style("font-size", nominal_text_size + "px")

      // <== Chunnan defined 
      var bigNode = 4.5

      text.text(function (d) {
        return d.name.split(' ').slice(0, 1);
      })
    .style("text-anchor", function (d) {
	return d.value > bigNode ? "middle" : "start" 
    })
	   //"start") // "middle") <== Chunnan added to move the text left for small nodes
        // .attr("dx", "2.1em") // <== Chunnan added to move the text left for small nodes
        .attr("dx", function (d) {
            return d.value < bigNode ? 0.2+0.5*d.value.toString()+"em" : 0.0 
         })

//.style('stroke', function(d){  <== Chunnan changed here so the boldness of fonts are right
      .style('font-weight', function(d){
          if(isMaster(d.name)) { 
	    return 'bold'
        //    return 'black' // 'red' <== master node RRID text color
          }
	  return 'normal'
        })

      text.append("tspan")
        .attr("dy", "1.1em") // offest by 1.2 em
        .attr("x",0)
        //.attr("dx", "2.1em") // <== Chunnan added
        .attr("dx", function (d) {
            return d.value < bigNode ? 0.2+0.5*d.value.toString()+"em" : 0.0 
         })
        .text(function(d) {return d.name.split(' ').slice(1).join(' ');})
//.style('stroke', function(d){  // <== Chunnan commented out!!
 //     .style('font-weight', function(d){  
 //       if(d.name.split(' ')[0].replace(/SCR_0*/g, '') == master_id) {
 //	    return 'bold'
        //    return 'black' // 'red' <== master node name text color
 //          }
 //	   return 'normal'
 //       })

      
      node.on("click", function(d) {
        if (d3.event.defaultPrevented === true) {
          return
        } else {
          pid=d.name.split(' ')[0].replace(/SCR_0*/g, '')
          window.open(pid+'_main.html', "_blank"); // <== remove base URL eventually
        }
      })
        .on("mouseover", function (d) {
            set_highlight(d);
        })
        .on("mousedown", function (d) {
            d3.event.stopPropagation();
            focus_node = d;
            set_focus(d)
            if (highlight_node === null) set_highlight(d)
            
        })
        .on("mouseout", function (d) {
          exit_highlight();
        })
      
      d3.select(window).on("mouseup", () => {
        if (focus_node !== null) {
          focus_node = null;
          if (highlight_trans < 1) {
            circle.style("opacity", 1);
            text.style("opacity", 1);
            link.style("opacity", 1);
          }
        }
          
        if (highlight_node === null) exit_highlight();
      });
      
      function exit_highlight() {
        highlight_node = null;
        if (focus_node === null) {
          svg.style("cursor", "move");
          
        if (highlight_color != "white") {
            // <== Chunnan changed here...
            // circle.style(towhite, "white");
            circle.style(towhite,  function(d) {
		if(isMaster(d.name)) { 
                   return "#444" // <== color of master node ring
               }
               return "white"
            })
            text.style("font-weight",  function(d) {  // "normal");  <== Chunnan changed here
		if(isMaster(d.name)) { 
                   return "bold" 
               }
               return "normal"
            }) 
            link.style("stroke", function (d) {
		if(isMaster(d.source.name) || //.split(' ')[0].replace(/SCR_0*/g, '') == master_id || 
                   isMaster(d.target.name)) { //.split(' ')[0].replace(/SCR_0*/g, '') == master_id) {
                return 'black'
              }

              return default_link_color;
            })
          }
          
          [link, text, circle].forEach((obj) => {
            obj.style("opacity", o => 1);
          })
        }
      }
      
      function set_focus(d) {
        if (highlight_trans < 1) {
          circle.style("opacity", function (o) {
            return isConnected(d, o) ? 1 : highlight_trans;
          });
          
          text.style("opacity", function (o) {
            return isConnected(d, o) ? 1 : highlight_trans;
          });
          
          link.style("opacity", function (o) {
            return o.source.index == d.index || o.target.index == d.index ? 1 : highlight_trans;
          });
        }
      }
      
      function set_highlight(d) {
        svg.style("cursor", "pointer");
        if (focus_node !== null) d = focus_node;
        highlight_node = d;
        
        if (highlight_color != "white") {
          circle.style(towhite, function (o) {
            return isConnected(d, o) ? highlight_color : "white";
          });
            text.style("font-weight", function (o) {
             // return isConnected(d, o) ? "bold" : "normal";  
          });
          link.style("stroke", function (o) {
            return o.source.index == d.index || o.target.index == d.index ? highlight_color : default_link_color;
              
          });
        }

        circle.style("opacity", function (o) {
          return isConnected(d, o) ? 1 : highlight_trans;
        });
          
        text.style("opacity", function (o) {
          return isConnected(d, o) ? 1 : highlight_trans;
        });
        
        link.style("opacity", function (o) {
          return o.source.index == d.index || o.target.index == d.index ? 1 : highlight_trans;
        });
      }
      
      zoom.on("zoom", function () {
        var stroke = nominal_stroke;
        if (nominal_stroke * zoom.scale() > max_stroke) stroke = max_stroke / zoom.scale();
        link.style("stroke-width", function(d) { return Math.sqrt(d.value); });
        // circle.style("stroke-width", stroke);
        // Chunnan changed here...
        circle.style("stroke-width", function(d) {
            if(isMaster(d.name)) { //.split(' ')[0].replace(/SCR_0*/g, '') == master_id) {
                 return d.value < 3.0 ? "10px" : "15px" // <== master node ring size
             }
             return stroke
          })
        
        var base_radius = nominal_base_node_size;
        if (nominal_base_node_size * zoom.scale() > max_base_node_size) {
          base_radius = max_base_node_size / zoom.scale();
        }
        
        circle.attr("d", d3.svg.symbol()
          .size(function (d) {
              return Math.PI * Math.pow(d.value * 8, 2);
          })
          .type(function (d) {
              return d.type;
          }))
        
        // if (!text_center) text.attr("dx", function (d) {
        //     return (size(d.size) * base_radius / nominal_base_node_size || base_radius);
        // });
        
        var text_size = nominal_text_size;
        if (nominal_text_size * zoom.scale() > max_text_size) {
          text_size = max_text_size / zoom.scale();
        }
        text.style("font-size", text_size + "px");
        
        g.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
      });
      
      svg.call(zoom);
      
      resize();
      // window.focus();
      d3.select(window).on("resize", resize);
      
      force.on("tick", () => {

        node.attr("transform", function (d) {
          return "translate(" + d.x + "," + d.y + ")";
        });
        
        link.attr("x1", function (d) {
          return d.source.x;
        })
          .attr("y1", function (d) {
            return d.source.y;
          })
          .attr("x2", function (d) {
            return d.target.x;
          })
          .attr("y2", function (d) {
            return d.target.y;
          });
        
        node.attr("cx", function (d) {
          return d.x;
        })
          .attr("cy", function (d) {
            return d.y;
          });
      });
      
      function resize() {
          var width = window.innerWidth,
          height = window.innerHeight;
          svg.attr("width", width).attr("height", height);
          
          force.size([force.size()[0] + (width - w) / zoom.scale(), force.size()[1] + (height - h) / zoom.scale()]).resume();
          w = width;
          h = height;
      }

