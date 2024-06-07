import grpc
import threading
import shopping_pb2
import shopping_pb2_grpc
import uuid
import notifications_pb2_grpc
import notifications_pb2
from concurrent import futures

# Global variables for host addresses
MARKET_HOST = 'localhost' # '34.131.233.220'
MARKET_PORT = 50051
SELLER_HOST = '[::1]'#'103.25.231.102'
SELLER_PORT = 50055

# Define a new servicer for the SellerServer
class SellerServer(notifications_pb2_grpc.SellerNotificationsServicer):
    def __init__(self):
        self.notifications = []

    def ReceiveNotification(self, request, context):
        print(f"Received notification: {request.message}")
        return notifications_pb2.NotificationAck(success=True)

def start_seller_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notifications_pb2_grpc.add_SellerNotificationsServicer_to_server(SellerServer(), server)
    server.add_insecure_port(f'{SELLER_HOST}:{SELLER_PORT}')
    server.start()
    server.wait_for_termination()

class SellerClient:
    def __init__(self, market_host, market_port, seller_host, seller_port):
        self.market_host = market_host
        self.market_port = market_port
        self.seller_host = seller_host
        self.seller_port = seller_port
        self.market_channel = grpc.insecure_channel(f'{market_host}:{market_port}')
        self.stub = shopping_pb2_grpc.MarketStub(self.market_channel)
        self.address = f'{seller_host}:{seller_port}'
        self.uuid = str(uuid.uuid1())

    def register_seller(self):
        response = self.stub.RegisterSeller(shopping_pb2.SellerRegisterRequest(uuid=self.uuid))
        print(response.message)

    def post_new_item(self, name, category, price, quantity, description):
        category = category.lower()
        if category not in ['electronics', 'fashion']:
            category = 'others'

        item = shopping_pb2.Item(
            name=name,
            category=category,
            price=price,
            quantity=quantity,
            description=description,
            seller_id=self.uuid,
            seller_addr=self.address
        )
        response = self.stub.AddItem(shopping_pb2.AddItemRequest(item=item, uuid=self.uuid))
        print(response.message)
        print("Item ID: ", response.id)

    def update_item(self, item_id, price, quantity):
        item_update = shopping_pb2.Item(
            id=item_id,
            price=price,
            quantity=quantity,
            seller_id=self.uuid,
        )
        response = self.stub.UpdateItem(shopping_pb2.UpdateItemRequest(item=item_update))
        print(response.message)

    def delete_item(self, item_id):
        response = self.stub.DeleteItem(shopping_pb2.ItemDeleteRequest(id=item_id, seller_uuid=self.uuid))
        print(response.message)

    def display_seller_items(self):
        responses = self.stub.ListItems(shopping_pb2.ListItemsRequest(seller_uuid=self.uuid))
        print(responses.message)
        
        for item in responses.items:
            print(f"Item ID: {item.id}, Name: {item.name}, Price: {item.price}, Category: {item.category},")
            print(f"Description: {item.description}")
            print(f"Quantity Remaining: {item.quantity}")
            print(f"Seller: {item.seller_addr}")
            print(f"Rating: {item.rating} / 5")
            print("-----")  # Separator between items

    def user_interface(self):
        while True:
            print("\nChoose an action:")
            print("1) Register as Seller")
            print("2) Sell Item")
            print("3) Update Item")
            print("4) Delete Item")
            print("5) Display Items")
            print("0) Exit")
            choice = input("Enter the number of your choice: ")

            if choice == "1":
                self.register_seller()
            elif choice == "2":
                name = input("Enter item name: ")
                category = input("Enter item category: ").lower()
                price = float(input("Enter item price: "))
                quantity = int(input("Enter item quantity: "))
                description = input("Enter item description: ")
                self.post_new_item(name, category, price, quantity, description)
            elif choice == "3":
                item_id = int(input("Enter item ID to update: "))
                price = float(input("Enter new item price: "))
                quantity = int(input("Enter new item quantity: "))
                self.update_item(item_id, price, quantity)
            elif choice == "4":
                item_id = int(input("Enter item ID to delete: "))
                self.delete_item(item_id)
            elif choice == "5":
                self.display_seller_items()
            elif choice == "0":
                print("Exiting...")
                break
            else:
                print("Invalid choice, please try again.")

if __name__ == '__main__':

    server_thread = threading.Thread(target=start_seller_server, daemon=True)
    server_thread.start()

    seller = SellerClient(market_host = MARKET_HOST, market_port= MARKET_PORT, seller_host = SELLER_HOST, seller_port= SELLER_PORT)
    seller.user_interface()
