import requests, json
requests.packages.urllib3.disable_warnings()
date = input("date (2018-08-28)")
url = "https://noc-dash-test01.phx1.jivehosted.com/flaskduty/events?since=" + date + "&until=" + date
data = requests.get(url, verify=False).json()

top = """<p style="min-height: 8pt; padding: 0px;">&nbsp;</p>
<div class="j-rte-table">
<table border="1" class="jiveBorder" style="border-image: initial; width: 100%; border: 1px solid #000000;">
<thead>
<tr style="height: 50px;">
<th style="text-align: center; color: #ffffff; padding: 2px; width: 38px; background-color: #6690bc; height: 50px;" valign="middle">
<p><strong>Start<br /></strong></p>
</th>
<th style="text-align: center; color: #ffffff; padding: 2px; width: 38px; background-color: #6690bc; height: 50px;" valign="middle">
<p><strong>End<br /></strong></p>
</th>
<th style="text-align: center; color: #ffffff; padding: 2px; width: 38px; background-color: #6690bc; height: 50px;" valign="middle">
<p><strong>Type<br /></strong></p>
</th>
<th style="text-align: center; background-color: #6690bc; color: #ffffff; padding: 2px; height: 50px;" valign="middle">
<p><strong>Installation</strong></p>
<p><strong>(link to JCA)</strong></p>
</th>
<th style="text-align: center; background-color: #6690bc; color: #ffffff; padding: 2px; height: 50px;" valign="middle">
<p><strong>Links</strong></p>
<p><strong>(Community Case/Pagerduty/Brewspace)</strong></p>
</th>
<th style="text-align: center; background-color: #6690bc; color: #ffffff; padding: 2px; height: 50px;" valign="middle"><strong>Assessment/Actions/Updates</strong></th>
<th style="text-align: center; background-color: #6690bc; color: #ffffff; padding: 2px; height: 50px;" valign="middle"><strong>People</strong></th>
</tr>
</thead>
<tbody>"""

print top


for y in data['results']:
    startTime = ""
    endTime = ""
    pdLinks = ""
    links = ""
    people = ""
    types = ""
    assessment = ""
    jcaUrls = ""
    for x in y['alerts']:
        startTime+=json.dumps(x['startTime'])
        endTime+=json.dumps(x['endTime'])
        jcaUrls+='<a|href="' + json.dumps(x['jcaLink']['jcaUrl']).replace('null', '').replace('"', '') + '">' + json.dumps(x['jcaLink']['name']).replace('"', '') + '</a>\n'
        pdLinks+='<a|href="' + json.dumps(x['alertLink']).replace('"', '') + '">' + json.dumps(x['alertId']).replace('"', '') + '</a>\n'
    for x in y['links']:
        links+='<a|href="' + json.dumps(x['url']).replace('"', '') + '">' + json.dumps(x['url']).replace('"', '') + '</a>\n'
    people+=json.dumps(y['people']).replace('"', '').replace('null', '').replace(']', '').replace('[', '')
    types+=json.dumps(y['alertType']).replace('"', '').replace('null', '')
    assessment+=json.dumps(y['assessment']).replace('"', '').replace('null', '')
    jcaUrls = "\n".join(set(jcaUrls.split())).replace('|', ' ')
    print "<tr style=\"height: 25px;\">"
    print "<td style=\"height: 25px;\">" + startTime.replace("\"\"", '\n').replace('null', '').replace('"', '') + "</td>"
    print "<td style=\"height: 25px;\">" + endTime.replace("\"\"", '\n').replace('null', '').replace('"', '') + "</td>"
    print "<td colspan=\"1\" style=\"height: 25px;\">" + types + "</td>"
    print "<td colspan=\"1\" style=\"height: 25px;\">" + jcaUrls.replace('|', ' ') + "</td>"
    print "<td colspan=\"1\" style=\"height: 25px;\">" + pdLinks.replace('|', ' ') + links.replace('|', ' ') + "</td>"
    print "<td style=\"height: 25px;\">" + assessment + "</td>"
    print "<td colspan=\"1\" style=\"height: 25px;\">" + people + "</td>"
    print "</tr>"

bottom = """</tbody>
</table>
</div>
<p style="min-height: 8pt; padding: 0px;">&nbsp;</p>
<p style="min-height: 8pt; padding: 0px;">&nbsp;</p>
<p>Type:</p>
<p style="padding-left: 30px;">1 = Single Node Outage (implies V)</p>
<p style="padding-left: 30px;">S = Site Outage (implies V)</p>
<p style="padding-left: 30px;">T = Transient (Clears within 10 mins&nbsp; - requires V or F)</p>
<p style="padding-left: 30px;">V = Valid (legitimate alert)</p>
<p style="padding-left: 30px;">F = False (site is OK)</p>
<p style="padding-left: 30px;">N = No NOC action available</p>
<p style="padding-left: 30px;">? = Unknown</p>"""

print bottom