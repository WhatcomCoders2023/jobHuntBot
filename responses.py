
# Send responses depends on the user's command/message
def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == 'hello':
        return 'Hey there'
    
    if p_message == '!help':
        return "`Bot commands list:...`"
    

    