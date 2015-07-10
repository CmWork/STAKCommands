
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

# ttStreamBlock<br><font size="2">(ClassName:  StreamBlock)</font><h3><a id="ttStreamBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AutoSelectTunnel</td><td>FALSE</td></tr><tr><td>EnableTxPortSendingTrafficToSelf</td><td>FALSE</td></tr><tr><td>EnableBackBoneTrafficSendToSelf</td><td>TRUE</td></tr><tr><td>EnableBidirectionalTraffic</td><td>FALSE</td></tr><tr><td>serializationBase</td><td>true</td></tr><tr><td>AdvancedInterleavingGroup</td><td>0</td></tr><tr><td>TrafficPattern</td><td>PAIR</td></tr><tr><td>id</td><td>2111</td></tr><tr><td>InsertSig</td><td>TRUE</td></tr><tr><td>StepFrameLength</td><td>1</td></tr><tr><td>IsControlledByGenerator</td><td>TRUE</td></tr><tr><td>ConstantFillPattern</td><td>0</td></tr><tr><td>AllowInvalidHeaders</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>ControlledBy</td><td>generator</td></tr><tr><td>ShowAllHeaders</td><td>FALSE</td></tr><tr><td>ByPassSimpleIpSubnetChecking</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>EndpointMapping</td><td>ONE_TO_ONE</td></tr><tr><td>Name</td><td>AF11</td></tr><tr><td>EnableHighSpeedResultAnalysis</td><td>TRUE</td></tr><tr><td>Filter</td><td></td></tr><tr><td>FixedFrameLength</td><td>128</td></tr><tr><td>MinFrameLength</td><td>128</td></tr><tr><td>EqualRxPortDistribution</td><td>TRUE</td></tr><tr><td>EnableResolveDestMacAddress</td><td>TRUE</td></tr><tr><td>MaxFrameLength</td><td>256</td></tr><tr><td>FrameConfig</td><td><frame><config><pdus><pdu name="eth1" pdu="ethernet:EthernetII"><vlans name="anon_3911"><Vlan name="Vlan"><pri>000</pri></Vlan><Vlan name="Vlan_1"><pri>000</pri></Vlan></vlans></pdu><pdu name="ip_1" pdu="ipv4:IPv4"><totalLength>20</totalLength><checksum>14936</checksum><tosDiffserv name="anon_3915"><diffServ name="anon_3916"><dscpHigh>1</dscpHigh><dscpLow>2</dscpLow><reserved>00</reserved></diffServ></tosDiffserv></pdu><pdu name="proto1" pdu="udp:Udp"><length>0</length></pdu></pdus></config></frame></td></tr><tr><td>EnableStreamOnlyGeneration</td><td>TRUE</td></tr><tr><td>EnableControlPlane</td><td>FALSE</td></tr><tr><td>FrameLengthMode</td><td>FIXED</td></tr><tr><td>DisableTunnelBinding</td><td>FALSE</td></tr><tr><td>FillType</td><td>CONSTANT</td></tr><tr><td>EnableFcsErrorInsertion</td><td>FALSE</td></tr></table></div>

# ttStreamBlockLoadProfile<br><font size="2">(ClassName:  StreamBlockLoadProfile)</font><h3><a id="ttStreamBlockLoadProfile.h3link" href="JavaScript:;" onclick="toggle_visibility('ttStreamBlockLoadProfile');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttStreamBlockLoadProfile"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Load</td><td>10</td></tr><tr><td>BurstSize</td><td>1</td></tr><tr><td>Name</td><td>StreamBlockLoadProfile 1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>InterFrameGap</td><td>12</td></tr><tr><td>LoadUnit</td><td>PERCENT_LINE_RATE</td></tr><tr><td>Priority</td><td>0</td></tr><tr><td>serializationBase</td><td>true</td></tr><tr><td>StartDelay</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>InterFrameGapUnit</td><td>BYTES</td></tr><tr><td>id</td><td>2112</td></tr></table></div>