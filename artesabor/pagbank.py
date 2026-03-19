import urllib.request
import urllib.error
import json
from django.conf import settings
from datetime import datetime, timedelta
from django.utils.timezone import now

def create_pix_order(order, cart_items, user):
    url = f"{settings.PAGBANK_API_URL}orders"

    items_payload = []
    total_value_cents = 0
    
    for item in cart_items:
        quantity = item['quantity'] if isinstance(item, dict) else item.quantity
        product = item['product'] if isinstance(item, dict) else item.product
        price_cents = int(product.price * 100)
        
        items_payload.append({
            "reference_id": str(product.id)[:10],
            "name": product.name,
            "quantity": quantity,
            "unit_amount": price_cents
        })
        total_value_cents += price_cents * quantity

    expiration = (now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S-03:00")
    

    payload = {
        "reference_id": str(order.id),
        "customer": {
            "name": getattr(user, 'name', f"{user.username} Silva") or "Cliente Teste",
            "email": user.email,
            "tax_id": "13004343410", 
            "phones": [
                {
                    "country": "55",
                    "area": "11",
                    "number": "999999999",
                    "type": "MOBILE"
                }
            ]
        },
        "items": items_payload,
        "qr_codes": [
            {
                "amount": {
                    "value": total_value_cents
                },
                "expiration_date": expiration
            }
        ]
    }
    

    headers = {
        "Authorization": f"Bearer {settings.PAGBANK_TOKEN}",
        "Content-type": "application/json",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return {
                "success": True,
                "order_id": res_data.get("id"),
                "qr_codes": res_data.get("qr_codes", []),
                "raw": res_data
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"Erro PagBank: {error_body}")
        return {
            "success": False,
            "error": error_body
        }
    except Exception as e:
        print(f"Exceção PagBank: {e}")
        return {
            "success": False,
            "error": str(e)
        }
