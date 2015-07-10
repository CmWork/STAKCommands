
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
<script type="text/javascript">
<!--
    function toggle_visibility(id) {
       var e = document.getElementById(id);
       var caption = document.getElementById(id + '.h3link');
       var text = caption.innerHTML
       if(e.style.display == 'block')
       {
          e.style.display = 'none';
          caption.innerHTML = text.replace('[-]', '[+]');
       }
       else
       {
          e.style.display = 'block';
          caption.innerHTML = text.replace('[+]', '[-]');
       }
    }
//!-->
</script>
<script type="text/javascript">
    var margin = {top: 20, right: 120, bottom: 20, left: 120},
        width = 960 - margin.right - margin.left,
        height = 800 - margin.top - margin.bottom;

    // var orientations = {
    //   "top-to-bottom": {
    //     size: [width, height],
    //     x: function(d) { return d.x; },
    //     y: function(d) { return d.y; }
    //   },
    //   "right-to-left": {
    //     size: [height, width],
    //     x: function(d) { return width - d.y; },
    //     y: function(d) { return d.x; }
    //   },
    //   "bottom-to-top": {
    //     size: [width, height],
    //     x: function(d) { return d.x; },
    //     y: function(d) { return height - d.y; }
    //   },
    //   "left-to-right": {
    //     size: [height, width],
    //     x: function(d) { return d.y; },
    //     y: function(d) { return d.x; }
    //   }
    // };

    var i = 0,
        duration = 750,
        root;

    var tree = d3.layout.tree()
        .size([width, height]);

    var diagonal = d3.svg.diagonal()
        .projection(function(d) { return [d.y, d.x]; });

    var svg = d3.select("body").append("svg")
        .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.json("./dmMap.json", function(error, flare) {
      if (error) throw error;

      root = flare;
      root.x0 = height / 2;
      root.y0 = 0;

      function collapse(d) {
        if (d.children) {
          d._children = d.children;
          d._children.forEach(collapse);
          d.children = null;
        }
      }

      root.children.forEach(collapse);
      update(root);
    });

    d3.select(self.frameElement).style("height", "800px");

    function update(source) {

      // Compute the new tree layout.
      var nodes = tree.nodes(root).reverse(),
          links = tree.links(nodes);

      // Normalize for fixed-depth.
      nodes.forEach(function(d) { d.y = d.depth * 180; });

      // Update the nodes
      var node = svg.selectAll("g.node")
          .data(nodes, function(d) { return d.id || (d.id = ++i); });

      // Enter any new nodes at the parent's previous position.
      var nodeEnter = node.enter().append("g")
          .attr("class", "node")
          .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
          .on("click", click);

      nodeEnter.append("circle")
          .attr("r", 10)
          .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

      nodeEnter.append("a")
          .attr("xlink:href", function(d) { return d.url; })
          .append("text")
            .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
            .attr("dy", ".35em")
            .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
            .text(function(d) { return d.name; })
            .style("fill-opacity", 1e-6);

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

      nodeUpdate.select("circle")
          .attr("r", 4.5)
          .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

      nodeUpdate.select("text")
          .style("fill-opacity", 1);

      // Transition exiting nodes to the parent's new position.
      var nodeExit = node.exit().transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
          .remove();

      nodeExit.select("circle")
          .attr("r", 1e-6);

      nodeExit.select("text")
          .style("fill-opacity", 1e-6);

      // Update the links
      var link = svg.selectAll("path.link")
          .data(links, function(d) { return d.target.id; });

      // Enter any new links at the parent's previous position.
      link.enter().insert("path", "g")
          .attr("class", "link")
          .attr("d", function(d) {
            var o = {x: source.x0, y: source.y0};
            return diagonal({source: o, target: o});
          });

      // Transition links to their new position.
      link.transition()
          .duration(duration)
          .attr("d", diagonal);

      // Transition exiting nodes to the parent's new position.
      link.exit().transition()
          .duration(duration)
          .attr("d", function(d) {
            var o = {x: source.x, y: source.y};
            return diagonal({source: o, target: o});
          })
          .remove();

      // Stash the old positions for transition.
      nodes.forEach(function(d) {
        d.x0 = d.x;
        d.y0 = d.y;
      });
    }

    // Toggle children on click.
    function click(d) {
      if (d.children) {
        d._children = d.children;
        d.children = null;
      } else {
        d.children = d._children;
        d._children = null;
      }
      update(d);
    }
//-->
</script>

# ttStreamBlockLoadProfile<br><font size="2">(ClassName:  StreamBlockLoadProfile)</font><h3><a id="ttStreamBlockLoadProfile.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamBlockLoadProfile');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamBlockLoadProfile"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Load</td><td>10</td></tr><tr><td>BurstSize</td><td>1</td></tr><tr><td>Name</td><td>StreamBlockLoadProfile 1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>InterFrameGap</td><td>12</td></tr><tr><td>LoadUnit</td><td>PERCENT_LINE_RATE</td></tr><tr><td>Priority</td><td>0</td></tr><tr><td>serializationBase</td><td>true</td></tr><tr><td>StartDelay</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>InterFrameGapUnit</td><td>BYTES</td></tr><tr><td>id</td><td>2112</td></tr></table></div>

# ttStreamModDstIp<br><font size="2">(ClassName:  RangeModifier)</font><h3><a id="ttStreamModDstIp.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamModDstIp');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamModDstIp"><table><tr><th>Property</th><th>Value</th></tr><tr><td>StepValue</td><td>0.0.0.1</td></tr><tr><td>Name</td><td>IPv4 Modifier</td></tr><tr><td>OffsetReference</td><td>ip_1.destAddr</td></tr><tr><td>RecycleCount</td><td>1</td></tr><tr><td>EnableStream</td><td>FALSE</td></tr><tr><td>Offset</td><td>0</td></tr><tr><td>Mask</td><td>255.255.255.255</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>DataType</td><td>NATIVE</td></tr><tr><td>RepeatCount</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Data</td><td>192.0.0.1</td></tr><tr><td>id</td><td>1411</td></tr><tr><td>ModifierMode</td><td>INCR</td></tr></table></div>

# ttStreamModDstMac<br><font size="2">(ClassName:  RangeModifier)</font><h3><a id="ttStreamModDstMac.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamModDstMac');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamModDstMac"><table><tr><th>Property</th><th>Value</th></tr><tr><td>StepValue</td><td>00:00:00:00:00:01</td></tr><tr><td>Name</td><td>MAC Modifier</td></tr><tr><td>OffsetReference</td><td>eth1.dstMac</td></tr><tr><td>RecycleCount</td><td>1</td></tr><tr><td>EnableStream</td><td>FALSE</td></tr><tr><td>Offset</td><td>0</td></tr><tr><td>Mask</td><td>00:00:FF:FF:FF:FF</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>DataType</td><td>NATIVE</td></tr><tr><td>RepeatCount</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Data</td><td>00:00:01:00:00:01</td></tr><tr><td>id</td><td>1407</td></tr><tr><td>ModifierMode</td><td>INCR</td></tr></table></div>

# ttStreamModGateway<br><font size="2">(ClassName:  RangeModifier)</font><h3><a id="ttStreamModGateway.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamModGateway');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamModGateway"><table><tr><th>Property</th><th>Value</th></tr><tr><td>StepValue</td><td>0.0.0.1</td></tr><tr><td>Name</td><td>IPv4 Modifier</td></tr><tr><td>OffsetReference</td><td>ip_1.gateway</td></tr><tr><td>RecycleCount</td><td>1</td></tr><tr><td>EnableStream</td><td>FALSE</td></tr><tr><td>Offset</td><td>0</td></tr><tr><td>Mask</td><td>255.255.255.255</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>DataType</td><td>NATIVE</td></tr><tr><td>RepeatCount</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Data</td><td>192.85.1.1</td></tr><tr><td>id</td><td>1410</td></tr><tr><td>ModifierMode</td><td>INCR</td></tr></table></div>

# ttStreamFragFlag<br><font size="2">(ClassName:  RangeModifier)</font><h3><a id="ttStreamFragFlag.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamFragFlag');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamFragFlag"><table><tr><th>Property</th><th>Value</th></tr><tr><td>StepValue</td><td>1</td></tr><tr><td>Name</td><td>Modifier</td></tr><tr><td>OffsetReference</td><td>ip_1.flags.mfBit</td></tr><tr><td>RecycleCount</td><td>1</td></tr><tr><td>EnableStream</td><td>FALSE</td></tr><tr><td>Offset</td><td>0</td></tr><tr><td>Mask</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>DataType</td><td>NATIVE</td></tr><tr><td>RepeatCount</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Data</td><td>0</td></tr><tr><td>id</td><td>1408</td></tr><tr><td>ModifierMode</td><td>INCR</td></tr></table></div>

# ttStreamFragOffset<br><font size="2">(ClassName:  RangeModifier)</font><h3><a id="ttStreamFragOffset.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamFragOffset');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamFragOffset"><table><tr><th>Property</th><th>Value</th></tr><tr><td>StepValue</td><td>1</td></tr><tr><td>Name</td><td>Modifier</td></tr><tr><td>OffsetReference</td><td>ip_1.fragOffset</td></tr><tr><td>RecycleCount</td><td>1</td></tr><tr><td>EnableStream</td><td>FALSE</td></tr><tr><td>Offset</td><td>0</td></tr><tr><td>Mask</td><td>8191</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>DataType</td><td>NATIVE</td></tr><tr><td>RepeatCount</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Data</td><td>0</td></tr><tr><td>id</td><td>1409</td></tr><tr><td>ModifierMode</td><td>INCR</td></tr></table></div>