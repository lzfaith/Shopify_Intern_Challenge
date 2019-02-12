# Shopify_Intern_Challenge

* __Task__: Build the barebones of an online marketplace.<br/>

* Build a server side web api that can be used to fetch products either one at a time or all at once.<br/>

* Querying for all products should support passing an argument to only return products with avaliable inventory.<br/>

* Products should be able to be "purchased" which should reduce the inventory by 1.<br/>

*__Extra credit__*:

* Fit these product purchase into the context of a simple shopping cart.<br/>

* create a cart -> adding products to the cart -> completing the cart<br/>

* The cart should contain a list of all included products, a total dollar amount(the total value of all products), and product inventory shouldn't reduce until after a cart has been completed.

***

## Implementing Restful services in Python and Flask:

##### The products and shopping_carts will used HTTP methods as follow:
|  HTTP Method  |  URl  |  Examples  |
|:-------------:|:--------:|:----------:|
|      GET      |  http://[hostname]/api/v1.0/products?avaliable=True |  Retrieve  list of products with avaliable inventory |
|      GET      |  http://[hostname]/api/v1.0/products/[product_id]  | Retrieve a product                 |
|      GET      |  http://[hostname]/api/v1.0/shopping_carts         | Retrieve a list of shopping_carts  |
|      GET      |  http://[hostname]/api/v1.0/shopping_carts/[cart_id]  | Retrieve a shopping_cart id and the total value of products
|      PUT      |  http://[hostname]/api/v1.0/products/[product_id]  | Update an existing product |
|      PUT      |  http://[hostname]/api/v1.0/shopping_carts/[card_id]  | Update an existing shopping_cart |
|     POST      |  http://[hostname]/api/v1.0/shopping_carts          | Create a new Shopping_cart |
|    DELETE     |  http://[hostname]/api/v1.0/shopping_carts/[cart_id]          | Delete a shopping_cart |
 
## Database:

* The Sqlite will be applied


|  Table  |    |    |   |     |     |   
|:-------------:|:--------:|:----------:|:----------:|:----------:|:----------:|
|      product      |  id(primary)  |  title  |  price  |  inventory  |  relationships <br/>  __relationship('Relationship', backref='product', primaryjoin=id == Relationship.product_id)__  |
|      shoppingcart  |  id(primary)  |  relationships <br/>  __relationship('Relationship', backref='product', primaryjoin=id == Relationship.shoppingcart_id)__  | 
|      product_shoppingcart   |    shoppingcart_id(primary) <br/> __ForeignKey('product.id')__     |     product_id(primary) <br/> __ForeignKey('shoppingcart.id')__     |     quantity    | 


 ***


## Testing:

The __curl__ will be used for test web server, the command will be provided in each example


### Fetch one product or many products: 

#### Examples: 

* Fetch the list all products by the following command:
```bash
$ curl -i http://localhost:5000/api/v1.0/products
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 316
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 05:16:53 GMT

{
  "products": [
    {
      "id": 1,
      "inventory": 5,
      "price": 30.0,
      "title": "Apple"
    },
    {
      "id": 2,
      "inventory": 1,
      "price": 20.0,
      "title": "Bear"
    },
    {
      "id": 3,
      "inventory": 0,
      "price": 10.0,
      "title": "Orange"
    }
  ]
}
```

* Fetch one product by the following command：

```
$ curl -i http://localhost:5000/api/v1.0/products/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 99
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 05:14:36 GMT

{
  "product": {
    "id": 1,
    "inventory": 5,
    "price": 30.0,
    "title": "Apple"
  }
}
```

* Fetch the product with avaliable inventory, the following command: 
```bash
$ curl -i http://localhost:5000/api/v1.0/products?avaliable=true
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 217
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 05:17:53 GMT

{
  "products": [
    {
      "id": 1,
      "inventory": 5,
      "price": 30.0,
      "title": "Apple"
    },
    {
      "id": 2,
      "inventory": 1,
      "price": 20.0,
      "title": "Bear"
    }
  ]
}
```

* Purchase the product with avalible inventory and the product with unavaliabel inventory by following command:

```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"purchase"}' http://localhost:5000/api/v1.0/products/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 118
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:26:49 GMT

{
  "product": {
    "id": 1,
    "inventory": 4,
    "price": 30.0,
    "title": "Apple"
  },
  "result": true
}

# if the inventory is zero, then it will show its out of stock
curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"purchase"}' http://localhost:5000/api/v1.0/products/3
HTTP/1.0 409 CONFLICT
Content-Type: application/json
Content-Length: 149
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:27:51 GMT

{
  "product": {
    "id": 3,
    "inventory": 0,
    "price": 10.0,
    "title": "Orange"
  },
  "reason": "out of stock",
  "result": false
}
```

***
### Shopping carts
#### Examples:

* Create Shopping cart with one or more products by following command:

```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"products":{"1": 2, "2": 3}}' http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 114
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:29:56 GMT

{
  "result": true,
  "shopping_cart": {
    "id": 1,
    "products": {
      "1": 2,
      "2": 3
    }
  }
}

# if the product is not exist, it will show unknown product
curl -i -H "Content-Type: application/json" -X POST -d '{"products":{"4": 2}}' http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 409 CONFLICT
Content-Type: application/json
Content-Length: 56
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:30:59 GMT

{
  "reason": "Unknown product 4",
  "result": false
}
```

* Get the list of shopping carts by following command <br/> 
* Get shopping cart by cart id:
```bash
$ curl -i http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 191
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:32:26 GMT

{
  "shopping_carts": [
    {
      "id": 1,
      "products": {
        "1": 2,
        "2": 3
      }
    },
    {
      "id": 2,
      "products": {
        "3": 1
      }
    }
  ]
}

curl -i http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 95
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:33:02 GMT

{
  "shopping_cart": {
    "id": 1,
    "products": {
      "1": 2,
      "2": 3
    }
  }
}
```


* Remove the shopping cart by cart id by the following command:
```bash
$ curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 21
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:36:01 GMT

{
  "result": true
}

# After remove the shopping card #1, then it only left the shopping cart #2
$ curl -i http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 101
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:36:18 GMT

{
  "shopping_carts": [
    {
      "id": 2,
      "products": {
        "3": 1
      }
    }
  ]
}
```

* Add(1)/remove(-1) product(s) in shopping cart with cart id by following command:
```bash
# Add one apple into the shopping card
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"add_product", "products":{"1":1}}' http://localhost:5000/api/v1.0/shopping_carts/2
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 114
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:38:57 GMT

{
  "result": true,
  "shopping_cart": {
    "id": 2,
    "products": {
      "1": 1,
      "3": 1
    }
  }
}

# Remove one orange in shopping card #2
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"add_product", "products":{"3":-1}}' http://localhost:5000/api/v1.0/shopping_carts/2
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 99
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Tue, 12 Feb 2019 06:41:02 GMT

{
  "result": true,
  "shopping_cart": {
    "id": 2,
    "products": {
      "1": 1
    }
  }
}
```

 ***

#### Continuing....

1. Purchase all products in shopping cart
