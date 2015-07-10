
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

# ttEmulatedDevice<br><font size="2">(ClassName:  EmulatedDevice)</font><h3><a id="ttEmulatedDevice.h3link" href="JavaScript:;" onclick="toggle_visibility('ttEmulatedDevice');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttEmulatedDevice"><table><tr><th>Property</th><th>Value</th></tr><tr><td>RouterId</td><td>192.0.0.1</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>Name</td><td>Device 1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>EnablePingResponse</td><td>FALSE</td></tr><tr><td>DeviceCount</td><td>1</td></tr><tr><td>serializationBase</td><td>true</td></tr><tr><td>Ipv6RouterIdStep</td><td>::1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Ipv6RouterId</td><td>2000::1</td></tr><tr><td>id</td><td>4242</td></tr></table></div>

# ttVlanIf<br><font size="2">(ClassName:  VlanIf)</font><h3><a id="ttVlanIf.h3link" href="JavaScript:;" onclick="toggle_visibility('ttVlanIf');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttVlanIf"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>VLAN 1</td></tr><tr><td>Tpid</td><td>33024</td></tr><tr><td>IfRecycleCount</td><td>0</td></tr><tr><td>Priority</td><td>7</td></tr><tr><td>IsDirectlyConnected</td><td>TRUE</td></tr><tr><td>VlanId</td><td>100</td></tr><tr><td>IfCountPerLowerIf</td><td>1</td></tr><tr><td>IsRange</td><td>TRUE</td></tr><tr><td>id</td><td>3795</td></tr><tr><td>IdResolver</td><td>default</td></tr><tr><td>IdList</td><td></td></tr><tr><td>Cfi</td><td>0</td></tr><tr><td>IdStep</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IsLoopbackIf</td><td>FALSE</td></tr><tr><td>IsDecorated</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>IdRepeatCount</td><td>0</td></tr></table></div>

# ttIpv4If<br><font size="2">(ClassName:  Ipv4If)</font><h3><a id="ttIpv4If.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv4If');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv4If"><table><tr><th>Property</th><th>Value</th></tr><tr><td>SkipReserved</td><td>TRUE</td></tr><tr><td>GatewayMacResolver</td><td>default</td></tr><tr><td>IfCountPerLowerIf</td><td>1</td></tr><tr><td>GatewayRepeatCount</td><td>0</td></tr><tr><td>id</td><td>4243</td></tr><tr><td>GatewayList</td><td></td></tr><tr><td>ResolveGatewayMac</td><td>TRUE</td></tr><tr><td>NeedsAuthentication</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IsLoopbackIf</td><td>FALSE</td></tr><tr><td>IsDecorated</td><td>FALSE</td></tr><tr><td>GatewayMac</td><td>00:00:01:00:00:01</td></tr><tr><td>Tos</td><td>192</td></tr><tr><td>IsDirectlyConnected</td><td>TRUE</td></tr><tr><td>AddrList</td><td></td></tr><tr><td>AddrStep</td><td>0.0.0.1</td></tr><tr><td>Name</td><td>IPv4 28</td></tr><tr><td>IfRecycleCount</td><td>0</td></tr><tr><td>GatewayRecycleCount</td><td>0</td></tr><tr><td>UseIpAddrRangeSettingsForGateway</td><td>FALSE</td></tr><tr><td>AddrRepeatCount</td><td>0</td></tr><tr><td>IsRange</td><td>TRUE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>AddrResolver</td><td>default</td></tr><tr><td>UsePortDefaultIpv4Gateway</td><td>FALSE</td></tr><tr><td>TosType</td><td>TOS</td></tr><tr><td>AddrStepMask</td><td>255.255.255.255</td></tr><tr><td>Ttl</td><td>255</td></tr><tr><td>GatewayStep</td><td>0.0.0.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>Gateway</td><td>192.85.1.1</td></tr><tr><td>Address</td><td>192.85.1.3</td></tr></table></div>

# ttEthIIIf<br><font size="2">(ClassName:  EthIIIf)</font><h3><a id="ttEthIIIf.h3link" href="JavaScript:;" onclick="toggle_visibility('ttEthIIIf');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttEthIIIf"><table><tr><th>Property</th><th>Value</th></tr><tr><td>SourceMac</td><td>00:10:94:00:00:01</td></tr><tr><td>Name</td><td>EthernetII 28</td></tr><tr><td>IfRecycleCount</td><td>0</td></tr><tr><td>IsDirectlyConnected</td><td>TRUE</td></tr><tr><td>IfCountPerLowerIf</td><td>1</td></tr><tr><td>IsRange</td><td>TRUE</td></tr><tr><td>id</td><td>4244</td></tr><tr><td>IsDecorated</td><td>FALSE</td></tr><tr><td>SrcMacStepMask</td><td>00:00:ff:ff:ff:ff</td></tr><tr><td>SrcMacRepeatCount</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IsLoopbackIf</td><td>FALSE</td></tr><tr><td>SrcMacList</td><td></td></tr><tr><td>Authenticator</td><td>default</td></tr><tr><td>UseDefaultPhyMac</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>SrcMacStep</td><td>00:00:00:00:00:01</td></tr></table></div>

# ttGreIf<br><font size="2">(ClassName:  GreIf)</font><h3><a id="ttGreIf.h3link" href="JavaScript:;" onclick="toggle_visibility('ttGreIf');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttGreIf"><table><tr><th>Property</th><th>Value</th></tr><tr><td>TxFlowKeyField</td><td>0</td></tr><tr><td>IfCountPerLowerIf</td><td>1</td></tr><tr><td>IfRecycleCount</td><td>0</td></tr><tr><td>KeepAlivePeriod</td><td>10</td></tr><tr><td>SeqNumEnabled</td><td>FALSE</td></tr><tr><td>IsDirectlyConnected</td><td>TRUE</td></tr><tr><td>KeepAliveRetryCount</td><td>3</td></tr><tr><td>ChecksumEnabled</td><td>FALSE</td></tr><tr><td>IsRange</td><td>TRUE</td></tr><tr><td>OutFlowKeyFieldEnabled</td><td>FALSE</td></tr><tr><td>id</td><td>2951</td></tr><tr><td>Name</td><td>GRE 1</td></tr><tr><td>EnableKeepAlive</td><td>FALSE</td></tr><tr><td>RemoteTunnelEndPointV6Step</td><td>::1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IsLoopbackIf</td><td>FALSE</td></tr><tr><td>IsDecorated</td><td>FALSE</td></tr><tr><td>RemoteTunnelEndPointV4Step</td><td>0.0.0.1</td></tr><tr><td>InFlowKeyFieldEnabled</td><td>FALSE</td></tr><tr><td>RemoteTunnelEndPointV6</td><td>2000::2</td></tr><tr><td>RemoteTunnelEndPointV4</td><td>1.1.1.4</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>RxFlowKeyField</td><td>0</td></tr></table></div>