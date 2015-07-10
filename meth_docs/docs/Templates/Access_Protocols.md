
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

# ttDhcpv4BlockConfig<br><font size="2">(ClassName:  Dhcpv4BlockConfig)</font><h3><a id="ttDhcpv4BlockConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttDhcpv4BlockConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttDhcpv4BlockConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>RemoteId</td><td>remoteId_@p-@b-@s</td></tr><tr><td>VPNId</td><td>spirent</td></tr><tr><td>CircuitId</td><td>circuitId_@p</td></tr><tr><td>DefaultHostAddrPrefixLength</td><td>24</td></tr><tr><td>RelayServerIpv4Addr</td><td>0.0.0.0</td></tr><tr><td>RelayAgentIpv4AddrStep</td><td>0.0.0.1</td></tr><tr><td>UseBroadcastFlag</td><td>TRUE</td></tr><tr><td>RelayClientMacAddrStart</td><td>00:10:01:00:00:01</td></tr><tr><td>id</td><td>2094</td></tr><tr><td>EnableRelayLinkSelection</td><td>FALSE</td></tr><tr><td>EnableRouterOption</td><td>FALSE</td></tr><tr><td>RelayClientMacAddrMask</td><td>00:00:00:ff:ff:ff</td></tr><tr><td>HostName</td><td>client_@p-@b-@s</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>RelayLinkSelection</td><td>192.85.1.1</td></tr><tr><td>OptionList</td><td>1 6 15 33 44</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>RelayServerIpv4AddrStep</td><td>0.0.0.1</td></tr><tr><td>EnableRelayServerIdOverride</td><td>FALSE</td></tr><tr><td>EnableRemoteId</td><td>FALSE</td></tr><tr><td>RelayServerIdOverride</td><td>192.85.1.1</td></tr><tr><td>RetryAttempts</td><td>4</td></tr><tr><td>ExportAddrToLinkedClients</td><td>FALSE</td></tr><tr><td>RelayPoolIpv4AddrStep</td><td>0.0.1.0</td></tr><tr><td>EnableAutoRetry</td><td>FALSE</td></tr><tr><td>EnableRelayVPNID</td><td>FALSE</td></tr><tr><td>RelayPoolIpv4Addr</td><td>0.0.0.0</td></tr><tr><td>RelayClientMacAddrStep</td><td>00:00:00:00:00:01</td></tr><tr><td>ClientRelayAgent</td><td>FALSE</td></tr><tr><td>UseClientMacAddrForDataplane</td><td>FALSE</td></tr><tr><td>VPNType</td><td>NVT_ASCII</td></tr><tr><td>RelayAgentIpv4AddrMask</td><td>255.255.0.0</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>EnableCircuitId</td><td>FALSE</td></tr><tr><td>EnableArpServerId</td><td>FALSE</td></tr><tr><td>EnableRelayAgent</td><td>FALSE</td></tr><tr><td>RelayAgentIpv4Addr</td><td>0.0.0.0</td></tr><tr><td>Name</td><td>DHCP 1</td></tr></table></div>

# ttPppoeClientBlockConfig<br><font size="2">(ClassName:  PppoeClientBlockConfig)</font><h3><a id="ttPppoeClientBlockConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttPppoeClientBlockConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttPppoeClientBlockConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>LcpTermRequestTimeout</td><td>3</td></tr><tr><td>MaxPapRequestAttempts</td><td>10</td></tr><tr><td>EnableAutoFillIpv6</td><td>TRUE</td></tr><tr><td>RelayAgentType</td><td>RFC_2516</td></tr><tr><td>PapRequestTimeout</td><td>3</td></tr><tr><td>CircuitId</td><td>circuit @s</td></tr><tr><td>AutoRetryCount</td><td>65535</td></tr><tr><td>EnableNcpTermination</td><td>FALSE</td></tr><tr><td>RelayAgentMacAddr</td><td>00:00:00:00:00:00</td></tr><tr><td>EnableEchoRequest</td><td>FALSE</td></tr><tr><td>MaxNaks</td><td>5</td></tr><tr><td>id</td><td>2102</td></tr><tr><td>Username</td><td>spirent</td></tr><tr><td>MaxEchoRequestAttempts</td><td>0</td></tr><tr><td>MaxPayloadBytes</td><td>1500</td></tr><tr><td>PadrTimeout</td><td>3</td></tr><tr><td>RelayAgentMacAddrStep</td><td>00:00:00:00:00:01</td></tr><tr><td>ChapChalRequestTimeout</td><td>3</td></tr><tr><td>LcpTermRequestMaxAttempts</td><td>10</td></tr><tr><td>EnableMaxPayloadTag</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IncludeTxChapId</td><td>TRUE</td></tr><tr><td>EnableMpls</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>NcpConfigRequestTimeout</td><td>3</td></tr><tr><td>Password</td><td>spirent</td></tr><tr><td>LcpConfigRequestMaxAttempts</td><td>10</td></tr><tr><td>MruSize</td><td>1492</td></tr><tr><td>PadiMaxAttempts</td><td>10</td></tr><tr><td>Name</td><td>PppoeClientBlockConfig 1</td></tr><tr><td>LcpConfigRequestTimeout</td><td>3</td></tr><tr><td>AutoCalculateMru</td><td>FALSE</td></tr><tr><td>EchoRequestGenFreq</td><td>10</td></tr><tr><td>LcpDelay</td><td>0</td></tr><tr><td>ServiceName</td><td></td></tr><tr><td>TotalClients</td><td>65535</td></tr><tr><td>ChapAckTimeout</td><td>3</td></tr><tr><td>EnableOsi</td><td>FALSE</td></tr><tr><td>MaxChapRequestReplyAttempts</td><td>10</td></tr><tr><td>EnableAutoRetry</td><td>FALSE</td></tr><tr><td>PadiTimeout</td><td>3</td></tr><tr><td>RAMOFlag</td><td>NODHCP</td></tr><tr><td>IncludeRelayAgentInPadi</td><td>TRUE</td></tr><tr><td>Protocol</td><td>UNDEFINED</td></tr><tr><td>Authentication</td><td>NONE</td></tr><tr><td>EnableMruNegotiation</td><td>TRUE</td></tr><tr><td>RelayAgentMacAddrMask</td><td>ff:ff:ff:ff:ff:ff</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>RemoteOrSessionId</td><td>remote @m-@p-@b</td></tr><tr><td>EnableRelayAgent</td><td>FALSE</td></tr><tr><td>EnableMagicNum</td><td>TRUE</td></tr><tr><td>IncludeRelayAgentInPadr</td><td>TRUE</td></tr><tr><td>IpcpEncap</td><td>IPV4</td></tr><tr><td>PadrMaxAttempts</td><td>10</td></tr><tr><td>NcpConfigRequestMaxAttempts</td><td>10</td></tr></table></div>

# ttL2tpv2BlockConfig<br><font size="2">(ClassName:  L2tpv2BlockConfig)</font><h3><a id="ttL2tpv2BlockConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttL2tpv2BlockConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttL2tpv2BlockConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>HelloTimeout</td><td>60</td></tr><tr><td>SessionStartingId</td><td>1</td></tr><tr><td>RxWindowSize</td><td>4</td></tr><tr><td>EnableHello</td><td>FALSE</td></tr><tr><td>UseGatewayAsRemoteIpv4Addr</td><td>TRUE</td></tr><tr><td>LcpProxyMode</td><td>NONE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>UdpSrcPort</td><td>1701</td></tr><tr><td>SessionsPerTunnelCount</td><td>1</td></tr><tr><td>AutoRetryCount</td><td>1</td></tr><tr><td>ForceLcpRenegotiation</td><td>FALSE</td></tr><tr><td>BearerCapabilities</td><td>ANALOG</td></tr><tr><td>TxConnectRate</td><td>56000</td></tr><tr><td>FrameType</td><td>SYNC</td></tr><tr><td>Name</td><td>L2tpv2BlockConfig 1</td></tr><tr><td>TunnelCount</td><td>1</td></tr><tr><td>TunnelStartingId</td><td>1</td></tr><tr><td>UseGatewayAsRemoteIpv6Addr</td><td>TRUE</td></tr><tr><td>RxTunnelPassword</td><td>spirent</td></tr><tr><td>BearerType</td><td>ANALOG</td></tr><tr><td>HostName</td><td>server.spirent.com</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>id</td><td>2104</td></tr><tr><td>EnableAutoRetry</td><td>FALSE</td></tr><tr><td>EnableDutAuthentication</td><td>TRUE</td></tr><tr><td>HiddenAvps</td><td></td></tr><tr><td>TxTunnelPassword</td><td>spirent</td></tr><tr><td>RetryTimeout</td><td>1</td></tr><tr><td>FrameCapabilities</td><td>SYNC</td></tr><tr><td>IpEncap</td><td>IPV4</td></tr></table></div>

# ttDhcpv6BlockConfig<br><font size="2">(ClassName:  Dhcpv6BlockConfig)</font><h3><a id="ttDhcpv6BlockConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttDhcpv6BlockConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttDhcpv6BlockConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AuthKeySpecMethod</td><td>LIST</td></tr><tr><td>AuthKeyCount</td><td>1</td></tr><tr><td>ControlPlanePrefix</td><td>LINKLOCAL</td></tr><tr><td>DuidStart</td><td>0001</td></tr><tr><td>ClientMacAddrMask</td><td>00:00:00:ff:ff:ff</td></tr><tr><td>UseRelayAgentMacAddrForDataplane</td><td>TRUE</td></tr><tr><td>RequestedAddrStart</td><td>::</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>T1Timer</td><td>302400</td></tr><tr><td>EnableLdra</td><td>FALSE</td></tr><tr><td>DuidType</td><td>LLT</td></tr><tr><td>PrefixStart</td><td>::</td></tr><tr><td>id</td><td>2110</td></tr><tr><td>DstAddrType</td><td>ALL_DHCP_RELAY_AGENTS_AND_SERVERS</td></tr><tr><td>PreferredLifetime</td><td>604800</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AuthKeyValuePattern</td><td></td></tr><tr><td>Dhcpv6ClientMode</td><td>DHCPV6</td></tr><tr><td>DhcpRealm</td><td>spirent.com</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>EnableAuth</td><td>FALSE</td></tr><tr><td>EnableRenew</td><td>TRUE</td></tr><tr><td>AuthKeyValueType</td><td>ASCII</td></tr><tr><td>RelayServerIpv6AddrStep</td><td>::</td></tr><tr><td>AddrRequestType</td><td>NA</td></tr><tr><td>Name</td><td>Dhcpv6BlockConfig 1</td></tr><tr><td>ClientMacAddrStep</td><td>00:00:00:00:00:01</td></tr><tr><td>EnableRelayAgent</td><td>FALSE</td></tr><tr><td>EnableReconfigAccept</td><td>FALSE</td></tr><tr><td>EnableDad</td><td>TRUE</td></tr><tr><td>AuthProtocol</td><td>DELAYED_AUTH</td></tr><tr><td>HgMacStep</td><td>00:00:00:00:00:01</td></tr><tr><td>DuidEnterprise</td><td>3456</td></tr><tr><td>DuidStep</td><td>1</td></tr><tr><td>DadTimeout</td><td>1</td></tr><tr><td>AuthKeyIdStart</td><td>1</td></tr><tr><td>EnableRebind</td><td>FALSE</td></tr><tr><td>UseHgMac</td><td>FALSE</td></tr><tr><td>DadTransmits</td><td>1</td></tr><tr><td>ExportAddrToLinkedClients</td><td>FALSE</td></tr><tr><td>HgMacStart</td><td>00:10:01:00:00:01</td></tr><tr><td>RelayServerIpv6Addr</td><td>null</td></tr><tr><td>DuidValue</td><td>1</td></tr><tr><td>ValidLifetime</td><td>2592000</td></tr><tr><td>RapidCommitMode</td><td>DISABLE</td></tr><tr><td>AuthKeyIdStep</td><td>1</td></tr><tr><td>PrefixLength</td><td>0</td></tr><tr><td>T2Timer</td><td>483840</td></tr><tr><td>ClientMacAddrStart</td><td>00:10:01:00:00:01</td></tr></table></div>

# ttDhcpv6PdBlockConfig<br><font size="2">(ClassName:  Dhcpv6PdBlockConfig)</font><h3><a id="ttDhcpv6PdBlockConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttDhcpv6PdBlockConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttDhcpv6PdBlockConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>ControlPlanePrefix</td><td>LINKLOCAL</td></tr><tr><td>DuidStart</td><td>0001</td></tr><tr><td>ClientMacAddrMask</td><td>00:00:00:ff:ff:ff</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>EnableLdra</td><td>FALSE</td></tr><tr><td>DuidType</td><td>LLT</td></tr><tr><td>PrefixStart</td><td>::</td></tr><tr><td>id</td><td>2112</td></tr><tr><td>DstAddrType</td><td>ALL_DHCP_RELAY_AGENTS_AND_SERVERS</td></tr><tr><td>PreferredLifetime</td><td>604800</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>RelayServerIpv6Addr</td><td>null</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>UseRelayAgentMacAddrForDataplane</td><td>TRUE</td></tr><tr><td>EnableRenew</td><td>TRUE</td></tr><tr><td>RelayServerIpv6AddrStep</td><td>::</td></tr><tr><td>T1Timer</td><td>302400</td></tr><tr><td>Name</td><td>Dhcpv6PdBlockConfig 2</td></tr><tr><td>ClientMacAddrStep</td><td>00:00:00:00:00:01</td></tr><tr><td>EnableRelayAgent</td><td>FALSE</td></tr><tr><td>EnableReconfigAccept</td><td>FALSE</td></tr><tr><td>HgMacStep</td><td>00:00:00:00:00:01</td></tr><tr><td>DuidEnterprise</td><td>3456</td></tr><tr><td>DuidStep</td><td>1</td></tr><tr><td>EnableRebind</td><td>FALSE</td></tr><tr><td>UseHgMac</td><td>TRUE</td></tr><tr><td>ExportAddrToLinkedClients</td><td>FALSE</td></tr><tr><td>HgMacStart</td><td>00:10:01:00:00:01</td></tr><tr><td>ClientMacAddrStart</td><td>00:10:01:00:00:01</td></tr><tr><td>DuidValue</td><td>1</td></tr><tr><td>ValidLifetime</td><td>2592000</td></tr><tr><td>RapidCommitMode</td><td>DISABLE</td></tr><tr><td>PrefixLength</td><td>0</td></tr><tr><td>T2Timer</td><td>483840</td></tr></table></div>

# ttDhcpv4ServerConfig<br><font size="2">(ClassName:  Dhcpv4ServerConfig)</font><h3><a id="ttDhcpv4ServerConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttDhcpv4ServerConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttDhcpv4ServerConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>RebindingTimePercent</td><td>87.5</td></tr><tr><td>MinAllowedLeaseTime</td><td>600</td></tr><tr><td>LeaseTime</td><td>3600</td></tr><tr><td>Name</td><td>DHCP Server 1</td></tr><tr><td>HostName</td><td>server_@p-@b-@s</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>AssignStrategy</td><td>GATEWAY</td></tr><tr><td>RenewalTimePercent</td><td>50</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>OfferReserveTime</td><td>10</td></tr><tr><td>id</td><td>2128</td></tr><tr><td>DeclineReserveTime</td><td>10</td></tr></table></div>

# ttPppoeServerBlockConfig<br><font size="2">(ClassName:  PppoeServerBlockConfig)</font><h3><a id="ttPppoeServerBlockConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttPppoeServerBlockConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttPppoeServerBlockConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>LcpTermRequestTimeout</td><td>3</td></tr><tr><td>CircuitId</td><td>circuit @s</td></tr><tr><td>EnableForceServerConnectMode</td><td>FALSE</td></tr><tr><td>EnableAutoFillIpv6</td><td>TRUE</td></tr><tr><td>EchoVendorSpecificTagInPado</td><td>FALSE</td></tr><tr><td>RelayAgentType</td><td>RFC_2516</td></tr><tr><td>Authentication</td><td>NONE</td></tr><tr><td>EchoVendorSpecificTagInPads</td><td>FALSE</td></tr><tr><td>EnableMruNegotiation</td><td>TRUE</td></tr><tr><td>EnableNcpTermination</td><td>FALSE</td></tr><tr><td>RelayAgentMacAddr</td><td>00:00:00:00:00:00</td></tr><tr><td>EnableEchoRequest</td><td>FALSE</td></tr><tr><td>MaxNaks</td><td>5</td></tr><tr><td>id</td><td>2122</td></tr><tr><td>Username</td><td>spirent</td></tr><tr><td>MaxEchoRequestAttempts</td><td>0</td></tr><tr><td>MaxPayloadBytes</td><td>1500</td></tr><tr><td>RelayAgentMacAddrStep</td><td>00:00:00:00:00:01</td></tr><tr><td>LcpTermRequestMaxAttempts</td><td>10</td></tr><tr><td>EnableMaxPayloadTag</td><td>FALSE</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>IncludeTxChapId</td><td>TRUE</td></tr><tr><td>EnableMpls</td><td>FALSE</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>NcpConfigRequestTimeout</td><td>3</td></tr><tr><td>Password</td><td>spirent</td></tr><tr><td>LcpConfigRequestMaxAttempts</td><td>10</td></tr><tr><td>ChapReplyTimeout</td><td>3</td></tr><tr><td>Name</td><td>PppoeServerBlockConfig 1</td></tr><tr><td>LcpConfigRequestTimeout</td><td>3</td></tr><tr><td>AutoCalculateMru</td><td>FALSE</td></tr><tr><td>MaxChapRequestChallengeAttempts</td><td>10</td></tr><tr><td>EchoRequestGenFreq</td><td>10</td></tr><tr><td>ServiceName</td><td></td></tr><tr><td>TotalClients</td><td>65535</td></tr><tr><td>EnableOsi</td><td>FALSE</td></tr><tr><td>RAMOFlag</td><td>NODHCP</td></tr><tr><td>IncludeRelayAgentInPadi</td><td>TRUE</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>Protocol</td><td>UNDEFINED</td></tr><tr><td>AcName</td><td>SpirentTestCenter</td></tr><tr><td>UnconnectedSessionThreshold</td><td>0</td></tr><tr><td>PapPeerRequestTimeout</td><td>3</td></tr><tr><td>RelayAgentMacAddrMask</td><td>ff:ff:ff:ff:ff:ff</td></tr><tr><td>MruSize</td><td>1492</td></tr><tr><td>RemoteOrSessionId</td><td>remote @m-@p-@b</td></tr><tr><td>ServerInactivityTimer</td><td>30</td></tr><tr><td>EnableRelayAgent</td><td>FALSE</td></tr><tr><td>EnableMagicNum</td><td>TRUE</td></tr><tr><td>IncludeRelayAgentInPadr</td><td>TRUE</td></tr><tr><td>IpcpEncap</td><td>IPV4V6</td></tr><tr><td>NcpConfigRequestMaxAttempts</td><td>10</td></tr></table></div>

# ttDhcpv6ServerConfig<br><font size="2">(ClassName:  Dhcpv6ServerConfig)</font><h3><a id="ttDhcpv6ServerConfig.h3link" href="JavaScript:;" onclick="toggle_visibility('ttDhcpv6ServerConfig');">Object Property Reference [+]</a></h3>

<div class="section" style="display:none;" id="ttDhcpv6ServerConfig"><table><tr><th>Property</th><th>Value</th></tr><tr><td>AuthKeySpecMethod</td><td>LIST</td></tr><tr><td>AuthKeyCount</td><td>1</td></tr><tr><td>ReconfigureKey</td><td>spirentcom123456</td></tr><tr><td>Name</td><td>DHCPv6 Server 1</td></tr><tr><td>EmulationMode</td><td>DHCPV6</td></tr><tr><td>UsePartialBlockState</td><td>FALSE</td></tr><tr><td>AuthKeyIdStart</td><td>1</td></tr><tr><td>PreferredLifetime</td><td>604800</td></tr><tr><td>id</td><td>2125</td></tr><tr><td>RebindingTimePercent</td><td>80</td></tr><tr><td>EnableDelayedAuth</td><td>FALSE</td></tr><tr><td>EnableReconfigureKey</td><td>FALSE</td></tr><tr><td>ReconfigureKeyValueType</td><td>ASCII</td></tr><tr><td>LocalActive</td><td>TRUE</td></tr><tr><td>RenewalTimePercent</td><td>50</td></tr><tr><td>AuthKeyValuePattern</td><td></td></tr><tr><td>ValidLifetime</td><td>2592000</td></tr><tr><td>DhcpRealm</td><td>spirent.com</td></tr><tr><td>Active</td><td>TRUE</td></tr><tr><td>AuthKeyIdStep</td><td>1</td></tr><tr><td>AuthKeyValueType</td><td>ASCII</td></tr></table></div>