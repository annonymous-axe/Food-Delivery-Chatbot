from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_orders = {}

@app.post('/')
async def handle_request(request:Request):

    
    # Retreive JSON Data from the request
    payload = await request.json()

    # Extract the necessary information from payload
    # Based on the structure of the WebhookRequest from DialogFlow
    intent     = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_context = payload['queryResult']['outputContexts']
    
    session_id = generic_helper.get_session_id(output_context[0]['name'])

    # if intent == 'trackOrder - context:ongoing-tracking':
    #     status =  track_order(parameters)
    #     return status
    
    intent_handler_dic = {
        "orderAdd - context:ongoing-order" : add_to_order,
        "orderComplete - context:ongoing-order" : complete_order,
        "orderRemove - context:ongoing-order" : remove_from_order,
        "trackOrder - context:ongoing-tracking" : track_order
    }

    return intent_handler_dic[intent](parameters, session_id)

def remove_from_order(parameters: dict, session_id: str):

    fulfillment_text = ''

    items = parameters["food-items"]
    quantities = [int(num) for num in parameters["number"]]

    if session_id not in inprogress_orders:
        fulfillment_text = "Sorry, but I can't find your order. Can you order again!"
        return JSONResponse(content={
            "fulfillmentText" : fulfillment_text
        })

    else:
        removed_items = {}
        no_such_items = []
        for item, quantity in zip(items, quantities):
            
            if item not in inprogress_orders[session_id]:
                no_such_items.append(item)
            elif item in inprogress_orders[session_id]:
                current_quantity = inprogress_orders[session_id][item]
                removed_items[item] = quantity
                if current_quantity - quantity == 0:
                    inprogress_orders[session_id].pop(item)
                else:
                    inprogress_orders[session_id][item] -= int(quantity)
    if len(removed_items.keys()) > 0:
        fulfillment_text += f"Removed items {generic_helper.get_order_list(removed_items)} done!"
    if len(no_such_items) > 0:
        fulfillment_text += f"Items not found {", ".join(no_such_items)}."
    if len(inprogress_orders[session_id]) == 0:
        fulfillment_text += "You don't have any items remaining now!So add items before ordering food."
        del inprogress_orders[session_id]
    else:
        fulfillment_text += f"Now you have {inprogress_orders[session_id]}."

    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })

def add_to_order(parameters: dict, session_id: str):

    items = parameters["food-items"]
    quantities = parameters["number"]

    
    
    if len(items) != len(quantities):
        fulfillment_text = "Sorry, but can you mention the clear quantities and food items you want?"
    else:

        new_food_dict = dict(zip(items, quantities))

        if session_id in inprogress_orders:
            # print("Old order\t:", inprogress_orders[session_id])
            current_food_dict = inprogress_orders[session_id]
            new_food_dict.update(current_food_dict)
            inprogress_orders[session_id] = new_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        # print("="*10)
        # print("Session\t:",session_id)
        # print("Order\t:", inprogress_orders[session_id])
        # print("dict\t:", new_food_dict)
        # print("-"*10)
        order_list = generic_helper.get_order_list(inprogress_orders[session_id])    

        fulfillment_text = f"Order summary: {order_list}. You want to add anything else?"   
    
    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })

def complete_order(parameters:dict, session_id: str):

    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble to finding your order, can you just placed your order again!"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = "Server is down."
        else:
            order_total = db_helper.get_order_total(order_id)
            fulfillment_text = f"Awesome, we placed your order. Here is your order id : {order_id}."\
                               f"Your order total is {order_total}, which you can pay on delivery." 
            
            del inprogress_orders[session_id]
    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })

def save_to_db(order: dict):

    order_id = db_helper.get_order_id()

    for item, quantities in order.items():
        flag = db_helper.insert_order(
            item, 
            quantities,
            order_id
        )

        if flag == -1:
            return -1
    
    db_helper.insert_order_tracking(order_id, "in progress")
    return order_id



def track_order(parameters: dict, session_id: str):
    order_id = parameters['number'][0] // 1

    order_status = db_helper.get_order_status(order_id)
    # order_status = None

    if order_status is not None:
        fulfillment_text = f"The order status is: {order_status}"
    else:
        fulfillment_text = f"No order found with id:{order_id}"
    return JSONResponse(content={
        "fulfillmentText" : fulfillment_text
    })
    

