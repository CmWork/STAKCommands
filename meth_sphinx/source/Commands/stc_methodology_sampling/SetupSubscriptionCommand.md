# SetupSubscriptionCommand

Set up Sampling Subscription Command

<font size="2">File Reference: stc_methodology_sampling.xml</font>

<text>Properties</text>

### PollingInterval: "Polling Interval (s)" (input:u32)

Polling Interval in seconds

* default - 1
### TerminalValueList: "Terminal Value List" (input:u32)

Terminal Value List. Subscription will be marked complete if properties reach values (count must match with subscribed property list)

* default - 
### EnableCondition: "Enable Terminal Values" (input:bool)

Enable Terminal Value(s) for completion of subscription

* default - false
### PropertyList: "Whitespace-separated list of classname.property values" (input:string)

Whitespace-separated list of classname.property values

* default - 
### ResultParent: "Root(s) of subscription, port(s) or project " (input:handle)

Root(s) of subscription, can be port or project

* default - 
### ValueIdleTimeout: "Time to mark subscription complete if all values stay constant" (input:u32)

Time to mark subscription complete if all polled values in subscription stay constant

* default - 60
## UsedIn
* BGP Route Reflector Test

* Routing Multi-Protocol

* Widgets Test

