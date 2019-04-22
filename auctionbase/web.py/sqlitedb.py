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
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    return results[0].Time # TODO: update this as well to match the
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

#change current time manually
def changeCurrentTime(cur_time):
    query_string = 'update CurrentTime set Time = $Cur_time where Time = $old'
    try:
        result = query(query_string, {'Cur_time': cur_time,'old': getTime().encode("utf-8")})
        #return unicode(result[0].Time)
    except Exception as e:
        print str(e)
   
#auction users to enter bids on open auctions
def enterBids(itemid, userid, amount):
    query_string = 'insert into Bids(itemid, userid, amount, time) values ( $v1, $v2, $v3, $v4);'
    #try:
    result = query(query_string, {'v1' : itemid.encode("utf-8"), 'v2' : userid, 'v3' : amount.encode("utf-8"),'v4' : getTime().encode("utf-8") })
    #except Exception as e :
    #    print str(e)
    #    return False
    return True

#automatic auction closing
def auctionClosing(itemid):
    query_string = 'select Started, Ends, Currently, Buy_price from Items where ItemID = $itemid'
    try:
        result = query(query_string,{'itemid':itemid})
    except Exception as e:
        print str(e)
    else:
        if  (getTime() >= result[0].Ends | result[0].Currently >= result[0].Buy_Price | getTime() < result[0].Started) :
            return False
    return True

#browse auctions itemid, userid,min_price max_price, status
def browseAuctions(itemid, category, itemdes, min_price,max_price, status):
    itemid.encode("utf-8")
    category.encode("utf-8")
    itemdes.encode("utf-8")
    min_price.encode("utf-8")
    max_price.encode("utf-8")
    results = [] 
    result_auction = []
    result_cat = []
    query_string = 'select distinct Items.itemid from Items, Categories  where Items.ItemID = Categories.ItemID'
    if itemid != '' :
        query_string = query_string + ' and Items.ItemID = ' + itemid 
    if category != '' :
        query_string = query_string + ' and Categories.category  = \'' + category +'\''
    if itemdes != '' :
        query_string = query_string + ' and Items.description  like  \'%' + itemdes + "%\'"
    if min_price != '' :
        query_string = query_string + ' and Items.Buy_Price  >= ' + min_price 
    if max_price != '' :
        query_string = query_string + ' and Items.Buy_Price  <= ' + max_price
    if(status == 'open') :
        query_string = query_string + ' and Items.Ends > \'' + getTime().encode("utf-8") + '\' and Items.Currently >= Items.Buy_Price  and Items.Started <= \'' +getTime().encode("utf-8") +'\''
    elif(status == 'close'):
        query_string = query_string + ' and (Items.Ends <= \'' + getTime().encode("utf-8") + '\' or Items.Currently >= Items.Buy_Price  or Items.Started > \'' +getTime().encode("utf-8") +'\')'
    try:
        results = query(query_string)
        for i in range (0, len(results) - 1):
            q_str = "select * from Items where itemid = " + results[i].itemid.encode("utf-8")
            result2 = query(q_str)
            result_auction.append(result2)
            q2_str = "select * from Categories where itemid = " + results[i].itemid.encode("utf-8")
            result3 = query(q2_str)
            result_cat.append(result3)
    except Exception as e:
        print str(e)
    return results, result_auction, result_cat 
    
    
    
