import grpc
import threading
import shopping_pb2
import shopping_pb2_grpc
import notifications_pb2_grpc
import notifications_pb2
from concurrent import futures

# Global variables for host and port configuration
MARKET_HOST = 'localhost'#'34.131.233.220'
MARKET_PORT = 50051
BUYER_HOST = '[::1]'
BUYER_PORT = 50053  # Port for the BuyerServer

# Define a new servicer for the BuyerClient
class BuyerServer(notifications_pb2_grpc.BuyerNotificationsServicer):
    def __init__(self):
        self.notifications = []

    def ReceiveNotification(self, request, context):
        print(f"Received notification: {request.message}")
        return notifications_pb2.NotificationAck(success=True)
    
def start_buyer_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notifications_pb2_grpc.add_BuyerNotificationsServicer_to_server(BuyerServer(), server)
    server.add_insecure_port(f'{BUYER_HOST}:{BUYER_PORT}')
    server.start()
    server.wait_for_termination()

class BuyerClient:
    def __init__(self, market_host, market_port, buyer_host, buyer_port):
        self.market_host = market_host
        self.market_port = market_port
        self.market_channel = grpc.insecure_channel(f'{market_host}:{market_port}')
        self.stub = shopping_pb2_grpc.MarketStub(self.market_channel)
        self.address = f'{BUYER_HOST}:{BUYER_PORT}'  # Address including the BuyerServer port

    def search_items(self, item_name, category):

        if category not in ('electronics', 'fashion', 'others') or category == '':
            category = "any"

        response = self.stub.SearchItems(shopping_pb2.SearchItemsRequest(name=item_name, category=category))

        print(response.message)
        for item in response.items:
            print(f"Item ID: {item.id}, Name: {item.name}, Price: {item.price}, Category: {item.category},")
            print(f"Description: {item.description}")
            print(f"Quantity Remaining: {item.quantity}")
            print(f"Seller: {item.seller_addr}")
            print(f"Rating: {item.rating} / 5")
            print("-----")  # Separator between items
            # Separator between items


    def buy_item(self, item_id, quantity):
        response = self.stub.BuyItem(shopping_pb2.BuyItemRequest(id=item_id, quantity=quantity, buyer_addr=self.address))
        print(response.message)

    def add_to_wishlist(self, item_id):
        response = self.stub.AddToWishList(shopping_pb2.WishListRequest(id=item_id, buyer_addr=self.address))
        print(response.message)

    def rate_item(self, item_id, rating):
        response = self.stub.RateItem(shopping_pb2.RateItemRequest(id=item_id, rating=rating))
        print(response.message)


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_buyer_server, daemon=True)
    server_thread.start()

    buyer = BuyerClient(market_host=MARKET_HOST, market_port=MARKET_PORT, buyer_host = BUYER_HOST, buyer_port=BUYER_PORT)
    print(f"Buyer address: {buyer.address}")
    
    while True:
        print("\n1. Search Items")
        print("2. Buy Item")
        print("3. Add to Wishlist")
        print("4. Rate Item")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            item_name = input("Enter item name (press Enter to skip): ")
            category = input("Enter item category (press Enter to skip): ")
            if item_name == '' and category == '':
                category = 'any'
            buyer.search_items(item_name=item_name, category=category)
        elif choice == '2':
            item_id = int(input("Enter item ID: "))
            quantity = input("Enter quantity: ")
            buyer.buy_item(item_id= item_id, quantity=int(quantity))
        elif choice == '3':
            item_id = int(input("Enter item ID: "))
            buyer.add_to_wishlist(item_id=int(item_id))
        elif choice == '4':
            item_id = int(input("Enter item ID: "))
            rating = int(input("Enter rating (1-5): "))
            if rating > 5:
                rating = 5
            if rating <= 0:
                rating = 1
            buyer.rate_item(item_id=int(item_id), rating=int(rating))
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")




    
    







