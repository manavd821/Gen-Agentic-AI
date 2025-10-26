def print_name(name : str) -> str:
    print(f"🤖 AI: {name}")
    return {"status": "success", "message": "print successful"}

ticket_prices = {
    "london": 799,
    "paris": 899,
    "tokyo": 1400,
    "berlin": 499
}
def get_ticket_price(location : str):
    if location not in ticket_prices:
        return {'status' : 'not_found', 'message' : f'Ticket price for {location} not found.'}
    price = ticket_prices[location]
    return {'status' : 'success', 'message' : f'Ticket price for {location} is ${price}.'}