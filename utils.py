
def create_translation_request_message(id,sender,region,requester,text):
    message={
        "sender":sender,
        "region":region,
        "requester":requester,
        "id":id,
        "message":text
    }
    return message

def create_translation_response_message(translation_request,sender,translated_text):
    message={
        "sender":sender,
        "region":translation_request["region"],
        "requester":translation_request["requester"],
        "id":translation_request["id"],
        "message":translated_text
    }
    return message
