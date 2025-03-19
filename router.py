import os
from fastapi import Request
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from twilio.request_validator import RequestValidator

router = APIRouter()
twilio_validator = RequestValidator(os.environ['TWILIO_AUTH_TOKEN'])

@router.post("/twilio/text", response_class=PlainTextResponse)
async def handle_sms_webhook(request: Request):
    form_data = await request.form()
    body = form_data.get("Body")

    twilio_signature = request.headers.get("X-Twilio-Signature")
    if not twilio_signature:
        raise HTTPException(status_code=400, detail="Missing Twilio signature")
    if not twilio_validator.validate(str(request.url), dict(form_data), twilio_signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    try:
        if body.lower() == "start":
            response_message = f"Hello, we received your message to enroll in our conversational agent service. How can I help you today?"
        elif body.lower() == "stop":
            response_message = f"You have successfully been unsubscribed. You will not receive any more messages from this number. Reply START to resubscribe."
        else:
            # This is where we will handle passing the message to the agent
            response_message = "Hello"
        return response_message

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing webhook")

@router.post("/twilio/voice", response_class=PlainTextResponse)
async def handle_voice_webhook(request: Request):
    pass