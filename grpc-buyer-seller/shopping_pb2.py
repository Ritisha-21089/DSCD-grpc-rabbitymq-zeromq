# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: shopping.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eshopping.proto\x12\x08shopping\"\xa0\x01\n\x04Item\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08\x63\x61tegory\x18\x03 \x01(\t\x12\r\n\x05price\x18\x04 \x01(\x01\x12\x13\n\x0b\x64\x65scription\x18\x05 \x01(\t\x12\x10\n\x08quantity\x18\x06 \x01(\x05\x12\x0e\n\x06rating\x18\x07 \x01(\x02\x12\x13\n\x0bseller_addr\x18\x08 \x01(\t\x12\x11\n\tseller_id\x18\t \x01(\t\"%\n\x15SellerRegisterRequest\x12\x0c\n\x04uuid\x18\x01 \x01(\t\"<\n\x0e\x41\x64\x64ItemRequest\x12\x1c\n\x04item\x18\x01 \x01(\x0b\x32\x0e.shopping.Item\x12\x0c\n\x04uuid\x18\x02 \x01(\t\"1\n\x11UpdateItemRequest\x12\x1c\n\x04item\x18\x01 \x01(\x0b\x32\x0e.shopping.Item\"4\n\x11ItemDeleteRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x13\n\x0bseller_uuid\x18\x02 \x01(\t\"\'\n\x10ListItemsRequest\x12\x13\n\x0bseller_uuid\x18\x01 \x01(\t\"4\n\x12SearchItemsRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08\x63\x61tegory\x18\x02 \x01(\t\"B\n\x0e\x42uyItemRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x10\n\x08quantity\x18\x02 \x01(\x05\x12\x12\n\nbuyer_addr\x18\x03 \x01(\t\"1\n\x0fWishListRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x12\n\nbuyer_addr\x18\x02 \x01(\t\"-\n\x0fRateItemRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0e\n\x06rating\x18\x02 \x01(\x05\"$\n\x11OperationResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\".\n\x0f\x41\x64\x64ItemResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\x05\"H\n\x16SellerRegisterResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0c\n\x04uuid\x18\x03 \x01(\t\"E\n\x13SearchItemsResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\x1d\n\x05items\x18\x02 \x03(\x0b\x32\x0e.shopping.Item2\x90\x05\n\x06Market\x12S\n\x0eRegisterSeller\x12\x1f.shopping.SellerRegisterRequest\x1a .shopping.SellerRegisterResponse\x12>\n\x07\x41\x64\x64Item\x12\x18.shopping.AddItemRequest\x1a\x19.shopping.AddItemResponse\x12\x46\n\nUpdateItem\x12\x1b.shopping.UpdateItemRequest\x1a\x1b.shopping.OperationResponse\x12\x46\n\nDeleteItem\x12\x1b.shopping.ItemDeleteRequest\x1a\x1b.shopping.OperationResponse\x12\x46\n\tListItems\x12\x1a.shopping.ListItemsRequest\x1a\x1d.shopping.SearchItemsResponse\x12J\n\x0bSearchItems\x12\x1c.shopping.SearchItemsRequest\x1a\x1d.shopping.SearchItemsResponse\x12@\n\x07\x42uyItem\x12\x18.shopping.BuyItemRequest\x1a\x1b.shopping.OperationResponse\x12G\n\rAddToWishList\x12\x19.shopping.WishListRequest\x1a\x1b.shopping.OperationResponse\x12\x42\n\x08RateItem\x12\x19.shopping.RateItemRequest\x1a\x1b.shopping.OperationResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'shopping_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ITEM']._serialized_start=29
  _globals['_ITEM']._serialized_end=189
  _globals['_SELLERREGISTERREQUEST']._serialized_start=191
  _globals['_SELLERREGISTERREQUEST']._serialized_end=228
  _globals['_ADDITEMREQUEST']._serialized_start=230
  _globals['_ADDITEMREQUEST']._serialized_end=290
  _globals['_UPDATEITEMREQUEST']._serialized_start=292
  _globals['_UPDATEITEMREQUEST']._serialized_end=341
  _globals['_ITEMDELETEREQUEST']._serialized_start=343
  _globals['_ITEMDELETEREQUEST']._serialized_end=395
  _globals['_LISTITEMSREQUEST']._serialized_start=397
  _globals['_LISTITEMSREQUEST']._serialized_end=436
  _globals['_SEARCHITEMSREQUEST']._serialized_start=438
  _globals['_SEARCHITEMSREQUEST']._serialized_end=490
  _globals['_BUYITEMREQUEST']._serialized_start=492
  _globals['_BUYITEMREQUEST']._serialized_end=558
  _globals['_WISHLISTREQUEST']._serialized_start=560
  _globals['_WISHLISTREQUEST']._serialized_end=609
  _globals['_RATEITEMREQUEST']._serialized_start=611
  _globals['_RATEITEMREQUEST']._serialized_end=656
  _globals['_OPERATIONRESPONSE']._serialized_start=658
  _globals['_OPERATIONRESPONSE']._serialized_end=694
  _globals['_ADDITEMRESPONSE']._serialized_start=696
  _globals['_ADDITEMRESPONSE']._serialized_end=742
  _globals['_SELLERREGISTERRESPONSE']._serialized_start=744
  _globals['_SELLERREGISTERRESPONSE']._serialized_end=816
  _globals['_SEARCHITEMSRESPONSE']._serialized_start=818
  _globals['_SEARCHITEMSRESPONSE']._serialized_end=887
  _globals['_MARKET']._serialized_start=890
  _globals['_MARKET']._serialized_end=1546
# @@protoc_insertion_point(module_scope)