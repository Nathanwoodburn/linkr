def links(links,host=""):
    host = "https://"+host+"/"

    html = ""
    for link in links:
        html += "<div class='link'><a href='"+link[3]+"' target='_blank' class='no_display'>"+host+link[2] +" -> " + link[3]+"</a>"
        html += "<div class='link-delete'><a class='no_display' href='/delete/"+link[2]+"'>Delete</a></div>"
        html += "</div>\n"
    return html