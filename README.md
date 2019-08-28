# fortinet_asymmetry
Parses routing data and determines asymmetric routes

Incomplete excerpt of a script used to determine asymmetric routes in Fortinet Firewall devices, by analysing ingress and egress traffic.

A typical symmetric flow is as such:

IP A (interface X) -> IP B (interface Y)
IP B (interface Y) -> IP A (interface X)

However, asymmetry occurs when this pattern is not upheld, for example:

IP A (interface X) -> IP B (interface Y)
IP B (interface Z) -> IP A (interface X)

In this case, a third interface has entered the equation, and thus the route is considered asymmetric. The reasons for why asymmetric routing is considered undesirable is outside of the scope of this readme, but can be researched online; suffice to say it creates unpredictable scenarios as firewalls are stateful, and incoming packets may be discarded as state is not communicated in the asymmetric case.

https://www.cisco.com/web/services/news/ts_newsletter/tech/chalktalk/archives/200903.html is a good summary, albeit for Cisco devices - but the principles are the same.

This script parses the data, extracting IP routes in the format above, and then loops over the entire collected data, identifying pairs (IP A -> IP B and IP B -> IP A), before assessing the ingress and egress interfaces. Designated recipients are then emailed informing them of present asymmetric routes.

This is extremely difficult to do manually as raw data can consist of hundreds of thousands of lines, and are not ordered. This is why it is necessary to loop over the entire array in a way that is time-consuming, but thorough. I also wrote a JavaScript implementation, but the method is different - the Python version removes valid comparisons from the data array until its size hits 0, where it terminates - therefore, since each line must "look through" all other lines, the speed gradually increases. JavaScript however had the opposite effect, which puzzled me for a time - upon investigation, it is determined that JavaScript does not alter the original array upon shrinking it, rather creating a new one. This results in a massive memory bloat! Recursive methods were eventually applied in that instance.

A variant of this script was used in a major international project and I received recognition and an award from senior management for my part in mitigating a major crisis.
