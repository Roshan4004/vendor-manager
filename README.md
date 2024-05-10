# API Documentation

## Register

This endpoint is used to create a user. The credentials provided here are required to generate a token later.

### Endpoint
- Method: POST
- URL: `http://127.0.0.1:8000/api/register`

### Request Body
- Content-Type: application/json

```json
{
    "username": "admin",
    "password": "admin",
    "email": "something@gmail.com"
}

```
## Token

This endpoint is used to obtain a token for "Token authorization".

### Endpoint
- Method: POST
- URL: `http://127.0.0.1:8000/api/login`

### Request Body
- Content-Type: application/json

```json
{
    "username": "admin",
    "password":

```

## Add Vendor

This request is used to add a new vendor. The vendor code provided must be unique.

### Endpoint
- Method: POST
- URL: `http://localhost:8000/api/vendors/`

### Headers
- Authorization: Token ENTER TOKEN HERE

### Request Body
- Content-Type: application/json

```json
{
    "name": "vendor1",
    "contact_details": "980000",
    "address": "New Delhi, India",
    "vendor_code": "v1"
}

```

### Response
```json
{
  "msg": "Data created"
}
```

## All Vendors

This method is used to retrieve a list of all vendors along with their data.

### Endpoint
- Method: GET
- URL: `http://localhost:8000/api/vendors/{vendor_id}`

### Headers
- Authorization: Token ENETR TOKEN HERE

### Parameters
- id (required): A valid ID is required for specific data. Otherwise, an exception is returned.
- If id is not sent, all vendor list is returned.

### Response
``` json 
[
  {
    "id": 1,
    "name": "vendor1",
    "contact_details": "980000",
    "address": "New Delhi, India",
    "vendor_code": "v1",
    "on_time_delivery_rate": 0,
    "quality_rating_avg": 0,
    "average_response_time": 0,
    "fulfillment_rate": 0
  }
]
```

## Update Vendor

This endpoint is used to update a vendor's details. A valid ID is required, otherwise an exception is returned.

### Endpoint
- Method: PUT
- URL: `http://localhost:8000/api/vendors/1`

### Headers
- Authorization: Token ENTER TOKEN HERE

### Request Body
- Content-Type: application/json

```json
{
    "id": 1,
    "name": "vendor1_changed",
    "contact_details": "9800000000",
    "address": "New Delhi, India____ChangedAddress",
    "vendor_code": "v1",
    "on_time_delivery_rate": 0.0,
    "quality_rating_avg": 0.0,
    "average_response_time": 0.0,
    "fulfillment_rate": 0.0
}
```

### Response

```json
{
  "msg": "Complete data updated"
}
```

## Delete Vendor

### Endpoint
- Method: DELETE
- URL: `http://localhost:8000/api/vendors/2`

### Headers
- Authorization: Token ENTER TOKEN HERE

## Add Purchase Order

This endpoint is used to create a purchase order for any vendor. The vendor's ID is required in the "vendor" field.

### Endpoint
- Method: POST
- URL: `http://localhost:8000/api/purchase_orders/`

### Headers
- Authorization: Token ENTER TOKEN HERE

### Request Body
- Content-Type: application/json

```json
{
    "po_number": "p3",
    "order_date": "2024-05-09 17:16:52.734505",
    "delivery_date": "2024-05-14 17:18:52.158786",
    "items": {
        "SHIRT": 1
    },
    "quantity": 4,
    "vendor": 1
}

```
### Response
```json
{
  "msg": "Data created"
}
```

## GET Get Purchase Orders

This endpoint is used to retrieve a list of all purchase orders.

### Endpoint
- Method: GET
- URL: `http://localhost:8000/api/purchase_orders`

### Headers
- Authorization: Token ENTER TOKEN HERE

### Response
```json
[
  {
    "id": 1,
    "po_number": "p1",
    "order_date": "2024-05-09T17:16:52.734505Z",
    "delivery_date": "2024-05-14T17:18:52.158786Z",
    "items": {
      "SHIRT": 1
    },
    "quantity": 4,
    "status": "pending",
    "quality_rating": 0,
    "issue_date": "2024-05-09T17:16:52.734505Z",
    "acknowledgment_date": null,
    "vendor": 1
  }
]
```

## POST Acknowledge Orders

This endpoint is used to acknowledge an order, typically from the vendor's side. The "acknowledgement_date" field is updated in the database, which is later used to calculate different metrics.

- Method: POST
- URL: `http://localhost:8000/api/purchase_orders/1/acknowledge/`

### Headers
- Authorization: Token ENTER TOKEN HERE

### Request Body
- Content-Type: application/json

```json
{
    "acknowledgment_date": ""
}

```
## PUT Update Purchase Order

This endpoint is used to update a purchase order. If the status is changed to "completed", the data cannot be updated in the future. Additionally, a signal is triggered and metrics are updated.

- Method: PUT
- URL: `http://localhost:8000/api/purchase_orders/1`

### Headers
- Authorization: Token ENTER TOKEN HERE

### Request Body
- Content-Type: application/json

```json
{
    "id": 1,
    "po_number": "p1",
    "order_date": "2024-05-09T17:16:52Z",
    "delivery_date": "2024-05-14T17:18:52Z",
    "items": {
        "SHIRT": 6
    },
    "quantity": 4,
    "status": "completed",
    "quality_rating": 0.0,
    "issue_date": "2024-05-10T02:30:34Z",
    "vendor": 1
}

```
## DELETE Delete Purchase Order

This endpoint is used to delete a purchase order.

- Method: DELETE
- URL: `http://localhost:8000/api/purchase_orders/2`

### Headers
- Authorization: Token ENTER TOKEN HERE

## GET History API

This endpoint is used to retrieve historical performance metrics for a vendor.

### Endpoint
- Method: GET
- URL: `http://localhost:8000/api/vendors/1/performance/`

### Headers
- Authorization: Token ENTER TOKEN HERE

### Response
``` json
{
    "id": 5,
    "date": "2024-05-10T02:52:38.465231Z",
    "on_time_delivery_rate": 1.0,
    "quality_rating_avg": 4.0,
    "average_response_time": -0.4,
    "fulfillment_rate": 1.0,
    "vendor": 1
}
```

