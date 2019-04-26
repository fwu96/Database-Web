import web

db = web.database(dbn='sqlite',
        db='AuctionBase' #TODO: add your SQLite database filename
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # TODO: update the query string to match
    # the correct column and table name in your database
    query_string = 'select Time from CurrentTime'
    dist_id = query(query_string)
    # alternatively: return dist_id[0]['currenttime']
    return dist_id[0].Time # TODO: update this as well to match the
                                  # column name

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where item_ID = $itemID'
    try:
        result = query(query_string, {'itemID': item_id})
    except Exception as e :
        print str(e)
    finally:
        return result[0]

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    result = db.query(query_string, vars)
    if(isinstance(result,int)):
        return result
    return list(result)

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time

# Manually updating current time
def changeCurrentTime(cur_time):
    query_string = 'update CurrentTime set Time = $curTime where Time = $oldTime'
    try:
        result = query(query_string, {'curTime': cur_time, 'oldTime': getTime().encode("utf-8")})
    except Exception as e:
        print str(e)
   
# Allow user to enter their bid
# return true if they enter successfully, otherwise false
# the entering result would be shown on the screen
def enterBids(itemid, userid, amount):
    query_string = 'insert into Bids(itemid, userid, amount, time) values ($v1, $v2, $v3, $v4);'
    try:
        result = query(query_string, {'v1': itemid.encode("utf-8"), 'v2': userid, 'v3': amount.encode("utf-8"), 'v4': getTime().encode("utf-8") })
    except Exception as e :
        print str(e)
        return False
    return True

# automatic auction closing
def auctionClosing(itemid):
    query_string = 'select Started, Ends, Currently, Buy_price from Items where ItemID = $itemid'
    try:
        result = query(query_string,{'itemid': itemid})
    except Exception as e:
        print str(e)
    else:
        if (getTime() >= result[0].Ends | result[0].Currently >= result[0].Buy_Price | getTime() < result[0].Started):
            return False
    return True

# browse auctions by given conditions by users
# return a list containing needed information
def browseAuctions(itemid, category, itemdes, min_price,max_price, status):
    # encode to utf-8
    itemid.encode("utf-8")
    category.encode("utf-8")
    itemdes.encode("utf-8")
    min_price.encode("utf-8")
    max_price.encode("utf-8")
    # declare needed lists
    dist_id = [] 
    info_result = []
    cat_result = []
    status_result = []
    bid_result = []
    winner_result = []
    result_list = []
    # this query gives the result of distinct itemID with the given conditions users entered
    # the ruslts are used for other queries
    query_string = 'select distinct Items.itemid from Items, Categories  where Items.ItemID = Categories.ItemID'
    if itemid != '':  # if user enter itemID
        query_string = query_string + ' and Items.ItemID = ' + itemid 
    if category != '':  # if user enter category name
        query_string = query_string + ' and Categories.category  = \'' + category +'\''
    if itemdes != '':  # if user enter part of description of items
        query_string = query_string + ' and Items.description  like  \'%' + itemdes + "%\'"
    if min_price != '':  # if user enter minimum price boundary
        query_string = query_string + ' and Items.Buy_Price  >= ' + min_price 
    if max_price != '':  # if user enter maximum price boundary
        query_string = query_string + ' and Items.Buy_Price  <= ' + max_price
    if status == 'open':  # if user only want to see open auctions
        query_string = (query_string + ' and Items.Ends > \'' + getTime().encode("utf-8") + '\' and '
                                       '((Items.Currently < Items.Buy_Price and Items.Buy_Price is not null) or Items.Buy_Price is null) ' 
                                       'and Items.Started <= \'' +getTime().encode("utf-8") +'\'')
    elif status == 'close':  # if user only want to see closed auctions
        query_string = (query_string + ' and (Items.Ends <= \'' + getTime().encode("utf-8") + '\' or '
                                       '((Items.Currently >= Items.Buy_Price and Items.Buy_Price is not null) or Items.Buy_Price is null) '
                                       'or Items.Started > \'' +getTime().encode("utf-8") +'\')')
    try:
        dist_id = query(query_string)
        for i in range (len(dist_id)):
            # query for basic information about itmes
            q_info = "select *, 'link' as Link from Items where itemid = " + str(dist_id[i].ItemID).encode("utf-8")
            info_result = query(q_info)
            # query for category information
            q_cat = 'select group_concat(category, \', \' ) as Category from Categories where itemid = ' + str(dist_id[i].ItemID).encode("utf-8") + ' group by itemID'
            cat_result = query(q_cat)
            # query for status information
            q_status = ('select (case when (Items.Ends > \'' + getTime().encode("utf-8") + '\' and '
                        '((Items.Currently < Items.Buy_Price and Items.Buy_Price is not null) or Items.Buy_Price is null) '
                        'and Items.Started <= \'' + getTime().encode("utf-8") + '\') then \'Open\' '
                        'when ((Items.Ends <= \'' + getTime().encode("utf-8") + '\' or '
                        '((Items.Currently >= Items.Buy_Price and Items.Buy_Price is not null) or '
                        'Items.Buy_Price is null) or Items.Started > \'' + getTime().encode("utf-8") + '\')) then \'Close\' '
                        'else \'All\' end) '
                        'as Status from Items where itemId = ' + str(dist_id[i].ItemID).encode("utf-8"))
            status_result = query(q_status)
            # query for bid information
            q_bid = ('select \'Name: \' || userID || \'; \' || \'Time: \' || Time || \'; \' || \'Price: \' || Amount as Bid '
                     'from Bids where itemID = ' + str(dist_id[i].ItemID).encode("utf=8") + ' group by userID order by Amount ASC')
            bid_result = query(q_bid)
            if len(bid_result) != 0:
                # query for winner information
                q_winner = ('select \'Name: \' || userID || \'; \' || \'Price: \' || Amount as Winner '
                            'from Bids where itemID = ' + str(dist_id[i].ItemID).encode("utf-8") + ' and Amount = '
                            '(select max(Amount) from Bids where itemID = ' + str(dist_id[i].ItemID).encode("utf-8") + ')')
                winner_result = query(q_winner)
            # connects all the result
            info_result.extend(cat_result)
            info_result.extend(bid_result)
            info_result.extend(status_result)
            info_result.extend(winner_result)
            # make all the information of each single auction together to the result list
            result_list.append(list(info_result))
    except Exception as e:
        print str(e)
    return result_list
