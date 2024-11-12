import streamlit as st
import random

# Function to calculate the value of a hand
def calculate_hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        if card in ['J', 'Q', 'K']:
            value += 10
        elif card == 'A':
            value += 11
            aces += 1
        else:
            value += card
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Function to deal a card
def deal_card(deck):
    return deck.pop()

# Function to initialize the deck
def create_deck():
    deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A'] * 4
    random.shuffle(deck)
    return deck

# Streamlit app
def main():
    st.title("Advanced Blackjack Game with Card Counting")

    # Initialize session state variables if they don't exist
    if 'deck' not in st.session_state:
        st.session_state.deck = create_deck()
    if 'player_hand' not in st.session_state:
        st.session_state.player_hand = [deal_card(st.session_state.deck), deal_card(st.session_state.deck)]
    if 'dealer_hand' not in st.session_state:
        st.session_state.dealer_hand = [deal_card(st.session_state.deck), deal_card(st.session_state.deck)]
    if 'player_stands' not in st.session_state:
        st.session_state.player_stands = False
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'balance' not in st.session_state:
        st.session_state.balance = 1000  # Starting balance
    if 'current_bet' not in st.session_state:
        st.session_state.current_bet = 0
    if 'split_hands' not in st.session_state:
        st.session_state.split_hands = None
    if 'doubled_down' not in st.session_state:
        st.session_state.doubled_down = False
    if 'card_count' not in st.session_state:
        st.session_state.card_count = 0

    # Card counting system (Hi-Lo)
    def update_card_count(card):
        if card in [2, 3, 4, 5, 6]:
            st.session_state.card_count += 1
        elif card in [10, 'J', 'Q', 'K', 'A']:
            st.session_state.card_count -= 1

    # Update card count for initial hands
    if 'initial_card_count_updated' not in st.session_state:
        for card in st.session_state.player_hand + st.session_state.dealer_hand:
            update_card_count(card)
        st.session_state.initial_card_count_updated = True

    # Betting System
    if st.session_state.current_bet == 0:
        st.subheader("Place Your Bet")
        bet = st.number_input("Bet Amount", min_value=10, max_value=st.session_state.balance, step=10)
        if st.button("Place Bet"):
            st.session_state.current_bet = bet
            st.session_state.balance -= bet
            st.experimental_rerun()  # Force rerun after placing a bet

    # Display player and dealer hands
    st.subheader("Your Hand")
    st.write(st.session_state.player_hand)
    st.write(f"Total Value: {calculate_hand_value(st.session_state.player_hand)}")

    st.subheader("Dealer's Hand")
    if st.session_state.player_stands:
        st.write(st.session_state.dealer_hand)
        st.write(f"Total Value: {calculate_hand_value(st.session_state.dealer_hand)}")
    else:
        st.write([st.session_state.dealer_hand[0], '?'])

    # Player actions
    if not st.session_state.game_over and st.session_state.current_bet > 0:
        if not st.session_state.player_stands:
            if st.button("Hit"):
                new_card = deal_card(st.session_state.deck)
                st.session_state.player_hand.append(new_card)
                update_card_count(new_card)
                if calculate_hand_value(st.session_state.player_hand) > 21:
                    st.session_state.game_over = True
                    st.warning("You busted! Dealer wins.")
                st.experimental_rerun()  # Force rerun after hitting
            if st.button("Stand"):
                st.session_state.player_stands = True
                st.experimental_rerun()  # Force rerun after standing

            # Split Option
            if len(st.session_state.player_hand) == 2 and st.session_state.player_hand[0] == st.session_state.player_hand[1]:
                if st.button("Split"):
                    st.session_state.split_hands = [
                        [st.session_state.player_hand[0], deal_card(st.session_state.deck)],
                        [st.session_state.player_hand[1], deal_card(st.session_state.deck)]
                    ]
                    for hand in st.session_state.split_hands:
                        for card in hand:
                            update_card_count(card)
                    st.session_state.player_hand = st.session_state.split_hands[0]
                    st.experimental_rerun()  # Force rerun after splitting

            # Double Down Option
            if len(st.session_state.player_hand) == 2 and not st.session_state.doubled_down:
                if st.button("Double Down"):
                    st.session_state.balance -= st.session_state.current_bet
                    st.session_state.current_bet *= 2
                    new_card = deal_card(st.session_state.deck)
                    st.session_state.player_hand.append(new_card)
                    update_card_count(new_card)
                    st.session_state.doubled_down = True
                    st.session_state.player_stands = True
                    st.experimental_rerun()  # Force rerun after doubling down

        # Dealer's turn
        if st.session_state.player_stands:
            while calculate_hand_value(st.session_state.dealer_hand) < 17:
                new_card = deal_card(st.session_state.deck)
                st.session_state.dealer_hand.append(new_card)
                update_card_count(new_card)
            dealer_value = calculate_hand_value(st.session_state.dealer_hand)
            player_value = calculate_hand_value(st.session_state.player_hand)

            if dealer_value > 21:
                st.success("Dealer busted! You win!")
                st.session_state.balance += st.session_state.current_bet * 2
            elif dealer_value < player_value:
                st.success("You win!")
                st.session_state.balance += st.session_state.current_bet * 2
            elif dealer_value > player_value:
                st.warning("Dealer wins!")
            else:
                st.info("It's a tie!")
                st.session_state.balance += st.session_state.current_bet  # Return the bet in case of a tie
            st.session_state.game_over = True
            st.experimental_rerun()  # Force rerun after dealer's turn ends

    # Insurance Option
    if st.session_state.dealer_hand[0] == 'A' and not st.session_state.player_stands and st.session_state.current_bet > 0:
        if st.button("Insurance"):
            insurance_bet = st.session_state.current_bet / 2
            st.session_state.balance -= insurance_bet
            if calculate_hand_value(st.session_state.dealer_hand) == 21:
                st.success("Dealer has Blackjack! Insurance pays 2:1.")
                st.session_state.balance += insurance_bet * 3
            else:
                st.warning("Dealer does not have Blackjack. You lose the insurance bet.")
            st.experimental_rerun()  # Force rerun after insurance action

    # Display balance
    st.subheader("Your Balance")
    st.write(f"${st.session_state.balance}")

    # Display card counting information
    st.subheader("Card Counting Indicator (Educational Purpose)")
    if st.session_state.card_count > 0:
        st.write(f"Current Count: +{st.session_state.card_count} (Advantage to Player)")
    elif st.session_state.card_count < 0:
        st.write(f"Current Count: {st.session_state.card_count} (Advantage to Dealer)")
    else:
        st.write("Current Count: 0 (Neutral)")

    # Restart the game
    if st.session_state.game_over:
        if st.button("Play Again"):
            st.session_state.deck = create_deck()
            st.session_state.player_hand = [deal_card(st.session_state.deck), deal_card(st.session_state.deck)]
            st.session_state.dealer_hand = [deal_card(st.session_state.deck), deal_card(st.session_state.deck)]
            st.session_state.player_stands = False
            st.session_state.game_over = False
            st.session_state.current_bet = 0
            st.session_state.split_hands = None
            st.session_state.doubled_down = False
            st.session_state.card_count = 0
            st.session_state.initial_card_count_updated = False
            st.experimental_rerun()  # Force rerun after restarting the game

if __name__ == "__main__":
    main()
