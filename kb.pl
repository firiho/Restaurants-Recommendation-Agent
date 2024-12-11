% Facts
restaurant('Bar Via 71', argentinian, cheap, close, [breakfast, lunch], no, [no_vegetarian], [credit_debit], indoor).
restaurant('Santos Manjares', argentinian, moderate, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('La Aguada', argentinian, moderate, mid, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('La Cabana Restaurant', argentinian, expensive, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('Huacho', argentinian, expensive, close, [lunch, dinner], yes, [no_vegetarian], [credit_debit], indoor).
restaurant('Buenos Aires Grill', argentinian, expensive, close, [lunch, dinner], no, [vegetarian], [credit_debit], indoor).
restaurant('El Nuevo Negrin', argentinian, cheap, mid, [breakfast, lunch], no, [vegetarian], [credit_debit], indoor).
restaurant('Cafe Bar El Teatro', argentinian, moderate, close, [breakfast, lunch], no, [vegetarian], [credit_debit], indoor).

restaurant('Coya', peruvian, cheap, close, [lunch, dinner], no, [vegetarian], [credit_debit], outdoor).
restaurant('Tanta Argentina', peruvian, expensive, close, [lunch, dinner], no, [vegetarian], [credit_debit], indoor).

restaurant('Extrawurst - Brat', german, cheap, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], outdoor).

restaurant('MAGIC DRAGON', chinese, moderate, close, [breakfast, lunch], no, [no_vegetarian], [credit_debit], outdoor).
restaurant('Rong Cheng Sisi', chinese, expensive, close, [lunch, dinner], no, [no_vegetarian], [cash], indoor).
restaurant('Jia Yan', chinese, expensive, close, [dinner], no, [vegetarian], [cash], indoor).
restaurant('Restaurante Chi', chinese, expensive, close, [lunch, dinner], no, [no_vegetarian], [cash], indoor).

restaurant('Bogota', columbian, moderate, close, [breakfast, lunch], no, [vegetarian], [credit_debit], outdoor).
restaurant('Los Guaduales', columbian, moderate, close, [breakfast, lunch], no, [vegetarian], [credit_debit], indoor).

restaurant('Fa Song Song', korean, moderate, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).
restaurant('Mr. Ho', korean, moderate, close, [lunch, dinner], no, [no_vegetarian], [credit_debit], indoor).

% Main matches predicate
matches(_, _, any) :- !.
matches(Rest, matches_cuisine, Cuisine) :-
    restaurant(Rest, Cuisine, _, _, _, _, _, _, _).
matches(Rest, matches_price, Price) :-
    restaurant(Rest, _, Price, _, _, _, _, _, _).
matches(Rest, matches_distance, Distance) :-
    restaurant(Rest, _, _, Distance, _, _, _, _, _).
matches(Rest, matches_time, Time) :-
    restaurant(Rest, _, _, _, Times, _, _, _, _),
    member(Time, Times).
matches(Rest, matches_reservation, Reservation) :-
    restaurant(Rest, _, _, _, _, Reservation, _, _, _).
matches(Rest, matches_dietary, DietaryOptions) :-
    restaurant(Rest, _, _, _, _, _, Dietary, _, _),
    forall(member(D, DietaryOptions), member(D, Dietary)).
matches(Rest, matches_payment, Payment) :-
    restaurant(Rest, _, _, _, _, _, _, Payments, _),
    member(Payment, Payments).
matches(Rest, matches_seating, Seating) :-
    restaurant(Rest, _, _, _, _, _, _, _, Seating).

% Check all filters
check_all_filters(_, []).
check_all_filters(Rest, [match(Pred,Val)|Fs]) :-
    matches(Rest, Pred, Val),
    check_all_filters(Rest, Fs).

% Current matches
current_matches(Filters, Matches) :-
    findall(R, (restaurant(R,_,_,_,_,_,_,_,_), check_all_filters(R, Filters)), Matches).

% Ask user input
ask_input(Prompt, Predicate, OldFilters, NewFilters, ErrorMsg) :-
    repeat,
    write(Prompt), nl,
    read(UserInput),
    (   UserInput == any ->
        NewFilters = OldFilters,
        current_matches(NewFilters, M),
        (M \= [] -> !; write(ErrorMsg), nl, fail)
    ;   is_list(UserInput) ; atom(UserInput) ->
        FiltersTry = [match(Predicate, UserInput)|OldFilters],
        current_matches(FiltersTry, M),
        (M \= [] -> NewFilters = FiltersTry, !; write(ErrorMsg), nl, fail)
    ;   write('Please provide a valid input.'), nl, fail
    ).

% Print single recommendation
print_single_restaurant([R]) :-
    write('Your recommended restaurant is: '), write(R), nl.

% Print all recommendations
print_all_restaurants([]).
print_all_restaurants([R|Rs]) :-
    write('- '), write(R), nl,
    print_all_restaurants(Rs).

% Main recommendation routine
get_recommendation :-
    Filters = [],
    ask_input('What type of cuisine are you looking for? (or "any"):', 
              matches_cuisine, Filters, F1,
              'No restaurants offer this cuisine.'),
    current_matches(F1, M1),
    (length(M1, 1) -> print_single_restaurant(M1) ;
     ask_input('What is your budget? (cheap/moderate/expensive or "any"):', 
               matches_price, F1, F2,
               'No restaurants match this price range.'),
     current_matches(F2, M2),
     (length(M2, 1) -> print_single_restaurant(M2) ;
      ask_input('How far are you willing to travel? (close/mid/far or "any"):', 
                matches_distance, F2, F3,
                'No restaurants are available at this distance.'),
      current_matches(F3, M3),
      (length(M3, 1) -> print_single_restaurant(M3) ;
       ask_input('What time of day will you be eating? (breakfast/lunch/dinner or "any"):', 
                 matches_time, F3, F4,
                 'No restaurants are available at this time.'),
       current_matches(F4, M4),
       (length(M4, 1) -> print_single_restaurant(M4) ;
        ask_input('Would you like a place that requires a reservation? (yes/no or "any"):', 
                  matches_reservation, F4, F5,
                  'No restaurants match your reservation preference.'),
        current_matches(F5, M5),
        (length(M5, 1) -> print_single_restaurant(M5) ;
         ask_input('What dietary options do you require? (e.g., [vegetarian] or "any"):', 
                   matches_dietary, F5, F6, 
                   'No restaurants meet your dietary requirements.'),
         current_matches(F6, M6),
         (length(M6, 1) -> print_single_restaurant(M6) ;
          ask_input('What payment method do you prefer? (credit_debit/cash or "any"):', 
                    matches_payment, F6, F7,
                    'No restaurants support this payment method.'),
          current_matches(F7, M7),
          (length(M7, 1) -> print_single_restaurant(M7) ;
           ask_input('What seating do you prefer? (indoor/outdoor or "any"):', 
                     matches_seating, F7, FFinal,
                     'No restaurants offer this seating option.'),
           current_matches(FFinal, MFinal),
           (  length(MFinal,1) -> print_single_restaurant(MFinal)
           ;  MFinal = [] ->
              write('Sorry, no restaurant matches your preferences.'), nl
           ;  write('Recommended Restaurants:'), nl, print_all_restaurants(MFinal)
           )
          )
         )
        )
       )
      )
      )
     ).

