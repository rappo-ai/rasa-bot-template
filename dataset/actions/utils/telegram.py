from actions.utils.json import get_json_key

def get_chat_type(metadata):
    return (get_json_key(metadata, "message.chat.type") or
     get_json_key(metadata, "callback_query.message.chat.type"))
