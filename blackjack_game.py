import random
import asyncio
from discord import TextChannel, Client

# Card and deck setup
BASE_DECK = [
    ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6), ('7', 7), ('8', 8), ('9', 9), ('10', 10), ('J', 10), ('Q', 10), ('K', 10), ('A', 11)
]

def shuffle_deck():
    """Creates and shuffles a fresh deck of cards"""
    deck = BASE_DECK * 4  # Full 52-card deck (4 suits)
    random.shuffle(deck)
    return deck


def calculate_hand(hand):
    """Calculates the total value of a hand"""
    total = sum(card[1] for card in hand)
    ace_count = sum(1 for card in hand if card[0] == 'A')
    while total > 21 and ace_count:
        total -= 10
        ace_count -= 1
    return total


async def blackjack(bot: Client, channel: TextChannel) -> None:
    """Handles a complete blackjack game session in a Discord text channel"""
    deck = shuffle_deck()
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    player_total = calculate_hand(player_hand)
    dealer_total = calculate_hand(dealer_hand)

    # Show initial hands (dealer's second card is hidden)
    await channel.send(f"🃏 **Your hand:** {player_hand}, Total: {player_total}")
    await channel.send(f"🃏 **Dealer's hand:** [{dealer_hand[0]}, ('?', ?)]")

    # Player's turn
    while player_total < 21:
        await channel.send("💬 **Do you want to 'hit' or 'stand'?**")

        try:
            def check(msg):
                return msg.channel == channel and msg.author != bot.user and msg.content.lower() in ['hit', 'stand']

            msg = await bot.wait_for('message', timeout=30.0, check=check)
            action = msg.content.lower()

            if action == 'hit':
                card = deck.pop()
                player_hand.append(card)
                player_total = calculate_hand(player_hand)
                await channel.send(f"🃏 **You drew:** {card}, Total: {player_total}")
            elif action == 'stand':
                break

        except asyncio.TimeoutError:
            await channel.send("⏳ You took too long to respond. Game over!")
            return

    # Check for immediate player bust
    if player_total > 21:
        await channel.send(f"💥 **Bust!** You lose. Your total was {player_total}.")
        return

    # Dealer's turn
    await channel.send(f"🃏 **Dealer's full hand:** {dealer_hand}, Total: {dealer_total}")
    while dealer_total < 17:
        card = deck.pop()
        dealer_hand.append(card)
        dealer_total = calculate_hand(dealer_hand)
        await channel.send(f"🃏 **Dealer drew:** {card}, Total: {dealer_total}")

    # Final result
    if dealer_total > 21:
        await channel.send(f"🎉 **Dealer busts! You win!** Your total: {player_total}, Dealer's total: {dealer_total}")
    elif player_total > dealer_total:
        await channel.send(f"🎉 **You win!** Your total: {player_total}, Dealer's total: {dealer_total}")
    elif player_total < dealer_total:
        await channel.send(f"😢 **Dealer wins!** Your total: {player_total}, Dealer's total: {dealer_total}")
    else:
        await channel.send(f"🤝 **It's a tie!** Your total: {player_total}, Dealer's total: {dealer_total}")
