
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

# ttBgpRouteGenParamsIpv4<br><font size="2">(ClassName:  BgpRouteGenParams)</font><h3><a id="ttBgpRouteGenParamsIpv4.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpRouteGenParamsIpv4');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpRouteGenParamsIpv4"><table><tr><th>Property</th><th>Value</th></tr><tr><td>TeUnRsvrBandwidth1Step</td><td>100000</td></tr><tr><td>TeUnRsvrBandwidth6Step</td><td>100000</td></tr><tr><td>SrCapRange</td><td>100</td></tr><tr><td>Ipv4AddrEnd</td><td>223.255.255.255</td></tr><tr><td>EnableLinkState</td><td>TRUE</td></tr><tr><td>SrAlgorithms</td><td>0</td></tr><tr><td>id</td><td>2142</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>IgpMetricEnabled</td><td>FALSE</td></tr><tr><td>AreaNumber</td><td>2</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Ipv4AddrStart</td><td>1.0.0.0</td></tr><tr><td>SystemIdStep</td><td>00:00:00:00:00:01</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>SrSidLabelType</td><td>LABEL</td></tr><tr><td>TeUnRsvrBandwidth4Step</td><td>100000</td></tr><tr><td>BackboneHeadendRoutersNumber</td><td>2</td></tr><tr><td>IncrementTeRsvrBandwidth</td><td>FALSE</td></tr><tr><td>TeUnRsvrBandwidth7Step</td><td>100000</td></tr><tr><td>IncrementIgpMetric</td><td>FALSE</td></tr><tr><td>Name</td><td>BgpRouteGenParams 1</td></tr><tr><td>SrCapValue</td><td>100</td></tr><tr><td>HeadendRoutersPerArea</td><td>2</td></tr><tr><td>IncrementSrWeight</td><td>FALSE</td></tr><tr><td>IgpProtocols</td><td>OSPFV2</td></tr><tr><td>TeRsvrBandwidthStep</td><td>10000</td></tr><tr><td>IfPrefixLength</td><td>24</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>SrAdjValue</td><td>9001</td></tr><tr><td>TeUnRsvrBandwidth5Step</td><td>100000</td></tr><tr><td>TeUnRsvrBandwidth3Step</td><td>100000</td></tr><tr><td>TeUnRsvrBandwidth2Step</td><td>100000</td></tr><tr><td>IncrementTeUnRsvrBandwidth</td><td>FALSE</td></tr><tr><td>SrIpv4PrefixSid</td><td>0</td></tr><tr><td>SystemIdStart</td><td>10:00:00:00:00:01</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>SrIpv4PrefixSidStep</td><td>1</td></tr><tr><td>IgpMetricType</td><td>OSPFV2</td></tr><tr><td>IncrementIpv4PrefixMetric</td><td>TRUE</td></tr><tr><td>TeUnRsvrBandwidth0Step</td><td>100000</td></tr><tr><td>SrEnabled</td><td>FALSE</td></tr></table></div>

# ttBgpRouteGenParamsIpv4.Ipv4RouteGenParams<br><font size="2">(ClassName:  Ipv4RouteGenParams)</font><h3><a id="ttBgpRouteGenParamsIpv4.Ipv4RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpRouteGenParamsIpv4.Ipv4RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpRouteGenParamsIpv4.Ipv4RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 1 0 1 1 1 1 1 1 2 3 2 6 3 1 6 8 55 1 1 1 1 1 1 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv4RouteGenParams 1</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>ALL</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>24</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2144</td></tr><tr><td>EmulatedRouters</td><td>NONE</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>TRUE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>223.255.255.255</td></tr><tr><td>IpAddrStart</td><td>1.0.0.0</td></tr><tr><td>PrefixLengthStart</td><td>24</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttBgpRouteGenParamsIpv6<br><font size="2">(ClassName:  BgpRouteGenParams)</font><h3><a id="ttBgpRouteGenParamsIpv6.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpRouteGenParamsIpv6');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpRouteGenParamsIpv6"><table><tr><th>Property</th><th>Value</th></tr><tr><td>TeUnRsvrBandwidth1Step</td><td>100000</td></tr><tr><td>TeUnRsvrBandwidth6Step</td><td>100000</td></tr><tr><td>SrCapRange</td><td>100</td></tr><tr><td>Ipv4AddrEnd</td><td>223.255.255.255</td></tr><tr><td>EnableLinkState</td><td>TRUE</td></tr><tr><td>SrAlgorithms</td><td>0</td></tr><tr><td>id</td><td>2143</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>IgpMetricEnabled</td><td>FALSE</td></tr><tr><td>AreaNumber</td><td>2</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Ipv4AddrStart</td><td>1.0.0.0</td></tr><tr><td>SystemIdStep</td><td>00:00:00:00:00:01</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>SrSidLabelType</td><td>LABEL</td></tr><tr><td>TeUnRsvrBandwidth4Step</td><td>100000</td></tr><tr><td>BackboneHeadendRoutersNumber</td><td>2</td></tr><tr><td>IncrementTeRsvrBandwidth</td><td>FALSE</td></tr><tr><td>TeUnRsvrBandwidth7Step</td><td>100000</td></tr><tr><td>IncrementIgpMetric</td><td>FALSE</td></tr><tr><td>Name</td><td>BgpRouteGenParams 2</td></tr><tr><td>SrCapValue</td><td>100</td></tr><tr><td>HeadendRoutersPerArea</td><td>2</td></tr><tr><td>IncrementSrWeight</td><td>FALSE</td></tr><tr><td>IgpProtocols</td><td>OSPFV2</td></tr><tr><td>TeRsvrBandwidthStep</td><td>10000</td></tr><tr><td>IfPrefixLength</td><td>24</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>SrAdjValue</td><td>9001</td></tr><tr><td>TeUnRsvrBandwidth5Step</td><td>100000</td></tr><tr><td>TeUnRsvrBandwidth3Step</td><td>100000</td></tr><tr><td>TeUnRsvrBandwidth2Step</td><td>100000</td></tr><tr><td>IncrementTeUnRsvrBandwidth</td><td>FALSE</td></tr><tr><td>SrIpv4PrefixSid</td><td>0</td></tr><tr><td>SystemIdStart</td><td>10:00:00:00:00:01</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>SrIpv4PrefixSidStep</td><td>1</td></tr><tr><td>IgpMetricType</td><td>OSPFV2</td></tr><tr><td>IncrementIpv4PrefixMetric</td><td>TRUE</td></tr><tr><td>TeUnRsvrBandwidth0Step</td><td>100000</td></tr><tr><td>SrEnabled</td><td>FALSE</td></tr></table></div>

# ttBgpRouteGenParamsIpv6.Ipv6RouteGenParams<br><font size="2">(ClassName:  Ipv6RouteGenParams)</font><h3><a id="ttBgpRouteGenParamsIpv6.Ipv6RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpRouteGenParamsIpv6.Ipv6RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpRouteGenParamsIpv6.Ipv6RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 2 2 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 2 3 1 1 1 1 1 2 6 50 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv6RouteGenParams 1</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>ALL</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>64</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2146</td></tr><tr><td>EmulatedRouters</td><td>NONE</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>TRUE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>3ffe::</td></tr><tr><td>IpAddrStart</td><td>2000::</td></tr><tr><td>PrefixLengthStart</td><td>64</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv2LsaGenParamsStub<br><font size="2">(ClassName:  Ospfv2LsaGenParams)</font><h3><a id="ttOspfv2LsaGenParamsStub.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv2LsaGenParamsStub');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv2LsaGenParamsStub"><table><tr><th>Property</th><th>Value</th></tr><tr><td>EnableTeRouterInformationTlv</td><td>FALSE</td></tr><tr><td>Name</td><td>Ospfv2LsaGenParams 1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>OspfSREnabled</td><td>FALSE</td></tr><tr><td>IfPrefixLength</td><td>24</td></tr><tr><td>AreaType</td><td>REGULAR</td></tr><tr><td>id</td><td>2215</td></tr><tr><td>IfIpAddrStart</td><td>1.0.0.1</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>NumberedPointToPointLinkEnabled</td><td>FALSE</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>IfEnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>IpAddrEnd</td><td>223.255.255.255</td></tr><tr><td>IpAddrStart</td><td>1.0.0.0</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv2LsaGenParamsStub.Ipv4RouteGenParams<br><font size="2">(ClassName:  Ipv4RouteGenParams)</font><h3><a id="ttOspfv2LsaGenParamsStub.Ipv4RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv2LsaGenParamsStub.Ipv4RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv2LsaGenParamsStub.Ipv4RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 1 0 1 1 1 1 1 1 2 3 2 6 3 1 6 8 55 1 1 1 1 1 1 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv4RouteGenParams 2</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>NONE</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>24</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2217</td></tr><tr><td>EmulatedRouters</td><td>ALL</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>223.255.255.255</td></tr><tr><td>IpAddrStart</td><td>1.0.0.0</td></tr><tr><td>PrefixLengthStart</td><td>24</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv2LsaGenParamsSummary<br><font size="2">(ClassName:  Ospfv2LsaGenParams)</font><h3><a id="ttOspfv2LsaGenParamsSummary.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv2LsaGenParamsSummary');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv2LsaGenParamsSummary"><table><tr><th>Property</th><th>Value</th></tr><tr><td>EnableTeRouterInformationTlv</td><td>FALSE</td></tr><tr><td>Name</td><td>Ospfv2LsaGenParams 2</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>OspfSREnabled</td><td>FALSE</td></tr><tr><td>IfPrefixLength</td><td>24</td></tr><tr><td>AreaType</td><td>REGULAR</td></tr><tr><td>id</td><td>2225</td></tr><tr><td>IfIpAddrStart</td><td>1.0.0.1</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>NumberedPointToPointLinkEnabled</td><td>FALSE</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>IfEnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>IpAddrEnd</td><td>223.255.255.255</td></tr><tr><td>IpAddrStart</td><td>1.0.0.0</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv2LsaGenParamsSummary.Ipv4RouteGenParams<br><font size="2">(ClassName:  Ipv4RouteGenParams)</font><h3><a id="ttOspfv2LsaGenParamsSummary.Ipv4RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv2LsaGenParamsSummary.Ipv4RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv2LsaGenParamsSummary.Ipv4RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 1 0 1 1 1 1 1 1 2 3 2 6 3 1 6 8 55 1 1 1 1 1 1 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv4RouteGenParams 3</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>NONE</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>24</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2219</td></tr><tr><td>EmulatedRouters</td><td>ALL</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>223.255.255.255</td></tr><tr><td>IpAddrStart</td><td>1.0.0.0</td></tr><tr><td>PrefixLengthStart</td><td>24</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv2LsaGenParamsExternal<br><font size="2">(ClassName:  Ospfv2LsaGenParams)</font><h3><a id="ttOspfv2LsaGenParamsExternal.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv2LsaGenParamsExternal');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv2LsaGenParamsExternal"><table><tr><th>Property</th><th>Value</th></tr><tr><td>EnableTeRouterInformationTlv</td><td>FALSE</td></tr><tr><td>Name</td><td>Ospfv2LsaGenParams 3</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>OspfSREnabled</td><td>FALSE</td></tr><tr><td>IfPrefixLength</td><td>24</td></tr><tr><td>AreaType</td><td>REGULAR</td></tr><tr><td>id</td><td>2235</td></tr><tr><td>IfIpAddrStart</td><td>1.0.0.1</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>NumberedPointToPointLinkEnabled</td><td>FALSE</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>IfEnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>IpAddrEnd</td><td>223.255.255.255</td></tr><tr><td>IpAddrStart</td><td>1.0.0.0</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv2LsaGenParamsExternal.Ipv4RouteGenParams<br><font size="2">(ClassName:  Ipv4RouteGenParams)</font><h3><a id="ttOspfv2LsaGenParamsExternal.Ipv4RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv2LsaGenParamsExternal.Ipv4RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv2LsaGenParamsExternal.Ipv4RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 1 0 1 1 1 1 1 1 2 3 2 6 3 1 6 8 55 1 1 1 1 1 1 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv4RouteGenParams 4</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>NONE</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>24</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2221</td></tr><tr><td>EmulatedRouters</td><td>ALL</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>223.255.255.255</td></tr><tr><td>IpAddrStart</td><td>1.0.0.0</td></tr><tr><td>PrefixLengthStart</td><td>24</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv3LsaGenParamsIntraArea<br><font size="2">(ClassName:  Ospfv3LsaGenParams)</font><h3><a id="ttOspfv3LsaGenParamsIntraArea.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LsaGenParamsIntraArea');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LsaGenParamsIntraArea"><table><tr><th>Property</th><th>Value</th></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>AreaType</td><td>REGULAR</td></tr><tr><td>Name</td><td>Ospfv3LsaGenParams 1</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>3ffe::</td></tr><tr><td>IpAddrStart</td><td>2000::</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>id</td><td>2969</td></tr><tr><td>EnableIpv6RouterIDAdvertisement</td><td>FALSE</td></tr></table></div>

# ttOspfv3LsaGenParamsIntraArea.Ipv6RouteGenParams<br><font size="2">(ClassName:  Ipv6RouteGenParams)</font><h3><a id="ttOspfv3LsaGenParamsIntraArea.Ipv6RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LsaGenParamsIntraArea.Ipv6RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LsaGenParamsIntraArea.Ipv6RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 2 2 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 2 3 1 1 1 1 1 2 6 50 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv6RouteGenParams 2</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>NONE</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>64</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2971</td></tr><tr><td>EmulatedRouters</td><td>ALL</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>3ffe::</td></tr><tr><td>IpAddrStart</td><td>2000::</td></tr><tr><td>PrefixLengthStart</td><td>64</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv3LsaGenParamsInterArea<br><font size="2">(ClassName:  Ospfv3LsaGenParams)</font><h3><a id="ttOspfv3LsaGenParamsInterArea.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LsaGenParamsInterArea');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LsaGenParamsInterArea"><table><tr><th>Property</th><th>Value</th></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>AreaType</td><td>REGULAR</td></tr><tr><td>Name</td><td>Ospfv3LsaGenParams 2</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>3ffe::</td></tr><tr><td>IpAddrStart</td><td>2000::</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>id</td><td>2980</td></tr><tr><td>EnableIpv6RouterIDAdvertisement</td><td>FALSE</td></tr></table></div>

# ttOspfv3LsaGenParamsInterArea.Ipv6RouteGenParams<br><font size="2">(ClassName:  Ipv6RouteGenParams)</font><h3><a id="ttOspfv3LsaGenParamsInterArea.Ipv6RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LsaGenParamsInterArea.Ipv6RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LsaGenParamsInterArea.Ipv6RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 2 2 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 2 3 1 1 1 1 1 2 6 50 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv6RouteGenParams 3</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>NONE</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>64</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2973</td></tr><tr><td>EmulatedRouters</td><td>ALL</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>3ffe::</td></tr><tr><td>IpAddrStart</td><td>2000::</td></tr><tr><td>PrefixLengthStart</td><td>64</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttOspfv3LsaGenParamsExternal<br><font size="2">(ClassName:  Ospfv3LsaGenParams)</font><h3><a id="ttOspfv3LsaGenParamsExternal.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LsaGenParamsExternal');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LsaGenParamsExternal"><table><tr><th>Property</th><th>Value</th></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>AreaType</td><td>REGULAR</td></tr><tr><td>Name</td><td>Ospfv3LsaGenParams 3</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>3ffe::</td></tr><tr><td>IpAddrStart</td><td>2000::</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>id</td><td>2981</td></tr><tr><td>EnableIpv6RouterIDAdvertisement</td><td>FALSE</td></tr></table></div>

# ttOspfv3LsaGenParamsExternal.Ipv6RouteGenParams<br><font size="2">(ClassName:  Ipv6RouteGenParams)</font><h3><a id="ttOspfv3LsaGenParamsExternal.Ipv6RouteGenParams.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LsaGenParamsExternal.Ipv6RouteGenParams');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LsaGenParamsExternal.Ipv6RouteGenParams"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthDist</td><td>0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 1 1 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 2 2 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 2 3 1 1 1 1 1 2 6 50 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 0 0 0 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 1</td></tr><tr><td>Count</td><td>10000</td></tr><tr><td>Name</td><td>Ipv6RouteGenParams 4</td></tr><tr><td>WeightRouteAssignment</td><td>BYROUTERS</td></tr><tr><td>SimulatedRouters</td><td>NONE</td></tr><tr><td>RoutesPerBlock</td><td>0</td></tr><tr><td>DuplicationPercentage</td><td>0</td></tr><tr><td>PrefixLengthEnd</td><td>64</td></tr><tr><td>IpAddrIncrement</td><td>1</td></tr><tr><td>PrefixLengthDistType</td><td>CUSTOM</td></tr><tr><td>id</td><td>2975</td></tr><tr><td>EmulatedRouters</td><td>ALL</td></tr><tr><td>UseIpAddrIncrement</td><td>FALSE</td></tr><tr><td>EnableIpAddrOverride</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IpAddrEnd</td><td>3ffe::</td></tr><tr><td>IpAddrStart</td><td>2000::</td></tr><tr><td>PrefixLengthStart</td><td>64</td></tr><tr><td>CreateMultipleRouteBlocks</td><td>FALSE</td></tr><tr><td>DisableRouteAggregation</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr></table></div>

# ttIsisLspGenParamsIpv4Internal<br><font size="2">(ClassName:  IsisLspGenParams)</font><h3><a id="ttIsisLspGenParamsIpv4Internal.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspGenParamsIpv4Internal');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspGenParamsIpv4Internal"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>IsisLspGenParams 1</td></tr><tr><td>UseSystemIdFromRouterId</td><td>FALSE</td></tr><tr><td>EnableRouterCapabilityTlv</td><td>FALSE</td></tr><tr><td>Ipv4AddrEnd</td><td>223.255.255.255</td></tr><tr><td>Ipv6RouterIdStart</td><td>2000::1</td></tr><tr><td>SREnabled</td><td>FALSE</td></tr><tr><td>id</td><td>3617</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>SystemIdStart</td><td>10:00:00:00:00:01</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>Ipv6AddrEnd</td><td>3ffe::</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Ipv4AddrStart</td><td>1.0.0.0</td></tr><tr><td>SystemIdStep</td><td>00:00:00:00:00:01</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>Ipv6RouterIdStep</td><td>::1</td></tr><tr><td>CreateSRTlvOnly</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Ipv6AddrStart</td><td>2000::</td></tr></table></div>

# ttIsisLspGenParamsIpv4External<br><font size="2">(ClassName:  IsisLspGenParams)</font><h3><a id="ttIsisLspGenParamsIpv4External.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspGenParamsIpv4External');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspGenParamsIpv4External"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>IsisLspGenParams 2</td></tr><tr><td>UseSystemIdFromRouterId</td><td>FALSE</td></tr><tr><td>EnableRouterCapabilityTlv</td><td>FALSE</td></tr><tr><td>Ipv4AddrEnd</td><td>223.255.255.255</td></tr><tr><td>Ipv6RouterIdStart</td><td>2000::1</td></tr><tr><td>SREnabled</td><td>FALSE</td></tr><tr><td>id</td><td>3627</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>SystemIdStart</td><td>10:00:00:00:00:01</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>Ipv6AddrEnd</td><td>3ffe::</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Ipv4AddrStart</td><td>1.0.0.0</td></tr><tr><td>SystemIdStep</td><td>00:00:00:00:00:01</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>Ipv6RouterIdStep</td><td>::1</td></tr><tr><td>CreateSRTlvOnly</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Ipv6AddrStart</td><td>2000::</td></tr></table></div>

# ttIsisLspGenParamsIpv6Internal<br><font size="2">(ClassName:  IsisLspGenParams)</font><h3><a id="ttIsisLspGenParamsIpv6Internal.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspGenParamsIpv6Internal');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspGenParamsIpv6Internal"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>IsisLspGenParams 3</td></tr><tr><td>UseSystemIdFromRouterId</td><td>FALSE</td></tr><tr><td>EnableRouterCapabilityTlv</td><td>FALSE</td></tr><tr><td>Ipv4AddrEnd</td><td>223.255.255.255</td></tr><tr><td>Ipv6RouterIdStart</td><td>2000::1</td></tr><tr><td>SREnabled</td><td>FALSE</td></tr><tr><td>id</td><td>3637</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>SystemIdStart</td><td>10:00:00:00:00:01</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>Ipv6AddrEnd</td><td>3ffe::</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Ipv4AddrStart</td><td>1.0.0.0</td></tr><tr><td>SystemIdStep</td><td>00:00:00:00:00:01</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>Ipv6RouterIdStep</td><td>::1</td></tr><tr><td>CreateSRTlvOnly</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Ipv6AddrStart</td><td>2000::</td></tr></table></div>

# ttIsisLspGenParamsIpv6External<br><font size="2">(ClassName:  IsisLspGenParams)</font><h3><a id="ttIsisLspGenParamsIpv6External.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspGenParamsIpv6External');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspGenParamsIpv6External"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>IsisLspGenParams 4</td></tr><tr><td>UseSystemIdFromRouterId</td><td>FALSE</td></tr><tr><td>EnableRouterCapabilityTlv</td><td>FALSE</td></tr><tr><td>Ipv4AddrEnd</td><td>223.255.255.255</td></tr><tr><td>Ipv6RouterIdStart</td><td>2000::1</td></tr><tr><td>SREnabled</td><td>FALSE</td></tr><tr><td>id</td><td>3647</td></tr><tr><td>RouterIdStep</td><td>0.0.0.1</td></tr><tr><td>SystemIdStart</td><td>10:00:00:00:00:01</td></tr><tr><td>EnableLoopbackAdvertisement</td><td>FALSE</td></tr><tr><td>TeEnabled</td><td>FALSE</td></tr><tr><td>Ipv6AddrEnd</td><td>3ffe::</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Ipv4AddrStart</td><td>1.0.0.0</td></tr><tr><td>SystemIdStep</td><td>00:00:00:00:00:01</td></tr><tr><td>RouterIdStart</td><td>1.0.0.1</td></tr><tr><td>Ipv6RouterIdStep</td><td>::1</td></tr><tr><td>CreateSRTlvOnly</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Ipv6AddrStart</td><td>2000::</td></tr></table></div>