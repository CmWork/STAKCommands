# AppendToEotCommand

Append Sampled data to EOT Database

<h2>- Properties</h2>

<h3>EventTableName (input:string)<br><font size=2>"Name for Event Table in DB"</font></h3>

Name for Event Table in DB

* default: Methodology_SamplingEvent

<h3>DataTableName (input:string)<br><font size=2>"Name for Data Table in DB"</font></h3>

Name for Data Table in DB

* default: Methodology_SamplingData

<h2>- UsedIn</h2>
* BGP Route Reflector Test

* Routing Multi-Protocol

* Widgets Test


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
</script># PollSubscriptionCommand

Poll and Wait for Sampling Subscription

<h2>- Properties</h2>

<h3>PollingPeriod (input:u32)<br><font size=2>"Maximum Polling Period (s)"</font></h3>

Maximum Polling Period

* default: 300

<h2>- UsedIn</h2>
* BGP Route Reflector Test

* Routing Multi-Protocol

* Widgets Test


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
</script># SetupSubscriptionCommand

Set up Sampling Subscription Command

<h2>- Properties</h2>

<h3>PollingInterval (input:u32)<br><font size=2>"Polling Interval (s)"</font></h3>

Polling Interval in seconds

* default: 1

<h3>ValueIdleTimeout (input:u32)<br><font size=2>"Time to mark subscription complete if all values stay constant"</font></h3>

Time to mark subscription complete if all polled values in subscription stay constant

* default: 60

<h3>PropertyList (input:string)<br><font size=2>"Whitespace-separated list of classname.property values"</font></h3>

Whitespace-separated list of classname.property values

* default: <font color=#cc8888>(empty string)</font>

<h3>ResultParent (input:handle)<br><font size=2>"Root(s) of subscription, port(s) or project "</font></h3>

Root(s) of subscription, can be port or project

* default: <font color=#cc8888>(empty)</font>

<h3>EnableCondition (input:bool)<br><font size=2>"Enable Terminal Values"</font></h3>

Enable Terminal Value(s) for completion of subscription

* default: false

<h3>TerminalValueList (input:u32)<br><font size=2>"Terminal Value List"</font></h3>

Terminal Value List. Subscription will be marked complete if properties reach values (count must match with subscribed property list)

* default: <font color=#cc8888>(empty)</font>

<h2>- UsedIn</h2>
* BGP Route Reflector Test

* Routing Multi-Protocol

* Widgets Test


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
</script># StoreEventCommand

Store Sampling Event Commnad

<h2>- Properties</h2>

<h3>EventName (input:string)<br><font size=2>"Name of Timestamp Event"</font></h3>

Name of Timestamp Event

* default: <font color=#cc8888>(empty string)</font>

<h2>- UsedIn</h2>
* BGP Route Reflector Test

* Routing Multi-Protocol

* Widgets Test


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