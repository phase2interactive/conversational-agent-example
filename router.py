from fastapi import Request
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.post("/twilio/text", response_class=PlainTextResponse)
async def handle_sms_webhook(request: Request):
    pass

@router.post("/twilio/voice", response_class=PlainTextResponse)
async def handle_voice_webhook(request: Request):
    pass