import mysql.connector

# global cnx

# Create a connection to the database
cnx = mysql.connector.connect(
    host = 'localhost', 
    user =  'root',
    password = 'student',
    database = 'pandeyji_eatery'
)

def get_order_status(order_id: int):
    # try:

    # create a cursor object
    cursor = cnx.cursor()

    # Write the query
    query = ("SELECT * FROM ORDER_TRACKING where order_id = %s")

    # Execute the query
    cursor.execute(query, (order_id, ))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    # except Exception as e:
    #     return e
    if result is not None:
        return result[1]
    else:
        return None
    

def get_order_id():
    # create a cursor object
    cursor = cnx.cursor()

    # Write the query
    query = ("SELECT MAX(order_id) FROM orders")

    # Execute the query
    cursor.execute(query)

    # Fetch the result
    result = cursor.fetchone()[0]

    # Close the cursor and connection
    cursor.close()
    # except Exception as e:
    #     return e
    if result is not None:
        return result+1
    else:
        return 1
    
def insert_order(food_items, quantities, order_id):

    try:
        # create a cursor object
        cursor = cnx.cursor()

        # Calling stored procedure
        cursor.callproc("insert_order_item", (food_items, quantities, order_id))

        # Commite the changes
        cnx.commit()

        # Close the cursor and connection
        cursor.close()
        # except Exception as e:
        #     return e

        print("Order item inserted successfully.")

        return 1
    except Exception as e:
        print("Error during insertion:\t", e)

        #Rollback changes
        cnx.rollback()

        return -1

def get_order_total(order_id: int):
    cursor = cnx.cursor()


    # Get total order
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    # Fetching result
    result = cursor.fetchone()[0]

    #Close cursor
    cursor.close()

    return result

def insert_order_tracking(order_id:int, status:str):
    cursor = cnx.cursor()

    # Inserting order into order tracking
    query = "insert into order_tracking (order_id, status) values(%s, %s);"

    # Execute query
    cursor.execute(query, (order_id, status))

    #Commit the changes
    cnx.commit()

    #Close the cursor
    cursor.close()
if __name__ == "__main__":
    id = "projects/deleverybot-jqly/agent/sessions/1af2179d-bb1f-25f5-5e30-183909404f7e/contexts/ongoing-order"

    print(get_order_id()+1)