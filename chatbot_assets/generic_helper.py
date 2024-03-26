import re

def get_session_id(session_str: str):
    match = re.search(r"sessions\/(.*)\/contexts", session_str)

    if match:
        extracted_session = match.group(1)

        return extracted_session
    else:
        return "No session!"

def get_order_list(food_dict: dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])

# if __name__ == "__main__":
#     id = "projects/deleverybot-jqly/agent/sessions/1af2179d-bb1f-25f5-5e30-183909404f7e/contexts/ongoing-order"

#     print(get_session_id(id))