from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pyswip import Prolog
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

prolog = Prolog()
prolog.consult("kb.pl")

# Steps and their corresponding predicates
steps = [
    ("cuisine", "matches_cuisine", "What type of cuisine are you looking for?", ['argentinian', 'peruvian', 'german', 'chinese', 'columbian', 'korean', 'any']),
    ("price", "matches_price", "What is your budget?", ["cheap", "moderate", "expensive", "any"]),
    ("distance", "matches_distance", "How far are you willing to go?", ["close", "mid", "far", "any"]),
    ("time", "matches_time", "What time of day will you be eating?", ["breakfast", "lunch", "dinner", "any"]),
    ("reservation", "matches_reservation", "Do you require a reservation?", ["yes", "no", "any"]),
    ("dietary", "matches_dietary", 'What dietary options do you require?', ['vegetarian', 'no_vegetarian', 'any']),
    ("payment", "matches_payment", "What payment method do you prefer?", ["credit_debit", "cash", "any"]),
    ("seating", "matches_seating", "What seating do you prefer?", ["indoor", "outdoor", "any"])
]

# Mapping options to display strings
options = {
    'argentinian': 'Argentinian',
    'peruvian': 'Peruvian',
    'german': 'German',
    'chinese': 'Chinese',
    'columbian': 'Columbian',
    'korean': 'Korean',
    'cheap': 'Cheap',
    'moderate': 'Moderate',
    'expensive': 'Expensive',
    'close': 'Close',
    'mid': 'Mid',
    'far': 'Far',
    'breakfast': 'Breakfast',
    'lunch': 'Lunch',
    'dinner': 'Dinner',
    'vegetarian': 'Vegetarian',
    'no_vegetarian': 'Non Vegetarian',
    'credit_debit': 'Credit/Debit Card',
    'cash': 'Cash',
    'indoor': 'Indoors',
    'outdoor': 'Outdoors',
    'any': 'Any',
    'yes': 'Yes',
    'no': 'No'
}

# Reverse lookup from display strings back to keys
reverse_options = {v: k for k, v in options.items()}

restaurants = {
    'Bar Via 71': 'https://www.google.com/maps/place/Bar+Via+71/...', 
    'Santos Manjares': 'https://maps.app.goo.gl/VZmBmYtekwD9VtJY8',
    'La Aguada': 'https://maps.app.goo.gl/jkXGCbbJUn2DhLiq7',
    'La Cabana Restaurant': 'https://www.google.com/maps/place/La+Caba%C3%B1a+Restaurant/...',
    'Huacho': 'https://www.google.com/maps/place/Huacho/...',
    'Buenos Aires Grill': 'https://www.google.com/maps/place/Buenos+Aires+Grill/...',
    'El Nuevo Negrin': 'https://maps.app.goo.gl/qCYmqrsDfhwByaRcA',
    'Cafe Bar El Teatro': 'https://maps.app.goo.gl/K9nEDcMvr13LmCKHA',
    'Coya': 'https://maps.app.goo.gl/n6qSHfUKdzDmhz1S6',
    'Tanta Argentina': 'https://maps.app.goo.gl/uzgKZiw37abAwuoh8',
    'Extrawurst - Brat': 'https://maps.app.goo.gl/Pn6hrNbcj8Krtz5L8',
    'MAGIC DRAGON': 'https://maps.app.goo.gl/qHCCQhtuYa5cmviJ6',
    'Rong Cheng Sisi': 'https://maps.app.goo.gl/rh8cejY1kDU1fbSr8',
    'Jia Yan': 'https://maps.app.goo.gl/pvS3qx92nfx9Pe3w7',
    'Restaurante Chi': 'https://maps.app.goo.gl/ajWS2rjmq9FS1b8VA',
    'Bogota': 'https://maps.app.goo.gl/gBrNWbJg8eRB7Son7',
    'Los Guaduales': 'https://maps.app.goo.gl/edySgzKj86irQim49',
    'Fa Song Song': 'https://maps.app.goo.gl/2tTD8TLgfkYzrVC48',
    'Mr. Ho': 'https://maps.app.goo.gl/skP1RXWaDyuvGRPA6'
}

# Restaurant images
rest_images = {
    'Bar Via 71': 'https://img.restaurantguru.com/rf62-photo-Bar-Via-71-2022-10.jpg', 
    'Santos Manjares': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/08/fb/75/35/santos-manjares.jpg',
    'La Aguada': 'https://media-cdn.tripadvisor.com/media/photo-s/0f/3f/30/b9/la-aguada.jpg',
    'La Cabana Restaurant': 'https://media-cdn.tripadvisor.com/media/photo-s/1a/4c/c9/53/foto-nueva-de-entrada.jpg',
    'Huacho': 'https://media-cdn.tripadvisor.com/media/photo-s/2b/10/f2/e4/huacho.jpg',
    'Buenos Aires Grill': 'https://media-cdn.tripadvisor.com/media/photo-s/19/2f/19/58/avenida-corrientes-1318.jpg',
    'El Nuevo Negrin': 'https://img.restaurantguru.com/r9f3-interior-El-Nuevo-Negrin.jpg',
    'Cafe Bar El Teatro': 'https://media-cdn.tripadvisor.com/media/photo-s/16/4e/36/5c/cafe-y-restaurante-tradicional.jpg',
    'Coya': 'https://media-cdn.tripadvisor.com/media/photo-s/09/ed/5e/50/photo0jpg.jpg',
    'Tanta Argentina': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/17/4d/0e/69/salon-con-jardin-interior.jpg?w=900&h=500&s=1',
    'Extrawurst - Brat': 'https://media-cdn.tripadvisor.com/media/photo-s/13/93/17/ea/excelente-wurst-alemanas.jpg',
    'MAGIC DRAGON': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0e/9c/5e/04/magic-dragon-abasto-vista.jpg?w=1200&h=-1&s=1',
    'Rong Cheng Sisi': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0e/0a/43/cf/20170102-213210-largejpg.jpg?w=1200&h=-1&s=1',
    'Jia Yan': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1b/8a/64/0d/jia-yan.jpg?w=900&h=500&s=1',
    'Restaurante Chi': 'https://media-cdn.tripadvisor.com/media/photo-s/19/77/2e/af/frente.jpg',
    'Bogota': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTWvmjYPa_a5XUoVkL_YI75kNQ3FJypQ9ByzA&s',
    'Los Guaduales': 'https://dynamic-media-cdn.tripadvisor.com/media/photo-o/09/00/89/11/restaurante-los-guaduales.jpg?w=700&h=-1&s=1',
    'Fa Song Song': 'https://media-cdn.tripadvisor.com/media/photo-s/18/c7/cf/ca/fa-song-song.jpg',
    'Mr. Ho': 'https://lh5.googleusercontent.com/p/AF1QipOcrUxtLUIpptEO_9DaAv7mHLRCmT1BWZizC7tT'
}


def current_matches(filters):
    # Query Prolog for current matches
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
        "options": [options[option] for option in steps[step_idx][3]],
        "message": None,
        "step_idx": step_idx
    })

# Handle the next step in the conversation
@app.post("/next", response_class=HTMLResponse)
async def next_step(
    request: Request,
    action: str = Form(None),
    step_idx: int = Form(0),
    cuisine: str = Form(None),
    price: str = Form(None),
    distance: str = Form(None),
    time: str = Form(None),
    reservation: str = Form(None),
    dietary: str = Form(None),
    payment: str = Form(None),
    seating: str = Form(None)
):

    # Handle "Restart"
    if action == "restart":
        # Just redirect to the start
        return RedirectResponse(url="/", status_code=303)

    # Convert user-selected display values to keys if needed
    def convert(val):
        if val is None:
            return None
        if val in reverse_options:
            return reverse_options[val]
        return val

    cuisine = convert(cuisine)
    price = convert(price)
    distance = convert(distance)
    time = convert(time)
    reservation = convert(reservation)
    dietary = convert(dietary)
    payment = convert(payment)
    seating = convert(seating)

    # Gather all answers so far
    # Note: For going back, we rely on previous_answers being sent as hidden fields
    answers = {
        "cuisine": cuisine,
        "price": price,
        "distance": distance,
        "time": time,
        "reservation": reservation,
        "dietary": dietary,
        "payment": payment,
        "seating": seating
    }

    # If "Go Back" is clicked and not at first step
    if action == "back":
        if step_idx > 0:
            step_idx -= 1
            # Remove the answer for the current step because we're going back
            back_key = steps[step_idx][0]
            answers[back_key] = None

            # Clean out answers that come after this step (if any)
            for i in range(step_idx+1, len(steps)):
                answers[steps[i][0]] = None

            # Re-ask the previous question
            prev_answers = {k: v for k, v in answers.items() if v is not None}
            prompt = steps[step_idx][2]
            opts = steps[step_idx][3]

            return templates.TemplateResponse("question.html", {
                "request": request,
                "question_prompt": prompt,
                "current_key": steps[step_idx][0],
                "previous_answers": prev_answers,
                "options": [options[opt] for opt in opts],
                "message": None,
                "step_idx": step_idx
            })
        else:
            # If at the first step, just show the first step again
            return RedirectResponse(url="/", status_code=303)

    # Normal forward logic
    filled = [(k, v) for k,v in answers.items() if v is not None]
    current_step_idx = len(filled)

    # Build filters so far and check matches
    filters = []
    for (key, predicate, _, _) in steps:
        val = answers.get(key)
        if val is None or val.lower() == "any":
            filters.append(f"match({predicate},any)")
        else:
            filters.append(f"match({predicate},{val.lower()})")

    filters_str = "[" + ",".join(filters) + "]"
    matches = current_matches(filters_str)

    # If no matches remain, prompt user to choose another option
    if not matches:
        redo_step_idx = current_step_idx - 1
        if redo_step_idx < 0:
            # No step answered yet, just restart
            return templates.TemplateResponse("question.html", {
                "request": request,
                "question_prompt": steps[0][2],
                "current_key": steps[0][0],
                "previous_answers": {},
                "options": [options[option] for option in steps[0][3]],
                "message": "No restaurants match that choice. Try a different option.",
                "step_idx": 0
            })
        
        prev_answers = {k:v for k,v in answers.items() if v is not None and k != steps[redo_step_idx][0]}
        return templates.TemplateResponse("question.html", {
            "request": request,
            "question_prompt": steps[redo_step_idx][2],
            "current_key": steps[redo_step_idx][0],
            "previous_answers": prev_answers,
            "options": [options[opt] for opt in steps[redo_step_idx][3]],
            "message": "No restaurants match that choice. Try a different option.",
            "step_idx": redo_step_idx
        })

    # If we have matches and haven't asked all questions yet
    if current_step_idx < len(steps):
        next_key, _, prompt, opts = steps[current_step_idx]
        prev_answers = {k:v for k,v in answers.items() if v is not None}
        return templates.TemplateResponse("question.html", {
            "request": request,
            "question_prompt": prompt,
            "current_key": next_key,
            "previous_answers": prev_answers,
            "options": [options[opt] for opt in opts],
            "message": None,
            "step_idx": current_step_idx
        })
    else:
        # All questions answered, show final recommendations
        return templates.TemplateResponse("result.html", {
            "request": request,
            "matches": set(matches),
            "rest_links": restaurants,
            "rest_images": rest_images
        })

@app.post("/", response_class=HTMLResponse)
async def handle_first_step(
    request: Request,
    action: str = Form(None),
    step_idx: int = Form(0),
    cuisine: str = Form(None),
    price: str = Form(None),
    distance: str = Form(None),
    time: str = Form(None),
    reservation: str = Form(None),
    dietary: str = Form(None),
    payment: str = Form(None),
    seating: str = Form(None)
):
    return await next_step(
        request,
        action=action,
        step_idx=step_idx,
        cuisine=cuisine,
        price=price,
        distance=distance,
        time=time,
        reservation=reservation,
        dietary=dietary,
        payment=payment,
        seating=seating
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)