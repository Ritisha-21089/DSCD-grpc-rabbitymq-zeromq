# README

## Part 1: Using gRPC to Implement an Online Shopping Platform

### Overview
The shopping platform consists of three main components:
- **Market (Central Platform):** Connects sellers and buyers, maintaining all data related to items, transactions, notifications, and user accounts.
- **Seller:** Interacts with the Market to manage items and transactions.
- **Buyer:** Interacts with the Market to search and purchase items.

All components communicate via gRPC using protocol buffers (protos). Each component resides on different virtual machines on Google Cloud.

### Components

#### Market (Central Platform)
- Maintains seller accounts, items, transaction logs, reviews, and notifications.
- Known IP:Port address for communication with sellers and buyers.

#### Seller (Client)
- Manages items and transactions through the Market.
- Hosted at a specific IP:Port address.
- Uses a UUID for secure transactions.

#### Buyer (Client)
- Searches and purchases items through the Market.
- Hosted at a specific IP:Port address.
- Can wishlist items for notifications.

### RPC Implementation

#### Seller to Market

- **RegisterSeller**
  - Request: Seller’s address (IP:Port) and UUID.
  - Response: SUCCESS or FAILED.
  - Market prints: `Seller join request from <IP:Port>, uuid = <UUID>`
  - Seller prints: SUCCESS or FAIL

- **SellItem**
  - Request: Item details (name, category, quantity, description, price, UUID).
  - Response: SUCCESS or FAILED.
  - Market prints: `Sell Item request from <IP:Port>`
  - Seller prints: SUCCESS or FAIL

- **UpdateItem**
  - Request: Item ID, new price, new quantity, seller address, UUID.
  - Response: SUCCESS or FAILED.
  - Market prints: `Update Item <Item ID> request from <IP:Port>`
  - Seller prints: SUCCESS or FAIL

- **DeleteItem**
  - Request: Item ID, seller address, UUID.
  - Response: SUCCESS or FAILED.
  - Market prints: `Delete Item <Item ID> request from <IP:Port>`
  - Seller prints: SUCCESS or FAIL

- **DisplaySellerItems**
  - Request: Seller address, UUID (optional).
  - Response: List of items.
  - Market prints: `Display Items request from <IP:Port>`
  - Seller prints: List of items with details

#### Buyer to Market

- **SearchItem**
  - Request: Item name (can be empty), category.
  - Response: List of matching items.
  - Market prints: `Search request for Item name: <Item name>, Category: <Category>`
  - Buyer prints: List of items with details

- **BuyItem**
  - Request: Item ID, quantity, buyer address (IP:Port).
  - Response: SUCCESS or FAILED.
  - Market prints: `Buy request <quantity> of item <Item ID>, from <IP:Port>`
  - Buyer prints: SUCCESS or FAIL

- **AddToWishList**
  - Request: Item ID, buyer address (IP:Port).
  - Response: SUCCESS or FAILED.
  - Market prints: `Wishlist request of item <Item ID>, from <IP:Port>`
  - Buyer prints: SUCCESS or FAIL

- **RateItem**
  - Request: Item ID, buyer address, rating (1-5).
  - Response: SUCCESS or FAILED.
  - Market prints: `<IP:Port> rated item <Item ID> with <rating> stars.`
  - Buyer prints: SUCCESS or FAIL

#### Market to Buyer/Seller

- **NotifyClient**
  - Triggers on item updates or purchases.
  - Notification message contains updated item details.
  - Buyer/Seller prints: Updated item details.

---

## Part 2: Using ZeroMQ to Build a Low-Level Group Messaging Application

### Overview
This messaging application consists of a central messaging server, groups, and users. The server maintains the group list, while groups handle user interactions and message storage.

### Components

#### Messaging App Server
- Maintains a list of groups with their IP addresses.
- Handles user requests for group lists.

#### Groups
- Manages user memberships and messages.
- Stores messages with timestamps.

#### Users
- Can join/leave groups and send/receive messages.
- Can fetch messages based on a timestamp.

### Node Interactions

#### Message Server to Group

- **Register Group**
  - Request: Group name, IP address.
  - Response: SUCCESS.
  - Server prints: `JOIN REQUEST FROM <IP:Port>`
  - Group prints: SUCCESS

#### User to Message Server

- **GetGroupList**
  - Request: List of groups.
  - Response: List of group names and IP addresses.
  - Server prints: `GROUP LIST REQUEST FROM <IP:Port>`
  - User prints: List of groups

#### User to Group

- **joinGroup**
  - Request: User UUID.
  - Response: SUCCESS.
  - Group prints: `JOIN REQUEST FROM <UUID>`
  - User prints: SUCCESS

- **LeaveGroup**
  - Request: User UUID.
  - Response: SUCCESS.
  - Group prints: `LEAVE REQUEST FROM <UUID>`
  - User prints: SUCCESS

- **GetMessage**
  - Request: Timestamp (optional).
  - Response: List of messages.
  - Group prints: `MESSAGE REQUEST FROM <UUID>`
  - User prints: List of messages

- **SendMessage**
  - Request: Message content, user UUID.
  - Response: SUCCESS or FAILED.
  - Group prints: `MESSAGE SEND FROM <UUID>`
  - User prints: SUCCESS or FAIL

---

## Part 3: Building a YouTube-like Application with RabbitMQ

### Overview
This simplified YouTube application uses RabbitMQ for messaging. The system has three components:
- **YouTuber:** Publishes videos.
- **User:** Subscribes to YouTubers and receives notifications.
- **YouTubeServer:** Manages data and processes messages from YouTubers and Users.

### Components

#### YouTubeServer.py

- **consume_user_requests()**
  - Consumes login and subscription/unsubscription requests.
  - Prints user login and subscription updates.

- **consume_youtuber_requests()**
  - Consumes video upload requests.
  - Prints video upload notifications.

- **notify_users()**
  - Sends notifications to subscribers.

Example:
```sh
$ python youtubeServer.py
```

#### Youtuber.py

- **publishVideo(youtuber, videoName)**
  - Publishes a video to the YouTube server.
  - Prints SUCCESS message.

Example:
```sh
$ python Youtuber.py TomScott "After ten years, it's time to stop weekly videos."
```

#### User.py

- **updateSubscription(user, action, youtuber)**
  - Sends subscription/unsubscription request to the YouTube server.
  - Prints SUCCESS message.

- **receiveNotifications(user)**
  - Receives notifications for subscribed YouTubers.

Examples:
```sh
$ python User.py username s TomScott
$ python User.py username u TomScott
$ python User.py username
```

### Flow of Service
1. Run `YoutubeServer.py` to start the server.
2. Run `Youtuber.py` and `User.py` multiple times and simultaneously.
3. Users receive real-time notifications when subscribed YouTubers upload new videos.
