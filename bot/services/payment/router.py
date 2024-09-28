import json

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from bot.config import settings
from bot.services.payment.publisher import payment_publisher
from bot.utils.payment import check_signature_result

router = APIRouter(
    prefix="/payment",
    tags=["Оплата Robokassa"],
)


@router.get("/result/", response_class=PlainTextResponse)
async def robokassa_result_url(
        request: Request,
):
    js = request.app.state.js

    number = int(request.query_params.get("InvId"))
    cost = request.query_params.get("DefaultSum")
    signature = request.query_params.get("SignatureValue")
    user_id = request.query_params.get("Shp_userId")

    if check_signature_result(
            number,
            cost,
            signature,
            settings.ROBOKASSA_TEST_PWD_2,
            f"Shp_userId={user_id}"
    ):
        await payment_publisher(
            js=js,
            subject=settings.NATS_CONSUMER_SUBJECT_PAYMENT,
            user_id=user_id,
            total_amount=cost,
            is_success=json.dumps(True)
        )
        return f'OK{number}'

    await payment_publisher(
        js=js,
        subject=settings.NATS_CONSUMER_SUBJECT_PAYMENT,
        user_id=user_id,
        total_amount=cost,
        is_success=json.dumps(False)
    )
    return "bad sign"

