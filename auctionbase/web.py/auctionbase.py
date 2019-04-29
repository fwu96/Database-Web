#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/add_bid','add_bid',
        '/search','search',
        '/curr_time', 'curr_time',
        # '/searchOne', 'searchResult',
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )
global searchingResult
searchingResult = []
class curr_time:
    # A simple GET request
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        t = sqlitedb.transaction()
        try:
            current_time = sqlitedb.getTime()
        except Exception as e:
            t.rollback()
            print str(e)
        else:
            t.commit()
        return render_template('curr_time.html', time = current_time)


class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss']
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database
        t = sqlitedb.transaction()
        try:
            sqlitedb.changeCurrentTime(selected_time.encode("utf-8"))
            selected_time = unicode(selected_time)
            # Here, we assign `update_message' to `message', which means
            # we'll refer to it in our template as `message'
        except Exception as e:
            t.rollback()
            print str(e)
        else:
            t.commit()
        return render_template('select_time.html', message = update_message)

class add_bid:
    def GET(self) :
         return render_template('add_bid.html')

    def POST(self) :
        post_params = web.input()
        itemID = post_params['itemID']
        price = post_params['price']
        userID = post_params['userID']
        t = sqlitedb.transaction()
        try:
            add_result = sqlitedb.enterBids(itemID,userID.encode("utf-8"),price)
        except Exception as e:
            t.rollback()
            print str(e)
        else:
            t.commit()
        return render_template('add_bid.html', add_result = add_result)

class search:
    def GET(self):
        return render_template('search.html')
    
    def POST(self) :
        post_params = web.input()
        itemID = post_params['itemID']
        maxPrice = post_params['maxPrice']
        minPrice = post_params['minPrice']
        status =  post_params['status']
        descrption = post_params['descrption']
        category =  post_params['category']
        t = sqlitedb.transaction()
        try:
            item_res = sqlitedb.browseAuctions(itemID, category, descrption, minPrice, maxPrice, status)
            global searchingResult
            searchingResult = item_res
            global urls
            a = ('/searchResult/(.*)', 'searchResult',)
            urls = urls + a
            for i in range(len(item_res)):
                urlStr = "http://0.0.0.0:8080/searchResult/search" + str(i)
                item_res[i][0].Link = urlStr
        except Exception as e:
            t.rollback()
            print str(e)
        else:
            t.commit()
        return render_template('search.html', search_result = item_res)

class searchResult:
    def GET(self, name):
        global searchingResult
        for i in range(len(searchingResult)):
            html_str = ("{% extends \"app_base.html\" %}\n"
                        "{% block content %}\n"
                        "<div><b>Auction infor</b>\n"
                        "<br>Detail Information\n"
                        "<br><b>Result</b></div>\n")
            if name == "search" + str(i):
                for j in range(len(searchingResult[i])):
                    res = searchingResult[i][j]
                    for key in res:
                        if key == "Bid":
                            html_str += ("<div>\n"
                                            "<span>" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + key + str(j - 1) + "</span>\n"
                                            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n"
                                            "<span>" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(res[key]) + "</span>\n"
                                         "</div>\n")
                        else:
                            html_str += ("<div>\n"
                                            "<span>" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + key + "</span>\n"
                                            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\n"
                                            "<span>" + "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + str(res[key]) + "</span>\n"
                                         "</div>\n")        
                    html_str += "<div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--------</div>\n"
                html_str += "{% endblock %}\n"
                Html_file = open("./templates/" + name + ".html", "w")
                Html_file.write(html_str)
                Html_file.close()
                return render_template(name + '.html')
        return render_template("")
###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
