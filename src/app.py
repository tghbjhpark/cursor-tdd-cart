"""Boundary — Flask 주문 폼 (ECB).

계약:
- UC-1: GET / → 200, 본문에 qty·price·VIP 입력 폼 포함
- UC-2: POST /calc (price·qty·vip) → 본문에 final_total 결과 표시
- UE-1: qty가 숫자가 아니면 400 + 에러 메시지

역할: HTTP/UI 경계. 할인 계산은 Entity(src.cart.final_total)에 위임한다.
"""

from flask import Flask, request

from src.cart import final_total

app = Flask(__name__)


@app.get("/")
def index():
    return (
        '<form action="/calc" method="post">'
        '<input name="price">'
        '<input name="qty">'
        '<input name="vip" type="checkbox">'
        '<button type="submit">계산</button>'
        "</form>"
    )  # UC-1


@app.post("/calc")
def calc():
    qty_raw = request.form.get("qty", "")
    if not qty_raw.isdigit():
        return "qty must be a number", 400  # UE-1

    price = int(request.form.get("price", "0"))
    qty = int(qty_raw)
    is_vip = request.form.get("vip") == "on"
    total = final_total([(price, qty)], is_vip=is_vip)  # UC-2
    return str(total)  # UC-2
