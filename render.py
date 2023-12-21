def links(links,host="",show_domain=False):
    host = "https://"+host+"/"

    html = ""
    for link in links:
        html += "<div class='link'><a href='"+link[3]+"' target='_blank' data-umami-event='Visited link from dashboard' data-umami-event-id='"+link[2] + "' class='no_display'>"+host+link[2] +" -> " + link[3]+"</a>"
        if show_domain:
            html += "<div class='link-domain'>"+link[1]+"</div>"
        html += "<div class='link-delete'><a class='no_display' data-umami-event='Deleted link' data-umami-event-id='"+link[2] + "' href='/delete/"+link[2]+"'>Delete</a></div>"
        html += "</div>\n"
    return html