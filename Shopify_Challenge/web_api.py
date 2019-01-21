from flask import Flask, jsonify, abort, request

app = Flask(__name__)

products = {
    1: {
        'title': 'Apple',
        'price': 20,
        'inventory': 5,
    },
    2: {
        'title': 'Bear',
        'price': 13,
        'inventory': 2,
    },
    3: {
        'title': 'Desk',
        'price': 100,
        'inventory': 0,
    }
}

shopping_carts = {
    1: {
        'products': {1: 1, 3: 2}
    }
}


@app.route('/api/v1.0/products', methods=['GET'])
def get_products():
    only_available = request.args.get('avaliable', 'false')
    if only_available == 'true':
        return jsonify({'products': dict((product_id, product) for product_id, product in products.items() if product['inventory'] > 0)})
    else:
        return jsonify({'products': products})


@app.route('/api/v1.0/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    if product_id not in products:
        abort(404)
    return jsonify({'product': products[product_id]})


@app.route('/api/v1.0/products/<int:product_id>', methods=['PUT'])
def purchase_product(product_id):
    if product_id not in products:
        abort(404)
    if not request.json:
        abort(400)
    if 'action' in request.json and type(request.json['action']) is not str:
        abort(400)
    if request.json['action'] == 'purchase':
        if products[product_id]['inventory'] > 0:
            products[product_id]['inventory'] -= 1
            return jsonify({'result': True, 'product': products[product_id]})
        else:
            return jsonify({'result': False, 'reason': 'out of stock', 'product': products[product_id]}), 409
    else:
        abort(400)


# create a cart which contains one or more pruducts
# request content: {'products': {123: 1, 456: 2}}
@app.route('/api/v1.0/shopping_carts', methods=['POST'])
def create_shopping_cart():
    if not request.json or not 'products' in request.json or type(request.json['products']) is not dict:
        return jsonify({'result': False, 'reason': 'no key "products" as dict'}), 400
    if len(request.json['products']) == 0:
        return jsonify({'result': False, 'reason': 'Shopping cart should contain at least one product'}), 409
    for product_id, quantity in request.json['products'].items():
        if type(product_id) is not str:
            return jsonify({'result': False, 'reason': 'product_id is not str'}), 400
        if not product_id.isdigit():
            return jsonify({'result': False, 'reason': 'int(product_id) failed'}), 400
        product_id = int(product_id)
        if type(quantity) is not int:
            return jsonify({'result': False, 'reason': 'quantity is not int'}), 400
        if quantity <= 0:
            return jsonify({'result': False, 'reason': 'quantity must be greater than zero'}), 409
        if product_id not in products:
            return jsonify({'result': False, 'reason': 'Unknown product %d' % product_id}), 409

    cart_id = max(shopping_carts.keys(), default = 0) + 1
    shopping_carts[cart_id] = {'products': request.json['products']}
    return jsonify({'result': True, 'shopping_cart_id': cart_id, 'shopping_cart': shopping_carts[cart_id]}), 201


# get all shopping_carts
@app.route('/api/v1.0/shopping_carts', methods=['GET'])
def get_shopping_carts():
    return jsonify({'shopping_carts': shopping_carts})


# get all products in cart
# response content: {'id': uri, 'products': [...]}
@app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['GET'])
def get_shopping_cart(cart_id):
    if cart_id not in shopping_carts:
        abort(404)

    total_price = 0
    for product_id, quantity in shopping_carts[cart_id]['products'].items():
        total_price += products[product_id]['price'] * quantity
    return jsonify({'shopping_cart': shopping_carts[cart_id], 'total_price': total_price})


# delete a cart
@app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['DELETE'])
def remove_shopping_cart(cart_id):
    if cart_id not in shopping_carts:
        abort(404)
    else:
        del shopping_carts[cart_id]
        return jsonify({'result': True})


# 1. add/remove product(s) to cart, request content: {'action':'add_product', 'products': {123: 1, 345: -1}]}
# 3. purchase all products in cart, request content: {'action':'purchase'}
#    if purchase success, cart should be removed
#    update the inventory of products
# @app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['PUT'])

@app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['PUT'])
def add_item_shopping_cart(cart_id):
    if cart_id not in shopping_carts:
        abort(404)
    if 'action' not in request.json or type(request.json['action']) is not str:
        abort(400)

    if request.json['action'] == 'add_product':
        if not request.json or 'products' not in request.json or type(request.json['products']) is not dict:
            return jsonify({'result': False, 'reason': 'no key "products" as dict'}), 400
        if len(request.json['products']) == 0:
            return jsonify({'result': False, 'reason': 'It should contain one when adding item in shopping cart'}), 409
        for product_id, quantity in request.json['products'].items():
            if type(product_id) is not str:
                return jsonify({'result': False, 'reason': 'product_id is not str'}), 400
            if not product_id.isdigit():
                return jsonify({'result': False, 'reason': 'int(product_id) failed'}), 400
            product_id = int(product_id)
            if product_id not in products:
                return jsonify({'result': False, 'reason': 'Unknown product %d' % product_id}), 409
            if quantity == 0:
                return jsonify({'result': False, 'reason': 'quantity cannot be zero'}), 409

        for product_id, quantity in request.json['products'].items():
            product_id = int(product_id)
            if product_id in shopping_carts[cart_id]['products']:
                if shopping_carts[cart_id]['products'][product_id] + quantity > 0:
                    shopping_carts[cart_id]['products'][product_id] += quantity
                else:
                    del shopping_carts[cart_id]['products'][product_id]
            elif quantity > 0:
                shopping_carts[cart_id]['products'][product_id] = quantity

        if len(shopping_carts[cart_id]['products']) == 0:
            del shopping_carts[cart_id]
            return jsonify({'result': True, 'reason': 'shopping_cart deleted'})

        return jsonify({'result': True, 'shopping_cart': shopping_carts[cart_id]})

    elif request.json['action'] == 'purchase':
        for product_id, quantity in shopping_carts[cart_id]['products'].items():
            if products[product_id]['inventory'] == 0:
                return jsonify({'result': False, 'reason': 'out of stock'})

        for product_id, quantity in shopping_carts[cart_id]['products'].items():
            products[product_id]['inventory'] -= quantity

        del shopping_carts[cart_id]
        return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'result': False, 'reason': 'Not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)
