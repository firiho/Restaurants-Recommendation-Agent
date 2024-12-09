% Facts: restaurant(Name, Cuisine, Price, Distance, Times, Reservation, DietaryOptions, PaymentOptions, Seating)
restaurant('Bar Via 71', argentinian, cheap, close, [breakfast, lunch], no, [no_vegetarian], [credit_debit], indoor).
restaurant('Santos Manjares', argentinian, moderate, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('La Aguada', argentinian, moderate, mid, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('La Cabaña Restaurant', argentinian, expensive, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('Huacho', argentinian, expensive, close, [lunch, dinner], yes, [no_vegetarian], [credit_debit], indoor).
restaurant('Buenos Aires Grill', argentinian, expensive, close, [lunch, dinner], no, [vegetarian], [credit_debit], indoor).
restaurant('El Nuevo Negrin', argentinian, cheap, mid, [breakfast, lunch], no, [vegetarian], [credit_debit], indoor).
restaurant('Cafe Bar El Teatro', argentinian, moderate, close, [breakfast, lunch], no, [vegetarian], [credit_debit], indoor).

restaurant('Coya', peruvian, cheap, close, [lunch, dinner], no, [vegetarian], [credit_debit], outdoor).
restaurant('Tanta Argentina', peruvian, expensive, close, [lunch, dinner], no, [vegetarian], [credit_debit], indoor).

restaurant('Extrawurst - Brat', german, cheap, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], outdoor).

restaurant('MAGIC DRAGON', chinese, moderate, close, [breakfast, lunch], no, [no_vegetarian], [credit_debit], outdoor).
restaurant('Rong Cheng "Sisi"', chinese, expensive, close, [lunch, dinner], no, [no_vegetarian], [cash], indoor).
restaurant('家宴 JIA YAN', chinese, expensive, close, [dinner], no, [vegetarian], [cash], indoor).
restaurant('Restaurante Chi', chinese, expensive, close, [lunch, dinner], no, [no_vegetarian], [cash], indoor).

restaurant('Bogotá', columbian, moderate, close, [breakfast, lunch], no, [vegetarian], [credit_debit], outdoor).
restaurant('Los Guaduales', columbian, moderate, close, [breakfast, lunch], no, [vegetarian], [credit_debit], indoor).

restaurant('Fa Song Song', korean, moderate, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('Mr. Ho', korean, moderate, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).

% Define price values for comparison
price_value(cheap, 1).
price_value(moderate, 2).
price_value(expensive, 3).

% Define distance values for comparison
distance_value(close, 1).
distance_value(mid, 2).
distance_value(far, 3).

% Define matching rules as before
matches_cuisine(_, any).
matches_cuisine(Restaurant, Cuisine) :-
    restaurant(Restaurant, Cuisine, _, _, _, _, _, _, _).

matches_price(_, any).
matches_price(Restaurant, Price) :-
    restaurant(Restaurant, _, Price, _, _, _, _, _, _).

matches_distance(_, any).
matches_distance(Restaurant, Distance) :-
    restaurant(Restaurant, _, _, Distance, _, _, _, _, _).

matches_time(_, any).
matches_time(Restaurant, Time) :-
    restaurant(Restaurant, _, _, _, Times, _, _, _, _),
    member(Time, Times).

matches_reservation(_, any).
matches_reservation(Restaurant, Reservation) :-
    restaurant(Restaurant, _, _, _, _, Reservation, _, _, _).

matches_dietary(_, any).
matches_dietary(Restaurant, DietaryOptions) :-
    restaurant(Restaurant, _, _, _, _, _, Dietary, _, _),
    forall(member(Option, DietaryOptions), member(Option, Dietary)).

matches_payment(_, any).
matches_payment(Restaurant, Payment) :-
    restaurant(Restaurant, _, _, _, _, _, _, Payments, _),
    member(Payment, Payments).

matches_seating(_, any).
matches_seating(Restaurant, Seating) :-
    restaurant(Restaurant, _, _, _, _, _, _, _, Seating).



% Dispatcher: checks a single filter
check_filter(Restaurant, match(matches_cuisine,Value)) :- matches_cuisine(Restaurant,Value).
check_filter(Restaurant, match(matches_price,Value)) :- matches_price(Restaurant,Value).
check_filter(Restaurant, match(matches_distance,Value)) :- matches_distance(Restaurant,Value).
check_filter(Restaurant, match(matches_time,Value)) :- matches_time(Restaurant,Value).
check_filter(Restaurant, match(matches_reservation,Value)) :- matches_reservation(Restaurant,Value).
check_filter(Restaurant, match(matches_dietary,Value)) :- matches_dietary(Restaurant,Value).
check_filter(Restaurant, match(matches_payment,Value)) :- matches_payment(Restaurant,Value).
check_filter(Restaurant, match(matches_seating,Value)) :- matches_seating(Restaurant,Value).

% Check all filters
check_all_filters(_, []).
check_all_filters(Restaurant, [F|Fs]) :-
    check_filter(Restaurant, F),
    check_all_filters(Restaurant, Fs).

% Current matches without using call/3 dynamically
current_matches(Filters, Matches) :-
    findall(Restaurant, (
        restaurant(Restaurant, _, _, _, _, _, _, _, _),
        check_all_filters(Restaurant, Filters)
    ), Matches).

% ask_input and ask_dietary_options remain similar, just no changes required there
ask_input(Prompt, Predicate, OldFilters, NewFilters, ErrorMsg) :-
    repeat,
    write(Prompt), nl,
    read(UserInput),
    (   UserInput == any ->
        NewFilters = OldFilters,
        current_matches(NewFilters, Matches),
        (Matches \= [] -> !; write(ErrorMsg), nl, fail)
    ;   % Add new filter
        NewFiltersTmp = [match(Predicate, UserInput)|OldFilters],
        current_matches(NewFiltersTmp, Matches),
        (Matches \= [] -> NewFilters = NewFiltersTmp, !; write(ErrorMsg), nl, fail)
    ).

ask_dietary_options(OldFilters, NewFilters, ErrorMsg) :-
    repeat,
    write('What dietary options do you require? (e.g., [vegetarian] or "any"): '), nl,
    read(UserInput),
    (   UserInput == any ->
        NewFilters = OldFilters,
        current_matches(NewFilters, Matches),
        (Matches \= [] -> !; write(ErrorMsg), nl, fail)
    ;   is_list(UserInput) ->
        NewFiltersTmp = [match(matches_dietary, UserInput)|OldFilters],
        current_matches(NewFiltersTmp, Matches),
        (Matches \= [] -> NewFilters = NewFiltersTmp, !; write(ErrorMsg), nl, fail)
    ;   write('Please provide a list or "any".'), nl, fail
    ).

get_recommendation :-
    Filters = [],
    ask_input('What type of cuisine are you looking for? (or "any"):', 
              matches_cuisine, Filters, Filters1,
              'No restaurants offer this cuisine. Try another.'),

    ask_input('What is your budget? (cheap/moderate/expensive or "any"):', 
              matches_price, Filters1, Filters2,
              'No restaurants match this price range. Try another.'),

    ask_input('How far are you willing to travel? (close/mid/far or "any"):', 
              matches_distance, Filters2, Filters3,
              'No restaurants are available at this distance. Try another.'),

    ask_input('What time of day will you be eating? (breakfast/lunch/dinner or "any"):', 
              matches_time, Filters3, Filters4,
              'No restaurants are available at this time. Try another.'),

    ask_dietary_options(Filters4, Filters5, 
                        'No restaurants meet your dietary requirements. Try another.'),

    ask_input('What payment method do you prefer? (credit_debit/cash or "any"):', 
              matches_payment, Filters5, Filters6,
              'No restaurants support this payment method. Try another.'),

    ask_input('What seating do you prefer? (indoor/outdoor or "any"):', 
              matches_seating, Filters6, FinalFilters,
              'No restaurants offer this seating option. Try another.'),

    current_matches(FinalFilters, Matches),
    (   Matches = [] ->
        write('Sorry, no restaurant matches your preferences.'), nl
    ;   write('Recommended Restaurants:'), nl,
        print_all_restaurants(Matches)
    ).

print_all_restaurants([]).
print_all_restaurants([R|Rs]) :-
    write('- '), write(R), nl,
    print_all_restaurants(Rs).