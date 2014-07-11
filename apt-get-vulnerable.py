import urllib
import fileinput
import re
import os
import report


#get packet page
def get_packet_page(packet):
    #try to implement a db with source package to avoid requesting twice the same page
    packet_page_url = "https://packages.debian.org/" + lang + "/" + distrib + "/"
    packet_page_url += packet
    return urllib.urlopen(packet_page_url).read()

#get debian official changelog file for a packet and a version
def get_changelog_file(packet, version):
    source_packet = get_source_packet(packet)
    #use a cache folder to avoid downloading twice the same changelog
    if os.path.isfile("cache/" + distrib + "/" + source_packet + "_" + version + ".txt") is False:
        packet_page = get_packet_page(packet)
        changelog_url = packet_page.partition("_changelog")[0].rpartition('http://')[2]
        changelog_url = "http://" + changelog_url + "_changelog"

        changelog_file = open("cache/" + distrib + "/" + source_packet + "_" + version + ".txt",'w')
        changelog_file.write(urllib.urlopen(changelog_url).read())
        changelog_file.close()

    with open("cache/" + distrib + "/" + source_packet + "_" + version + ".txt", 'r') as content_file:
        changelog = content_file.read()
    
    return changelog

#get source packet
def get_source_packet(packet):
    packet_page = get_packet_page(packet)
    if packet_page.partition('<div id="psource">')[1] == '<div id="psource">':
        source_packet = packet_page.partition('<div id="psource">')[2].partition('</div>')[0]
        source_packet = source_packet.partition('>')[2].partition('</a>')[0]
    else:
        source_packet = packet
        
    return source_packet

#get a list with [packet_name, uptodate_version] from "apt-get --simulate update"
def get_update_list(filename):
    update_list = []

    for line in fileinput.input(filename):
        if line[0:4] == 'Conf':
            packet_name = line.partition('Conf ')[2].partition(' ')[0]
            packet_version = line.partition('(')[2].partition(' ')[0]
            ##Raspian specific
            #update_list.append([packet_name, clean_packet_version(packet_version)])
            update_list.append([packet_name, packet_version])
            ##End
    return update_list

#get a packet list with [packet_name, version] from "dpkg -l"
def get_packet_dict(filename):
    packet_dict = {}

    for line in fileinput.input(filename):
        if line[0:2] == 'ii':
            list_temp = line.split(' ')
            while '' in list_temp:
                list_temp.remove('')
            #you have to split :, because some packet have proc info in name
            #like "libc6:i386"
            packet_dict[list_temp[1].split(':')[0]] = list_temp[2]

    return packet_dict


def analyse_packet(packet, actual_version, new_version):
    changelog_file = get_changelog_file(packet, new_version).split('\n')
    
    packet_changelog = ""
    #escape specifics chars
    ##Raspian Specific
    #actual_version_regex = clean_packet_version(actual_version).replace('.', '\.')
    actual_version_regex = actual_version.replace('.', '\.')
    ##End
    actual_version_regex = actual_version_regex.replace('+', '\+')
    
    pattern_to_stop = ".*\(" + actual_version_regex + "\).*"
    pattern_for_security = ".*security.*"
    is_security_update = False

    for line in changelog_file:
        if re.match(pattern_for_security, line):
                is_security_update = True
        if re.match(pattern_to_stop, line):
            break
        else:
            packet_changelog += line + '<br/>\n'

    return [packet, actual_version, new_version, is_security_update, packet_changelog]

#extract cve from changelog (return a string)
def extract_cve(changelog):
    cve_string = ""
    cve_pattern = "CVE-[12][09][1-9]{2}-[0-9]{4}"
    cve_list = set(sorted(re.findall(cve_pattern, changelog)))
    for cve in cve_list:
        cve_string += cve + ", "

    return cve_string[:-2]

#return a dic with source packet as key from a list with [packet_name, actual_version, new_version, is_security_update, packet_changelog]    
def get_update_packet_list_by_source_packet(update_list):
    source_packet_update_info = {}
    for packet in update_list:
        #we only keep security update
        if packet[3]:
            source_packet = get_source_packet(packet[0])
            if source_packet in source_packet_update_info.keys():
                source_packet_update_info[source_packet][0].append(packet[0])
            else:
                source_packet_update_info[source_packet] = [[packet[0]], packet[1], packet[2], packet[4], extract_cve(packet[4])] 
    #format: [source_packet] = [packet_list, actual_version, new_version, packet_changelog, cve]
    return source_packet_update_info

###Main###

def main():
    global lang
    global distrib

    lang = 'fr'
    distrib = 'wheezy'
    
    packet_list_to_update = get_update_list("upgrade.txt")
    
    packet_list = get_packet_dict("dpkg.txt")

    packet_update_info = []
    for packet in packet_list_to_update:
        #anayse_packet(packet_name, version, update_version)
        packet_update_info.append(analyse_packet(packet[0], packet_list[packet[0]], packet[1]))

    source_packet_update_info = get_update_packet_list_by_source_packet(packet_update_info)

    return report.export_to_html(source_packet_update_info)
    
main()
