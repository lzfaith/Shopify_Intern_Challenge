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

## Implementing Restful services in Python and Flask

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
 
I will store our products and shopping_carts in a memory structrue. It runs the application is single thread and proccess. *It is inappropriate to develop it on a production web server, a proper databse setup must be used.*

 ```Python
products = {
    1: {
        'title': 'Apple',
        'price': 20,
        'inventory': 5,
    }
}

shopping_carts = {
    1: {
        'products': {1: 1, 3: 2}
    }
}
}
 ```
 
 To run application we have to execute web_api.py:
 ```
 FLASK_APP = web_api.py
FLASK_ENV = development
FLASK_DEBUG = 1
In folder D:/pythonFiles/Shopify_Challenge
D:\Anaconda3\envs\Shopify\python.exe -m flask run
 * Serving Flask app "web_api.py" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 347-854-976
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 ```

The __curl__ will be used for test web server, the command will be provided in each example. 
 ***

### Fetch one product or many products: 

#### Examples: 

* Fetch the list all products by the following command:
```bash
$ curl -i http://localhost:5000/api/v1.0/products
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 276
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:00:47 GMT

{
  "products": {
    "1": {
      "inventory": 5,
      "price": 20,
      "title": "Apple"
    },
    "2": {
      "inventory": 2,
      "price": 13,
      "title": "Bear"
    },
    "3": {
      "inventory": 0,
      "price": 100,
      "title": "Desk"
    }
  }
}

```

* Fetch one product by the following command：

```
$ curl -i http://localhost:5000/api/v1.0/products/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 83
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:14:41 GMT

{
  "product": {
    "inventory": 5,
    "price": 20,
    "title": "Apple"
  }
}
```

* Fetch the product with avaliable inventory, the following command: 
```bash
$ curl -i http://localhost:5000/api/v1.0/products?avaliable=true
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 191
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:29:40 GMT

{
  "products": {
    "1": {
      "inventory": 5,
      "price": 20,
      "title": "Apple"
    },
    "2": {
      "inventory": 2,
      "price": 13,
      "title": "Bear"
    }
  }
}
```

* Purchase the product with avalible inventory and the product with unavaliabel inventory by following command:

```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"purchase"}' http://localhost:5000/api/v1.0/products/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 102
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:35:46 GMT

{
  "product": {
    "inventory": 4,
    "price": 20,
    "title": "Apple"
  },
  "result": true
}


$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"purchase"}' http://localhost:5000/api/v1.0/products/3
HTTP/1.0 409 CONFLICT
Content-Type: application/json
Content-Length: 132
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:37:00 GMT

{
  "product": {
    "inventory": 0,
    "price": 100,
    "title": "Desk"
  },
  "reason": "out of stock",
  "result": false
}

```

***
### Shopping carts
####Example:

* Create Shopping cart with one or more products by following command:

```bash
$ curl -i -H "Content-Type: application/json" -X POST -d '{"products":{"1": 2, "2": 3}}' http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 126
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:43:14 GMT

{
  "result": true,
  "shopping_cart": {
    "products": {
      "1": 2,
      "2": 3
    }
  },
  "shopping_cart_id": 2
}
```

* Get the list of shopping carts by following command:
```bash
$ curl -i http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 265
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:45:25 GMT

{
  "shopping_carts": {
    "1": {
      "products": {
        "1": 1,
        "3": 2
      }
    },
    "2": {
      "products": {
        "1": 2,
        "2": 3
      }
    }
  }
}
```

* Get total price of shopping_cart with cart id by the following command:

```bash
$ curl -i http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 104
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:51:44 GMT

{
  "shopping_cart": {
    "products": {
      "1": 1,
      "3": 2
    }
  },
  "total_price": 220
}
```

* Delete the shopping cart with cart id by the following command:
```bash
$ curl -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 21
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:55:42 GMT

{
  "result": true
}

$ curl -i http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 186
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 02:55:55 GMT

{
  "shopping_carts": {
    "2": {
      "products": {
        "1": 2,
        "2": 3
      }
    }
  }
}
```

* add(1)/remove(-1) product(s) in shopping cart with cart id by following command:
```bash
$ curl -i http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 107
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 03:33:23 GMT

{
  "shopping_carts": {
    "1": {
      "products": {
        "1": 1,
        "3": 2
      }
    }
  }
}

$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"add_product", "products":{"1":-1}}' http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 85
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 03:33:34 GMT

{
  "result": true,
  "shopping_cart": {
    "products": {
      "3": 2
    }
  }
}

$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"add_product", "products":{"2":1}}' http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 100
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 03:34:36 GMT

{
  "result": true,
  "shopping_cart": {
    "products": {
      "2": 1,
      "3": 2
    }
  }
}
```

* Compelete shopping cart with purchasing, if the product with unavaliable inventory, it cannot be compeleted:
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"purchase"}' http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 51
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 03:36:09 GMT

{
  "reason": "out of stock",
  "result": false
}
```

* If the product with avaliable inventory, the process will finish and remove the shopping cart:
```bash
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"add_product", "products":{"3":-1}}' http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 85
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 03:41:27 GMT

{
  "result": true,
  "shopping_cart": {
    "products": {
      "1": 1
    }
  }
}
$ curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"purchase"}' http://localhost:5000/api/v1.0/shopping_carts/1
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 21
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 03:41:35 GMT

{
  "result": true
}
$ curl -i http://localhost:5000/api/v1.0/shopping_carts
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 27
Server: Werkzeug/0.14.1 Python/3.6.8
Date: Mon, 21 Jan 2019 03:41:39 GMT

{
  "shopping_carts": {}
}

```


 ***

#### Continuing....

1. Using proper set up database
2. Using lock to ensure syncrhonization
