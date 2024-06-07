import grpc
from concurrent import futures
import shopping_pb2
import shopping_pb2_grpc

import notifications_pb2_grpc
import notifications_pb2

from datetime import datetime, timedelta

import uuid

MARKET_HOST = 'localhost'
MARKET_PORT = 50051

class MarketService(shopping_pb2_grpc.MarketServicer):
    def __init__(self):
        self.items = {}
        self.notifications = []
        self.sellers = []
        self.last_item_id = 0
        self.rated = {}
        self.wishlist = {}
        self.subscribers = {}

    def RegisterSeller(self, request, context):
        # seller_info = {
        #     'address': context.peer(),
        #     'uuid': request.uuid
        # }
        # self.sellers[request.uuid] = seller_info
        self.sellers.append(request.uuid)
        print(f"Seller join request from {context.peer()}, uuid = {request.uuid}")
        return shopping_pb2.SellerRegisterResponse(success=True, message='Seller registered successfully', uuid=request.uuid)


    def AddItem(self, request, context):
        if request.uuid not in self.sellers:
            return shopping_pb2.AddItemResponse(message='FAIL: Get Registered First', id=-1)

        print(f"Add Item request from {context.peer()}")

        self.last_item_id += 1  
        item_id = self.last_item_id

        self.items[item_id] = {
            'name': request.item.name,
            'category': request.item.category,
            'price': request.item.price,
            'description': request.item.description,
            'quantity': request.item.quantity,
            'rating': 0, 
            'seller_id': request.item.seller_id,
            'seller_addr': request.item.seller_addr,
            'raters': 0,
        }
        return shopping_pb2.AddItemResponse(message='SUCCESS', id=item_id)

    #Has notification

    def UpdateItem(self, request, context):
        # Check if the seller is registered
        if request.item.seller_id not in self.sellers:
            return shopping_pb2.OperationResponse(message='FAIL: Get Registered First')

        # Check if the item exists
        item_id = request.item.id
        if item_id not in self.items:
            return shopping_pb2.OperationResponse(message='FAIL: Item not found')

        # Check if the seller owns the item
        item = self.items[item_id]
        if item['seller_id'] != request.item.seller_id:
            return shopping_pb2.OperationResponse(message='FAIL: Permission denied')

        # Update the item details
        item['price'] = request.item.price if request.item.price else item['price']
        item['quantity'] = request.item.quantity if request.item.quantity else item['quantity']
        
        notification = (f"Item ID: {item_id} has been updated. "
                        f"New Price: {item['price']}, Quantity: {item['quantity']}")

        # Notify all buyers who have wishlisted the item
        if item_id in self.wishlist:
                
            for buyer_addr in self.wishlist[item_id]:
                print ("Buyer Address ------------------------------------------------------------------>", buyer_addr)
                self.NotifyClientBuyer(buyer_addr, notification)

        return shopping_pb2.OperationResponse(message='SUCCESS: Item updated successfully')

        

    def DeleteItem(self, request, context):
    # Assuming request has fields `id` for item ID and `seller_uuid` for seller's unique identifier
        if request.seller_uuid not in self.sellers:
            return shopping_pb2.OperationResponse(message='FAIL: Get Registered First')

        if request.id in self.items:
            item = self.items[request.id]
            # Assuming each item dictionary has a 'seller_id' field for seller's unique identifier
            if item['seller_id'] == request.seller_uuid:
            # Optionally, further validate the seller's address or other credentials here
                del self.items[request.id]
                return shopping_pb2.OperationResponse(
                message=f"Item with ID {request.id} successfully deleted." )
            else:
                return shopping_pb2.OperationResponse(
                    message="Permission denied.")
        else:
            return shopping_pb2.OperationResponse(
                message="Item ID not found.")



    def ListItems(self, request, context):

        if request.seller_uuid not in self.sellers:
            error_response = shopping_pb2.SearchItemsResponse()
            error_response.message = 'FAILED: Get yourself registered first'
            error_response.items.extend([]) 
            return error_response

        try:
            print(f"Display Items request from {context.peer()} and uuid {request.seller_uuid}")
        
            response = shopping_pb2.SearchItemsResponse()

            for item_id, item in self.items.items():
                if item['seller_id'] == request.seller_uuid:
                    item_msg = shopping_pb2.Item(
                        id= item_id,
                        name=item['name'],
                        category=item['category'],
                        price=float(item['price']),  # Ensure this is a double as per .proto definition
                        description=item['description'],
                        quantity=int(item['quantity']),  # Ensure this is an int32
                        rating=float(item['rating']),  # Ensure this is a float
                        seller_addr=item['seller_addr'],
                        seller_id=item['seller_id'],
                    )
                    response.items.append(item_msg)
            response.message = "Here's the list of items that you aare selling"
            return response

        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error or raise a gRPC error


    #-----------------------------------------------------------------------------------------------------------------------------------------

    #BUYER side services
    def SearchItems(self, request, context):
    # Initialize the response
        response = shopping_pb2.SearchItemsResponse()

        # Normalize the input for case insensitive comparison
        search_name = request.name.lower().strip()
        search_category = request.category.lower().strip()

        # Filter items by name and/or category
        matching_items = []
        for item_id, item in self.items.items():
            name_matches = not search_name or search_name in item['name'].lower()
            category_matches = search_category == 'any' or item['category'].lower() == search_category
            if name_matches and category_matches:
                matching_items.append((item_id, item))

        if search_name and not matching_items:
            response.items.extend([]) 
            response.message = "Fail: No such item exists"
            return response

        if search_category != 'any' and not matching_items:
            response.items.extend([]) 
            response.message = "Fail: No items found in the given category"
            return response

        for item_id, item in matching_items:
            item_msg = shopping_pb2.Item(
                id=item_id,
                name=item['name'],
                category=item['category'],
                price=float(item['price']),
                description=item['description'],
                quantity=int(item['quantity']),
                rating=float(item['rating']),
                seller_addr=item['seller_addr'],
                seller_id=item['seller_id'],
            )
            response.items.append(item_msg)

        response.message = "Success: Here's the list of items or the item you requested"
        return response


    # Has notification
    def BuyItem(self, request, context):
        print(f"Buy request {request.quantity} of item {request.id}, from {request.buyer_addr}")
        if request.id in self.items:
            item = self.items[request.id]
            if item['quantity'] >= request.quantity:
                item['quantity'] -= request.quantity  # Update the quantity
                # Notify the seller about the sale
                notification = (f"An item you're selling has been bought:\n"
                    f"Item ID: {request.id}, Quantity Bought: {request.quantity}")
                self.NotifyClientSeller(item['seller_addr'], notification)  # Corrected parameter order
                return shopping_pb2.OperationResponse(message='SUCCESS')
            else:
                return shopping_pb2.OperationResponse(message='FAILED: Not enough stock available')
        else:
            return shopping_pb2.OperationResponse(message='FAILED: Invalid item ID')
        
    
    def AddToWishList(self, request, context):
        print(f"{request.buyer_addr} wants to add the item {request.id} to wishlist")
        
        # Check if the item exists
        if request.id in self.items:
            item = self.items[request.id]
            
            # Check if the buyer has already added this item to wishlist
            if context.peer() not in self.wishlist.get(request.id, set()):
                
                # Record buyer's wishlist
                if request.id not in self.wishlist:
                    self.wishlist[request.id] = set()
                self.wishlist[request.id].add(request.buyer_addr)
                
                return shopping_pb2.OperationResponse(message=f"Successfully added Item ID: {request.id} to wishlist")
            else:
                return shopping_pb2.OperationResponse(message='FAIL: Buyer has already added this item to wishlist')
        else:
            return shopping_pb2.OperationResponse(message='FAIL: Invalid item ID')


        
    def RateItem(self, request, context):
        print(f"{context.peer()} rated item {request.id} with {request.rating} stars.")
        
        # Check if the item exists
        if request.id in self.items:
            item = self.items[request.id]
            
            # Check if the buyer has already rated this item
            if context.peer() not in self.rated.get(request.id, {}):
                # Update item rating
                current_rating = item.get('rating', 0)
                current_raters = item.get('raters', 0)
                new_rating = ((current_rating * current_raters) + request.rating) / (current_raters + 1)
                item['rating'] = new_rating
                item['raters'] = current_raters + 1
                
                # Record buyer's rating
                if request.id not in self.rated:
                    self.rated[request.id] = {}
                self.rated[request.id][context.peer()] = request.rating
                
                return shopping_pb2.OperationResponse(message='SUCCESS')
            else:
                return shopping_pb2.OperationResponse(message='FAIL: Buyer has already rated this item')
        else:
            return shopping_pb2.OperationResponse(message='FAIL: Invalid item ID')

    #NOTIFICATIONS .........................................................................................   
        


    def NotifyClientBuyer(self, buyer_addr, notification):
        # Improved to manage channels efficiently
        channel = grpc.insecure_channel(buyer_addr)
        stub = notifications_pb2_grpc.BuyerNotificationsStub(channel)
        try:
            #deadline = datetime.now() + timedelta(seconds=10)
            notification_message = notifications_pb2.Notification(message=notification)
            response= stub.ReceiveNotification(notification_message, timeout=100000)#, deadline= deadline)
            if response.success:
                print(f"Notification sent to {buyer_addr} successfully.")
            else:
                print(f"Notification to {buyer_addr} was not acknowledged.")
        except grpc.RpcError as e:
            print(f"Failed to send notification to {buyer_addr}: {e.code()} - {e.details()}")
        finally:
            channel.close()  # Ensure the channel is closed after the operation


    def NotifyClientSeller(self, seller_addr, notification):
    # Create a gRPC channel to the seller's address
        with grpc.insecure_channel(seller_addr) as channel:
            # Create a stub for the SellerNotifications service
            stub = notifications_pb2_grpc.SellerNotificationsStub(channel)
            
            try:
                # Create the notification message
                notification = notifications_pb2.Notification(message=notification)
                
                #deadline = datetime.now() + timedelta(seconds=10)
                response = stub.ReceiveNotification(notification, timeout=1000000)#, deadline=deadline)
                
                if response.success:
                    print(f"Notification sent to seller at {seller_addr} successfully.")
                else:
                    print(f"Notification to seller at {seller_addr} was not acknowledged.")
            except grpc.RpcError as e:
                print(f"Failed to send notification to seller at {seller_addr}: {e.code()} - {e.details()}")



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    shopping_pb2_grpc.add_MarketServicer_to_server(MarketService(), server)
    try:
        server.add_insecure_port(f'{MARKET_HOST}:{MARKET_PORT}')
        server.start()
        print("Server started on port 50051.")
        server.wait_for_termination()
    except Exception as e:
        print(f"Failed to bind to port 50051: {e}")
        server.stop(0)

if __name__ == '__main__':
    serve()

