#write an HTML file
def export_to_html(output, filename = "Security-update-analysis"):
    html_file = open(filename + ".html", "a+")
    html_file.write(convert_output_to_html(output))
    return html_file.close()

#return an HTML page from a dic with [source_packet] = [packet_list, actual_version, new_version, packet_changelog, cve]   
def convert_output_to_html(output, title = "Security update analysis"):
    html_output = "<html>\n<head><title>" + title + "</title></head>\n<body>\n"
    
    html_output += "<h1>Quick view</h1>\n"
    html_output += "<table>\n"
    html_output += "<tr><td>Source packet</td><td>Packets</td><td>Actual version</td><td>Up to date version</td><td>CVE</td></tr>\n"
    for key in output.keys():
        html_output += "<tr>"
        html_output += "<td>" + key + "</td>"
        html_output += "<td>"
        for packet in output[key][0]:
            html_output += packet + " "
        html_output += "</td>"
        html_output += "<td>" + output[key][1] + "</td>"
        html_output += "<td>" + output[key][2] + "</td>"
        html_output += "<td>" + output[key][4] + "</td>"
        html_output += "</tr>\n"
    html_output += "</table>\n"

    html_output += "<h1>Update details</h1>\n"

    for key in output.keys():
        html_output += "<h2>Source packet: " + key + "</h2>\n"
        html_output += "<h3>Packet(s): "
        for packet in output[key][0]:
            html_output += packet + " "
        html_output += "<h3>\n"
        ##Raspian specific
        #html_output += "<h3>Actual version (Raspian): " + output[key][1] + "</h3>\n"
        #html_output += "<h3>Up to date version (Debian): " + output[key][2] + "</h3>\n"	
        html_output += "<h3>Actual version: " + output[key][1] + "</h3>\n"
        html_output += "<h3>Up to date version: " + output[key][2] + "</h3>\n"	
        ##End
        html_output += "<h3>CVE</h3>\n"
        html_output += "<p>" + output[key][4] + "</p>\n"
        html_output += "<h3>Changelog</h3>\n"
        html_output += "<p>" + output[key][3] + "</p>\n"

    html_output += "</body>\n</html>"
    
    return html_output
