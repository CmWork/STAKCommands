
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

# ttBgpIpv4RouteConfig<br><font size="2">(ClassName:  BgpIpv4RouteConfig)</font><h3><a id="ttBgpIpv4RouteConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpIpv4RouteConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpIpv4RouteConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthCount</td><td>1</td></tr><tr><td>NextHop</td><td>null</td></tr><tr><td>OriginatorId</td><td>null</td></tr><tr><td>NextHopIncrementPerRouter</td><td>0.0.0.1</td></tr><tr><td>MedIncrementPerRouter</td><td>0</td></tr><tr><td>ExtendedCommunityPerBlockCount</td><td>1</td></tr><tr><td>LocalPreferenceIncrement</td><td>0</td></tr><tr><td>Med</td><td>null</td></tr><tr><td>NextHopIncrement</td><td>0.0.0.1</td></tr><tr><td>IsEditable</td><td>TRUE</td></tr><tr><td>ExtendedCommunity</td><td></td></tr><tr><td>AsPathIncrement</td><td></td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>4491</td></tr><tr><td>InsertRtImport</td><td>FALSE</td></tr><tr><td>CommunityPerBlockCount</td><td>1</td></tr><tr><td>LocalPreferenceIncrementPerRouter</td><td>0</td></tr><tr><td>MdtIpv4Addr</td><td>0.0.0.0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>AigpMetric</td><td>10</td></tr><tr><td>ClusterIdList</td><td></td></tr><tr><td>ExcludeAttributes</td><td>0</td></tr><tr><td>Name</td><td>BgpIpv4RouteConfig 1</td></tr><tr><td>AtomicAggregatePresent</td><td>FALSE</td></tr><tr><td>UseDeviceAddressAsNextHop</td><td>TRUE</td></tr><tr><td>MdtGroupAddr</td><td>0.0.0.0</td></tr><tr><td>CommunityIncrement</td><td></td></tr><tr><td>PrefixLengthIncrement</td><td>1</td></tr><tr><td>AigpPresent</td><td>FALSE</td></tr><tr><td>RouteSubAfi</td><td>UNICAST</td></tr><tr><td>AsPathPerBlockCount</td><td>1</td></tr><tr><td>Origin</td><td>IGP</td></tr><tr><td>AsPathSegmentType</td><td>SEQUENCE</td></tr><tr><td>NextHopCount</td><td>1</td></tr><tr><td>AggregatorAs</td><td></td></tr><tr><td>AigpMetricIncrement</td><td>0</td></tr><tr><td>AsPath</td><td>1</td></tr><tr><td>Community</td><td></td></tr><tr><td>MedIncrement</td><td>0</td></tr><tr><td>ExtendedCommunityIncrement</td><td></td></tr><tr><td>LocalPreference</td><td>10</td></tr><tr><td>AggregatorIp</td><td>null</td></tr><tr><td>RouteLabel</td><td>FIXED</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttBgpIpv4RouteConfig.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttBgpIpv4RouteConfig.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpIpv4RouteConfig.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpIpv4RouteConfig.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>BGP Route 192.0.1.0/24</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>4492</td></tr></table></div>

# ttBgpIpv6RouteConfig<br><font size="2">(ClassName:  BgpIpv6RouteConfig)</font><h3><a id="ttBgpIpv6RouteConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpIpv6RouteConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpIpv6RouteConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>PrefixLengthCount</td><td>1</td></tr><tr><td>NextHop</td><td>null</td></tr><tr><td>OriginatorId</td><td>null</td></tr><tr><td>NextHopIncrementPerRouter</td><td>::1</td></tr><tr><td>MedIncrementPerRouter</td><td>0</td></tr><tr><td>ExtendedCommunityPerBlockCount</td><td>1</td></tr><tr><td>LocalPreferenceIncrement</td><td>0</td></tr><tr><td>Name</td><td>BgpIpv6RouteConfig 2</td></tr><tr><td>Med</td><td>null</td></tr><tr><td>NextHopIncrement</td><td>::1</td></tr><tr><td>IsEditable</td><td>TRUE</td></tr><tr><td>ExtendedCommunity</td><td></td></tr><tr><td>AsPathIncrement</td><td></td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29119</td></tr><tr><td>InsertRtImport</td><td>FALSE</td></tr><tr><td>CommunityPerBlockCount</td><td>1</td></tr><tr><td>LocalPreferenceIncrementPerRouter</td><td>0</td></tr><tr><td>MdtIpv4Addr</td><td>0.0.0.0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>AigpMetric</td><td>10</td></tr><tr><td>ClusterIdList</td><td></td></tr><tr><td>RouteSubAfi</td><td>UNICAST</td></tr><tr><td>LocalNextHopIncrementPerRouter</td><td>::1</td></tr><tr><td>AtomicAggregatePresent</td><td>FALSE</td></tr><tr><td>ExcludeAttributes</td><td>0</td></tr><tr><td>UseDeviceAddressAsNextHop</td><td>TRUE</td></tr><tr><td>MdtGroupAddr</td><td>0.0.0.0</td></tr><tr><td>CommunityIncrement</td><td></td></tr><tr><td>PrefixLengthIncrement</td><td>1</td></tr><tr><td>AigpPresent</td><td>FALSE</td></tr><tr><td>AsPathPerBlockCount</td><td>1</td></tr><tr><td>Origin</td><td>IGP</td></tr><tr><td>AsPathSegmentType</td><td>SEQUENCE</td></tr><tr><td>NextHopCount</td><td>1</td></tr><tr><td>AggregatorAs</td><td></td></tr><tr><td>AigpMetricIncrement</td><td>0</td></tr><tr><td>AsPath</td><td>1</td></tr><tr><td>Community</td><td></td></tr><tr><td>MedIncrement</td><td>0</td></tr><tr><td>ExtendedCommunityIncrement</td><td></td></tr><tr><td>LocalPreference</td><td>10</td></tr><tr><td>AggregatorIp</td><td>null</td></tr><tr><td>RouteLabel</td><td>FIXED</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr><tr><td>LocalNextHop</td><td>null</td></tr></table></div>

# ttBgpIpv6RouteConfig.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttBgpIpv6RouteConfig.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpIpv6RouteConfig.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpIpv6RouteConfig.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv6 Network Block 18</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29120</td></tr></table></div>

# ttBgpEvpnMacAdvRouteConfig<br><font size="2">(ClassName:  BgpEvpnMacAdvRouteConfig)</font><h3><a id="ttBgpEvpnMacAdvRouteConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpEvpnMacAdvRouteConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpEvpnMacAdvRouteConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AsPath</td><td></td></tr><tr><td>RouteLabelAssignmentMode</td><td>FIXED</td></tr><tr><td>NextHop</td><td>null</td></tr><tr><td>OriginatorId</td><td>null</td></tr><tr><td>EviCount</td><td>1</td></tr><tr><td>IncludeMacMobility</td><td>FALSE</td></tr><tr><td>DataPlaneEncap</td><td>NONE</td></tr><tr><td>EncapLabelStep</td><td>0</td></tr><tr><td>ExtendedCommunityPerBlockCount</td><td>1</td></tr><tr><td>id</td><td>29123</td></tr><tr><td>EthernetTagId</td><td>0</td></tr><tr><td>SequenceNumber</td><td>0</td></tr><tr><td>ExtendedCommunity</td><td></td></tr><tr><td>EthernetSegmentId</td><td>0</td></tr><tr><td>AsPathIncrement</td><td></td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>EthernetSegmentType</td><td>TYPE0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>ClusterIdList</td><td></td></tr><tr><td>Name</td><td>BgpEvpnMacAdvRouteConfig 2</td></tr><tr><td>Med</td><td>null</td></tr><tr><td>AtomicAggregatePresent</td><td>FALSE</td></tr><tr><td>RouteTarget</td><td>100:1</td></tr><tr><td>Origin</td><td>IGP</td></tr><tr><td>AsPathSegmentType</td><td>SEQUENCE</td></tr><tr><td>IsStatic</td><td>FALSE</td></tr><tr><td>LocalPreferenceIncrement</td><td>0</td></tr><tr><td>AsPathPerBlockCount</td><td>1</td></tr><tr><td>RouteDistinguisherStep</td><td>0:1</td></tr><tr><td>RouteTargetStep</td><td>0:1</td></tr><tr><td>AggregatorAs</td><td></td></tr><tr><td>Community</td><td></td></tr><tr><td>EncapLabel</td><td>0</td></tr><tr><td>IsMPLSLabel2</td><td>FALSE</td></tr><tr><td>MedIncrement</td><td>0</td></tr><tr><td>ExtendedCommunityIncrement</td><td></td></tr><tr><td>LocalPreference</td><td>10</td></tr><tr><td>AggregatorIp</td><td>null</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr><tr><td>RouteDistinguisher</td><td>100.10.0.10:1</td></tr></table></div>

# ttBgpEvpnMacAdvRouteConfig.MacBlock<br><font size="2">(ClassName:  MacBlock)</font><h3><a id="ttBgpEvpnMacAdvRouteConfig.MacBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBgpEvpnMacAdvRouteConfig.MacBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBgpEvpnMacAdvRouteConfig.MacBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>BGP Route 00:00:00:00:00:01/48</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>StartMacList</td><td>00:00:00:00:00:01</td></tr><tr><td>Offset</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>PrefixLength</td><td>48</td></tr><tr><td>id</td><td>29124</td></tr></table></div>

# ttRouterLsaLink<br><font size="2">(ClassName:  RouterLsa)</font><h3><a id="ttRouterLsaLink.h3link" href="JavaScript:;" onclick="toggle_visibility('ttRouterLsaLink');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttRouterLsaLink"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Asbr</td><td>FALSE</td></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>Options</td><td>EBIT</td></tr><tr><td>Name</td><td>RouterLsa 1</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>Vl</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Abr</td><td>FALSE</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LinkStateId</td><td>0.0.0.0</td></tr><tr><td>id</td><td>4498</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttRouterLsaLink.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttRouterLsaLink.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttRouterLsaLink.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttRouterLsaLink.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>OSPFv2 Stub Network 192.0.1.0</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>4500</td></tr></table></div>

# ttSummaryLsaBlock<br><font size="2">(ClassName:  SummaryLsaBlock)</font><h3><a id="ttSummaryLsaBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttSummaryLsaBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttSummaryLsaBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>Name</td><td>SummaryLsaBlock 2</td></tr><tr><td>Tos</td><td>0</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Options</td><td>EBIT</td></tr><tr><td>Metric</td><td>1</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>id</td><td>29108</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr></table></div>

# ttSummaryLsaBlock.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttSummaryLsaBlock.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttSummaryLsaBlock.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttSummaryLsaBlock.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv4 Network Block 74</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>29109</td></tr></table></div>

# ttExternalLsaBlock<br><font size="2">(ClassName:  ExternalLsaBlock)</font><h3><a id="ttExternalLsaBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttExternalLsaBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttExternalLsaBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>Name</td><td>ExternalLsaBlock 2</td></tr><tr><td>Tos</td><td>0</td></tr><tr><td>ForwardingAddr</td><td>0.0.0.0</td></tr><tr><td>Type</td><td>EXT</td></tr><tr><td>id</td><td>29111</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Metric</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>MetricType</td><td>TYPE1</td></tr><tr><td>Options</td><td>EBIT</td></tr><tr><td>RouteTag</td><td>0</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttExternalLsaBlock.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttExternalLsaBlock.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttExternalLsaBlock.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttExternalLsaBlock.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv4 Network Block 75</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>29112</td></tr></table></div>

# ttOspfv3InterAreaPrefixLsaBlk<br><font size="2">(ClassName:  Ospfv3InterAreaPrefixLsaBlk)</font><h3><a id="ttOspfv3InterAreaPrefixLsaBlk.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3InterAreaPrefixLsaBlk');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3InterAreaPrefixLsaBlk"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>Name</td><td>Ospfv3InterAreaPrefixLsaBlk 2</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>PrefixOptions</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29095</td></tr><tr><td>RefLsType</td><td>0</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LinkStateId</td><td>0</td></tr><tr><td>Metric</td><td>1</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttOspfv3InterAreaPrefixLsaBlk.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttOspfv3InterAreaPrefixLsaBlk.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3InterAreaPrefixLsaBlk.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3InterAreaPrefixLsaBlk.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>OSPFv3 Inter-Area Prefix LSA 2000::1/64</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29096</td></tr></table></div>

# ttOspfv3AsExternalLsaBlock<br><font size="2">(ClassName:  Ospfv3AsExternalLsaBlock)</font><h3><a id="ttOspfv3AsExternalLsaBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3AsExternalLsaBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3AsExternalLsaBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>Name</td><td>Ospfv3AsExternalLsaBlock 2</td></tr><tr><td>AdminTag</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>ForwardingAddr</td><td>null</td></tr><tr><td>PrefixOptions</td><td>0</td></tr><tr><td>RefLsType</td><td>0</td></tr><tr><td>id</td><td>29098</td></tr><tr><td>LinkStateId</td><td>0</td></tr><tr><td>LsType</td><td>NONE</td></tr><tr><td>Metric</td><td>1</td></tr><tr><td>ExternalRouteTag</td><td>null</td></tr><tr><td>MetricType</td><td>FALSE</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>RefLinkStateId</td><td>0</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr></table></div>

# ttOspfv3AsExternalLsaBlock.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttOspfv3AsExternalLsaBlock.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3AsExternalLsaBlock.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3AsExternalLsaBlock.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>OSPFv3 AS External LSA 2000::1/64</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29099</td></tr></table></div>

# ttOspfv3NssaLsaBlock<br><font size="2">(ClassName:  Ospfv3NssaLsaBlock)</font><h3><a id="ttOspfv3NssaLsaBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3NssaLsaBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3NssaLsaBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>Name</td><td>Ospfv3NssaLsaBlock 2</td></tr><tr><td>AdminTag</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>ForwardingAddr</td><td>null</td></tr><tr><td>PrefixOptions</td><td>0</td></tr><tr><td>RefLsType</td><td>0</td></tr><tr><td>id</td><td>29100</td></tr><tr><td>LinkStateId</td><td>0</td></tr><tr><td>LsType</td><td>NONE</td></tr><tr><td>Metric</td><td>1</td></tr><tr><td>ExternalRouteTag</td><td>null</td></tr><tr><td>MetricType</td><td>FALSE</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>RefLinkStateId</td><td>0</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr></table></div>

# ttOspfv3NssaLsaBlock.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttOspfv3NssaLsaBlock.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3NssaLsaBlock.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3NssaLsaBlock.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>OSPFv3 NSSA Prefix LSA 2000::1/64</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29101</td></tr></table></div>

# ttOspfv3LinkLsaBlk<br><font size="2">(ClassName:  Ospfv3LinkLsaBlk)</font><h3><a id="ttOspfv3LinkLsaBlk.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LinkLsaBlk');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LinkLsaBlk"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>Name</td><td>Ospfv3LinkLsaBlk 2</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>PrefixOptions</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>Options</td><td>V6BIT|EBIT|RBIT</td></tr><tr><td>RouterPriority</td><td>0</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LinkStateId</td><td>0</td></tr><tr><td>id</td><td>29102</td></tr><tr><td>LinkLocalIfAddr</td><td>fe80::1</td></tr></table></div>

# ttOspfv3LinkLsaBlk.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttOspfv3LinkLsaBlk.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3LinkLsaBlk.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3LinkLsaBlk.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>OSPFv3 Link LSA 2000::1/64</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29103</td></tr></table></div>

# ttOspfv3IntraAreaPrefixLsaBlk<br><font size="2">(ClassName:  Ospfv3IntraAreaPrefixLsaBlk)</font><h3><a id="ttOspfv3IntraAreaPrefixLsaBlk.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3IntraAreaPrefixLsaBlk');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3IntraAreaPrefixLsaBlk"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AdvertisingRouterId</td><td>null</td></tr><tr><td>LinkStateId</td><td>0</td></tr><tr><td>PrefixMetric</td><td>1</td></tr><tr><td>Name</td><td>Ospfv3IntraAreaPrefixLsaBlk 2</td></tr><tr><td>RefAdvertisingRouterId</td><td>0.0.0.0</td></tr><tr><td>Age</td><td>0</td></tr><tr><td>PrefixOptions</td><td>0</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>RefLsType</td><td>0</td></tr><tr><td>SeqNum</td><td>2147483649</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>RefLinkStateId</td><td>0</td></tr><tr><td>id</td><td>29104</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr></table></div>

# ttOspfv3IntraAreaPrefixLsaBlk.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttOspfv3IntraAreaPrefixLsaBlk.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttOspfv3IntraAreaPrefixLsaBlk.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttOspfv3IntraAreaPrefixLsaBlk.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv6 Network Block 17</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29105</td></tr></table></div>

# ttIpv4PrefixLsp<br><font size="2">(ClassName:  Ipv4PrefixLsp)</font><h3><a id="ttIpv4PrefixLsp.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv4PrefixLsp');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv4PrefixLsp"><table><tr><th>Property</th><th>Value</th></tr><tr><td>FecType</td><td>LDP_FEC_TYPE_PREFIX</td></tr><tr><td>Name</td><td>Ipv4PrefixLsp 2</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29063</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttIpv4PrefixLsp.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttIpv4PrefixLsp.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv4PrefixLsp.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv4PrefixLsp.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv4 Network Block 70</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>29064</td></tr></table></div>

# ttIpv4IngressPrefixLsp<br><font size="2">(ClassName:  Ipv4IngressPrefixLsp)</font><h3><a id="ttIpv4IngressPrefixLsp.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv4IngressPrefixLsp');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv4IngressPrefixLsp"><table><tr><th>Property</th><th>Value</th></tr><tr><td>FecType</td><td>LDP_FEC_TYPE_PREFIX</td></tr><tr><td>Name</td><td>Ipv4IngressPrefixLsp 2</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29065</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttIpv4IngressPrefixLsp.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttIpv4IngressPrefixLsp.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv4IngressPrefixLsp.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv4IngressPrefixLsp.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv4 Network Block 71</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>29066</td></tr></table></div>

# ttIpv6PrefixLsp<br><font size="2">(ClassName:  Ipv6PrefixLsp)</font><h3><a id="ttIpv6PrefixLsp.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv6PrefixLsp');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv6PrefixLsp"><table><tr><th>Property</th><th>Value</th></tr><tr><td>FecType</td><td>LDP_FEC_TYPE_PREFIX</td></tr><tr><td>Name</td><td>Ipv6PrefixLsp 2</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29067</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttIpv6PrefixLsp.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttIpv6PrefixLsp.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv6PrefixLsp.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv6PrefixLsp.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv6 Network Block 11</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29068</td></tr></table></div>

# ttIpv6IngressPrefixLsp<br><font size="2">(ClassName:  Ipv6IngressPrefixLsp)</font><h3><a id="ttIpv6IngressPrefixLsp.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv6IngressPrefixLsp');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv6IngressPrefixLsp"><table><tr><th>Property</th><th>Value</th></tr><tr><td>FecType</td><td>LDP_FEC_TYPE_PREFIX</td></tr><tr><td>Name</td><td>Ipv6IngressPrefixLsp 2</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29069</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttIpv6IngressPrefixLsp.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttIpv6IngressPrefixLsp.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIpv6IngressPrefixLsp.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIpv6IngressPrefixLsp.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv6 Network Block 12</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>29070</td></tr></table></div>

# ttVcLsp<br><font size="2">(ClassName:  VcLsp)</font><h3><a id="ttVcLsp.h3link" href="JavaScript:;" onclick="toggle_visibility('ttVcLsp');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttVcLsp"><table><tr><th>Property</th><th>Value</th></tr><tr><td>IncludeStatusTlv</td><td>FALSE</td></tr><tr><td>UseCustomStatusCode</td><td>FALSE</td></tr><tr><td>VcIdCount</td><td>1</td></tr><tr><td>EnableGenericAssociatedLabel</td><td>FALSE</td></tr><tr><td>EnableBfd</td><td>FALSE</td></tr><tr><td>UseCustomEncap</td><td>FALSE</td></tr><tr><td>Encap</td><td>LDP_LSP_ENCAP_ETHERNET_VLAN</td></tr><tr><td>SignalRequestSwitchoverStatusBit</td><td>FALSE</td></tr><tr><td>id</td><td>29071</td></tr><tr><td>StatusCode</td><td>0</td></tr><tr><td>RequestedVlanIdIncrement</td><td>1</td></tr><tr><td>IncludeFlowLabelSubTlv</td><td>FALSE</td></tr><tr><td>ControlWordPreference</td><td>NOT_PREFERRED</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>VccvControlChannel</td><td>0</td></tr><tr><td>IfDescription</td><td></td></tr><tr><td>DstIpv4Address</td><td>127.0.0.1</td></tr><tr><td>StartVcId</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>VccvConnectivityVerification</td><td>0</td></tr><tr><td>IfMtu</td><td>1500</td></tr><tr><td>CustomStatusCode</td><td>0</td></tr><tr><td>Name</td><td>VcLsp 2</td></tr><tr><td>BfdMessageFormat</td><td>BFD_CC</td></tr><tr><td>RequestedVlanId</td><td>null</td></tr><tr><td>BfdMyDiscriminator</td><td>null</td></tr><tr><td>VcIdIncrement</td><td>1</td></tr><tr><td>RedundantSetRole</td><td>REDUNDANT_SET_ROLE_NONE</td></tr><tr><td>CustomEncap</td><td>4</td></tr><tr><td>FlowLabelSubTlvTRBit</td><td>0</td></tr><tr><td>GroupId</td><td>0</td></tr><tr><td>RouteCategory</td><td>UNDEFINED</td></tr></table></div>

# ttVcLsp.MacBlock<br><font size="2">(ClassName:  MacBlock)</font><h3><a id="ttVcLsp.MacBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttVcLsp.MacBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttVcLsp.MacBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>MAC Address Block 3</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>StartMacList</td><td>00:00:00:00:00:01</td></tr><tr><td>Offset</td><td>0</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>PrefixLength</td><td>null</td></tr><tr><td>id</td><td>29072</td></tr></table></div>

# ttIsisLspConfig1<br><font size="2">(ClassName:  IsisLspConfig)</font><h3><a id="ttIsisLspConfig1.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig1');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig1"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Ipv6TeRouterId</td><td>null</td></tr><tr><td>Ol</td><td>FALSE</td></tr><tr><td>Name</td><td>IsisLspConfig 1</td></tr><tr><td>PduType</td><td>STANDARD</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Att</td><td>FALSE</td></tr><tr><td>SystemId</td><td>null</td></tr><tr><td>TeRouterId</td><td>null</td></tr><tr><td>id</td><td>4513</td></tr><tr><td>NeighborPseudonodeId</td><td>0</td></tr><tr><td>SeqNum</td><td>1</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Lifetime</td><td>1200</td></tr></table></div>

# ttIsisLspConfig1.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttIsisLspConfig1.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig1.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig1.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>ISIS Route 192.0.1.0/24</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>4515</td></tr></table></div>

# ttIsisLspConfig2<br><font size="2">(ClassName:  IsisLspConfig)</font><h3><a id="ttIsisLspConfig2.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig2');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig2"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Ipv6TeRouterId</td><td>null</td></tr><tr><td>Ol</td><td>FALSE</td></tr><tr><td>Name</td><td>IsisLspConfig 1</td></tr><tr><td>PduType</td><td>STANDARD</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Att</td><td>FALSE</td></tr><tr><td>SystemId</td><td>null</td></tr><tr><td>TeRouterId</td><td>null</td></tr><tr><td>id</td><td>4513</td></tr><tr><td>NeighborPseudonodeId</td><td>0</td></tr><tr><td>SeqNum</td><td>1</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Lifetime</td><td>1200</td></tr></table></div>

# ttIsisLspConfig2.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttIsisLspConfig2.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig2.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig2.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv4 Network Block 72</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>29082</td></tr></table></div>

# ttIsisIpv4EroSubTlv<br><font size="2">(ClassName:  IsisIpv4EroSubTlv)</font><h3><a id="ttIsisIpv4EroSubTlv.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisIpv4EroSubTlv');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisIpv4EroSubTlv"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Flags</td><td>LBIT</td></tr><tr><td>Name</td><td>IsisIpv4EroSubTlv 1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29091</td></tr><tr><td>IlObjState</td><td>0</td></tr></table></div>

# ttIsisIpv4EroSubTlv.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttIsisIpv4EroSubTlv.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisIpv4EroSubTlv.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisIpv4EroSubTlv.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv4 Network Block 73</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>29092</td></tr></table></div>

# ttBfdIpv4ControlPlaneIndependentSession<br><font size="2">(ClassName:  BfdIpv4ControlPlaneIndependentSession)</font><h3><a id="ttBfdIpv4ControlPlaneIndependentSession.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBfdIpv4ControlPlaneIndependentSession');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBfdIpv4ControlPlaneIndependentSession"><table><tr><th>Property</th><th>Value</th></tr><tr><td>MyDiscriminatorIncrement</td><td>1</td></tr><tr><td>EnableMyDiscriminator</td><td>FALSE</td></tr><tr><td>Name</td><td>BfdIpv4ControlPlaneIndependentSession 1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>MyDiscriminator</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29057</td></tr></table></div>

# ttBfdIpv4ControlPlaneIndependentSession.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttBfdIpv4ControlPlaneIndependentSession.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBfdIpv4ControlPlaneIndependentSession.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBfdIpv4ControlPlaneIndependentSession.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>BFD BFD IPv4 Session 192.0.1.0/32</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>32</td></tr><tr><td>id</td><td>29058</td></tr></table></div>

# ttBfdIpv6ControlPlaneIndependentSession<br><font size="2">(ClassName:  BfdIpv6ControlPlaneIndependentSession)</font><h3><a id="ttBfdIpv6ControlPlaneIndependentSession.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBfdIpv6ControlPlaneIndependentSession');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBfdIpv6ControlPlaneIndependentSession"><table><tr><th>Property</th><th>Value</th></tr><tr><td>MyDiscriminatorIncrement</td><td>1</td></tr><tr><td>EnableMyDiscriminator</td><td>FALSE</td></tr><tr><td>Name</td><td>BfdIpv6ControlPlaneIndependentSession 1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>MyDiscriminator</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>id</td><td>29059</td></tr></table></div>

# ttBfdIpv6ControlPlaneIndependentSession.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttBfdIpv6ControlPlaneIndependentSession.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttBfdIpv6ControlPlaneIndependentSession.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttBfdIpv6ControlPlaneIndependentSession.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>BFD BFD IPv6 Session 2000::1/128</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>128</td></tr><tr><td>id</td><td>29060</td></tr></table></div>

# ttIsisLspConfig4<br><font size="2">(ClassName:  IsisLspConfig)</font><h3><a id="ttIsisLspConfig4.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig4');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig4"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Ipv6TeRouterId</td><td>null</td></tr><tr><td>Ol</td><td>FALSE</td></tr><tr><td>Name</td><td>IsisLspConfig 40</td></tr><tr><td>PduType</td><td>STANDARD</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Att</td><td>FALSE</td></tr><tr><td>SystemId</td><td>null</td></tr><tr><td>TeRouterId</td><td>null</td></tr><tr><td>id</td><td>33624</td></tr><tr><td>NeighborPseudonodeId</td><td>0</td></tr><tr><td>SeqNum</td><td>1</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Lifetime</td><td>1200</td></tr></table></div>

# ttIsisLspConfig4.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttIsisLspConfig4.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig4.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig4.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv4 Network Block 84</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>24</td></tr><tr><td>id</td><td>33626</td></tr></table></div>

# ttIsisLspConfig6<br><font size="2">(ClassName:  IsisLspConfig)</font><h3><a id="ttIsisLspConfig6.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig6');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig6"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Ipv6TeRouterId</td><td>null</td></tr><tr><td>Ol</td><td>FALSE</td></tr><tr><td>Name</td><td>IsisLspConfig 41</td></tr><tr><td>PduType</td><td>STANDARD</td></tr><tr><td>Level</td><td>LEVEL2</td></tr><tr><td>Att</td><td>FALSE</td></tr><tr><td>SystemId</td><td>null</td></tr><tr><td>TeRouterId</td><td>null</td></tr><tr><td>id</td><td>33627</td></tr><tr><td>NeighborPseudonodeId</td><td>0</td></tr><tr><td>SeqNum</td><td>1</td></tr><tr><td>HostName</td><td>Spirent-1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>CheckSum</td><td>GOOD</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>Lifetime</td><td>1200</td></tr></table></div>

# ttIsisLspConfig6.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttIsisLspConfig6.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttIsisLspConfig6.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttIsisLspConfig6.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>Ipv6 Network Block 27</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>64</td></tr><tr><td>id</td><td>33629</td></tr></table></div>

# ttAllRoutes.Ipv4NetworkBlock<br><font size="2">(ClassName:  Ipv4NetworkBlock)</font><h3><a id="ttAllRoutes.Ipv4NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttAllRoutes.Ipv4NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttAllRoutes.Ipv4NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>BFD BFD IPv4 Session 192.0.1.0/32</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>192.0.1.0</td></tr><tr><td>PrefixLength</td><td>32</td></tr><tr><td>id</td><td>29058</td></tr></table></div>

# ttAllRoutes.Ipv6NetworkBlock<br><font size="2">(ClassName:  Ipv6NetworkBlock)</font><h3><a id="ttAllRoutes.Ipv6NetworkBlock.h3link" href="JavaScript:;" onclick="toggle_visibility('ttAllRoutes.Ipv6NetworkBlock');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttAllRoutes.Ipv6NetworkBlock"><table><tr><th>Property</th><th>Value</th></tr><tr><td>Name</td><td>BFD BFD IPv6 Session 2000::1/128</td></tr><tr><td>NetworkCount</td><td>1</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AddrIncrement</td><td>1</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>StartIpList</td><td>2000::1</td></tr><tr><td>PrefixLength</td><td>128</td></tr><tr><td>id</td><td>29060</td></tr></table></div>