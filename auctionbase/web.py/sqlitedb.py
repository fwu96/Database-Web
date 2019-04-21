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
    print vars
    return list(db.query(query_string, vars))

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
def browseAuctions(itemid, userid, min_price, max_price, status):
    query_string = 'select * from Items where '
    if itemid != None :
        query_string = query_string + ' ItemID = ' + itemid + ','
    if userid != None :
        query_string = query_string + ' Seller_UserID  = ' + userid + ','
    if min_price != None :
        query_string = query_string + ' Buy_Price  >= ' + min_price + ','
    if max_price != None :
        query_string = query_string + ' Buy_Price  <= ' + max_price
    ans = []
    try:
        result = query(query_string)
    except Exception as e:
        print str(e)
    else:
        if(status == 'Open') :
            for i in range(0, len(status)-1 ):
                if result[i].Started <= getTime() & result[i].Ends > getTime() & result[i].Currently < result[i].Buy_Price :
                    ans.add(result[i])
        
        elif(stauts == 'Close'):
            for i in range(0, len(status)-1 ) :
                if result[i].Ends <= getTime() | result[i].Currently >= result[i].Buy_Price:
                    ans.add(result[i])

        elif(stauts == 'Not Started'):
            for i in range(0, len(status)-1 ) :
                if result[i].Started > getTime() :
                    ans.add(result[i])
        else:
            ans = result
        return ans



        

    
    
    

