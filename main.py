from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pyswip import Prolog
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

prolog = Prolog()
prolog.consult("kb.pl")

# Steps and their corresponding predicates
steps = [
    ("cuisine", "matches_cuisine", "What type of cuisine are you looking for? (e.g., argentinian/peruvian/any)", []),
    ("price", "matches_price", "What is your budget? (cheap/moderate/expensive/any)", ["cheap", "moderate", "expensive"]),
    ("distance", "matches_distance", "How far are you willing to travel? (close/mid/far/any)", ["close", "mid", "far"]),
    ("time", "matches_time", "What time of day will you be eating? (breakfast/lunch/dinner/any)", ["breakfast", "lunch", "dinner"]),
    ("dietary", "matches_dietary", 'What dietary options do you require? e.g. [vegetarian] or "any"', []),
    ("payment", "matches_payment", "What payment method do you prefer? (credit_debit/cash/any)", ["credit_debit", "cash"]),
    ("seating", "matches_seating", "What seating do you prefer? (indoor/outdoor/any)", ["indoor", "outdoor"])
]

restaurants = {
    'Bar Via 71': 'https://www.google.com/maps/place/Bar+Via+71/@-34.6007042,-58.3949208,17z/data=!3m1!4b1!4m6!3m5!1s0x95bccac07840e787:0xbad7878aa65a183f!8m2!3d-34.6007042!4d-58.3923459!16s%2Fg%2F11b6phgz9z?entry=ttu&g_ep=EgoyMDI0MTIwMS4xIKXMDSoASAFQAw%3D%3D',
    'Santos Manjares': 'https://maps.app.goo.gl/VZmBmYtekwD9VtJY8',
    'La Aguada': 'https://maps.app.goo.gl/jkXGCbbJUn2DhLiq7',
    'La Cabaña Restaurant': 'https://www.google.com/maps/place/La+Caba%C3%B1a+Restaurant/@-34.6017727,-58.3937183,15z/data=!4m10!1m2!2m1!1sargentinian+restaurant!3m6!1s0x95bccaa4d11f1e09:0xee7f7e8e243b0a4a!8m2!3d-34.6041125!4d-58.3667389!15sChZhcmdlbnRpbmlhbiByZXN0YXVyYW50WhgiFmFyZ2VudGluaWFuIHJlc3RhdXJhbnSSARZhcmdlbnRpbmlhbl9yZXN0YXVyYW504AEA!16s%2Fg%2F1tgzcjp3?entry=ttu&g_ep=EgoyMDI0MTIwMS4xIKXMDSoASAFQAw%3D%3D',
    'Huacho': 'https://www.google.com/maps/place/Huacho/@-34.5958592,-58.3833978,17z/data=!3m1!4b1!4m6!3m5!1s0x95bccb33a71391b9:0x8d32030aae3d5f77!8m2!3d-34.5958593!4d-58.3785269!16s%2Fg%2F11t29nb91k?entry=ttu&g_ep=EgoyMDI0MTIwMS4xIKXMDSoASAFQAw%3D%3D',
    'Buenos Aires Grill': 'https://www.google.com/maps/place/Buenos+Aires+Grill/@-34.6017727,-58.3937183,15z/data=!4m10!1m2!2m1!1sargentinian+restaurant!3m6!1s0x95bccac5da7791cf:0x71bb1deed8edd60a!8m2!3d-34.6040508!4d-58.3854773!15sChZhcmdlbnRpbmlhbiByZXN0YXVyYW50WhgiFmFyZ2VudGluaWFuIHJlc3RhdXJhbnSSARZhcmdlbnRpbmlhbl9yZXN0YXVyYW504AEA!16s%2Fg%2F11dx8_cv0v?entry=ttu&g_ep=EgoyMDI0MTIwMS4xIKXMDSoASAFQAw%3D%3D',
    'El Nuevo Negrin': 'https://maps.app.goo.gl/qCYmqrsDfhwByaRcA',
    'Cafe Bar El Teatro': 'https://maps.app.goo.gl/K9nEDcMvr13LmCKHA',
    'Coya': 'https://maps.app.goo.gl/n6qSHfUKdzDmhz1S6',
    'Tanta Argentina': 'https://maps.app.goo.gl/uzgKZiw37abAwuoh8',
    'Extrawurst - Brat': 'https://maps.app.goo.gl/Pn6hrNbcj8Krtz5L8',
    'MAGIC DRAGON': 'https://maps.app.goo.gl/qHCCQhtuYa5cmviJ6',
    'Rong Cheng "Sisi"': 'https://maps.app.goo.gl/rh8cejY1kDU1fbSr8',
    '家宴 JIA YAN': 'https://maps.app.goo.gl/pvS3qx92nfx9Pe3w7',
    'Restaurante Chi': 'https://maps.app.goo.gl/ajWS2rjmq9FS1b8VA',
    'Bogotá': 'https://maps.app.goo.gl/gBrNWbJg8eRB7Son7',
    'Los Guaduales': 'https://maps.app.goo.gl/edySgzKj86irQim49',
    'Fa Song Song': 'https://maps.app.goo.gl/2tTD8TLgfkYzrVC48',
    'Mr. Ho': 'https://maps.app.goo.gl/skP1RXWaDyuvGRPA6'
}

def current_matches(filters):
    # Convert filters into a Prolog query using current_matches/2 from KB
    # eg:
    # filters = [(Predicate,Value), ...]
    # current_matches([match(Predicate,Value),...], Matches).
    query = f"current_matches({filters}, Matches)"
    result = list(prolog.query(query))
    if result:
        return result[0]["Matches"]
    return []

@app.get("/", response_class=HTMLResponse)
async def start(request: Request):
    # Start at the first step
    step_idx = 0
    return templates.TemplateResponse("question.html", {
        "request": request,
        "question_prompt": steps[step_idx][2],
        "current_key": steps[step_idx][0],
        "previous_answers": {},
        "options": steps[step_idx][3]
    })

@app.post("/next", response_class=HTMLResponse)
async def next_step(
    request: Request,
    cuisine: str = Form(None),
    price: str = Form(None),
    distance: str = Form(None),
    time: str = Form(None),
    dietary: str = Form(None),
    payment: str = Form(None),
    seating: str = Form(None)
):
    # Gather all answers so far
    answers = {
        "cuisine": cuisine,
        "price": price,
        "distance": distance,
        "time": time,
        "dietary": dietary,
        "payment": payment,
        "seating": seating
    }

    # Determine the next step by counting how many are filled
    filled = [(k, v) for k,v in answers.items() if v is not None]
    step_idx = len(filled)  # number of answered steps
    if step_idx < len(steps):
        # Ask the next question
        next_key, _, prompt, opts = steps[step_idx]
        # Pass all answered so far as hidden fields
        prev_answers = {k:v for k,v in answers.items() if v is not None}
        return templates.TemplateResponse("question.html", {
            "request": request,
            "question_prompt": prompt,
            "current_key": next_key,
            "previous_answers": prev_answers,
            "options": opts
        })
    else:
        # All questions answered, run final recommendation
        # Build filters based on answers
        # If dietary is a list, it needs to be Prolog list, else "any"
        filters = []
        for (key, predicate, _, _) in steps:
            val = answers[key]
            if val is None or val == "any":
                filters.append(f"match({predicate},any)")
            else:
                # We assume the user typed something like [vegetarian], we pass it as is
                if key == "dietary":
                    filters.append(f"match({predicate},{val})")
                else:
                    filters.append(f"match({predicate},{val})")

        filters_str = "[" + ",".join(filters) + "]"
        matches = current_matches(filters_str)
        return templates.TemplateResponse("result.html", {
            "request": request,
            "matches": set(matches),
            "rest_links": restaurants
        })

# Redirect form actions to /next
@app.post("/", response_class=HTMLResponse)
async def handle_first_step(
    request: Request,
    cuisine: str = Form(None),
    price: str = Form(None),
    distance: str = Form(None),
    time: str = Form(None),
    dietary: str = Form(None),
    payment: str = Form(None),
    seating: str = Form(None)
):
    return await next_step(
        request,
        cuisine=cuisine,
        price=price,
        distance=distance,
        time=time,
        dietary=dietary,
        payment=payment,
        seating=seating
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
