from flask import Flask, jsonify, abort, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


# Relationship
class Relationship(db.Model):
    __tablename__ = 'product_shoppingcart'
    shoppingcart_id = db.Column('shoppingcart_id', db.Integer, db.ForeignKey('shoppingcart.id'), primary_key=True)
    product_id = db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
    quantity = db.Column('quantity', db.Integer, nullable=False)

    def __repr__(self):
        return '<Relationship %d: %r x %d>' % (self.shoppingcart_id, Product.query.get(self.product_id).title, self.quantity)

# products
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    inventory = db.Column(db.Integer, nullable=False)
    relationships = db.relationship('Relationship', backref='product',
                         primaryjoin=id == Relationship.product_id, lazy='select')

    def __repr__(self):
        return '<Product %r>' % self.title

    @property
    def json(self):
        return {'id': self.id,
                'title': self.title,
                'price': self.price,
                'inventory': self.inventory}

class ShoppingCart(db.Model):
    __tablename__ = 'shoppingcart'
    id = db.Column(db.Integer, primary_key=True)
    relationships = db.relationship('Relationship', backref='shopping_cart',
                         primaryjoin=id == Relationship.shoppingcart_id)

    def __repr__(self):
        return '<ShoppingCart %d>' % self.id

    @property
    def json(self):
        return {'id': self.id,
                'products': dict([(relationship.product.id, relationship.quantity) for relationship in self.relationships])}

def test_db():
    db.create_all()
    apple = Product(title="Apple", price=30, inventory=5)
    bear = Product(title="Bear", price=20, inventory=1)
    orange = Product(title='Orange', price=10, inventory=0)
    db.session.add(apple)
    db.session.add(bear)
    db.session.add(orange)
    # sc1 = ShoppingCart()
    # sc2 = ShoppingCart()
    # db.session.add(sc1)
    # db.session.add(sc2)
    # def add_product(sc, product, quantity):
    #     rel = Relationship(shoppingcart_id=sc.id, product_id=product.id, quantity=quantity)
    #     sc.stock.append(rel)
    #     product.stock.append(rel)
    #     db.session.add(rel)
    #
    # add_product(sc1, apple, 1)
    # add_product(sc1, bear, 2)
    # add_product(sc2, apple, 3)
    # add_product(sc2, bear, 4)
    db.session.commit()

# products = {
#     1: {
#         'title': 'Apple',
#         'price': 20,
#         'inventory': 5,
#     },
#     2: {
#         'title': 'Bear',
#         'price': 13,
#         'inventory': 2,
#     },
#     3: {
#         'title': 'Desk',
#         'price': 100,
#         'inventory': 0,
#     }
# }
#
# shopping_carts = {
#     1: {
#         'products': {1: 1, 3: 2}
#     }
# }


@app.route('/api/v1.0/products', methods=['GET'])
def get_products():
    only_available = request.args.get('avaliable', 'false')
    if only_available == 'true':
        products = Product.query.filter(Product.inventory > 0)
        return jsonify({'products': [product.json for product in products]})
    else:
        products = Product.query.all()
        return jsonify({'products': [product.json for product in products]})


@app.route('/api/v1.0/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'product': product.json})

# curl -i -H "Content-Type: application/json" -X PUT -d '{"action":"purchase"}' http://localhost:5000/api/v1.0/products/1
@app.route('/api/v1.0/products/<int:product_id>', methods=['PUT'])
def purchase_product(product_id):
    if not request.json:
        abort(400)
    if 'action' in request.json and type(request.json['action']) is not str:
        abort(400)
    if request.json['action'] == 'purchase':
        product = db.session.query(Product).with_for_update().get_or_404(product_id)
        if product.inventory > 0:
            product.inventory -= 1
            db.session.add(product)
            db.session.commit()
            return jsonify({'result': True, 'product': product.json})
        else:
            return jsonify({'result': False, 'reason': 'out of stock', 'product': product.json}), 409
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

    shoppingcart = ShoppingCart()
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
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'result': False, 'reason': 'Unknown product %d' % product_id}), 409
        relationship = Relationship(shoppingcart_id=shoppingcart.id, product_id=product_id, quantity=quantity)
        # relationship.shoppingcart_id is unknown, need to add relationship to shoppingcart for dependency
        shoppingcart.relationships.append(relationship)
        db.session.add(relationship)
    db.session.add(shoppingcart)
    db.session.commit()
    return jsonify({'result': True, 'shopping_cart': shoppingcart.json}), 201


# get all shopping_carts
@app.route('/api/v1.0/shopping_carts', methods=['GET'])
def get_shopping_carts():
    return jsonify({'shopping_carts': [shoppingcart.json for shoppingcart in ShoppingCart.query.all()]})


# get all products in cart
# response content: {'id': uri, 'products': [...]}
@app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['GET'])
def get_shopping_cart(cart_id):
    return jsonify({'shopping_cart': ShoppingCart.query.get_or_404(cart_id).json})


# delete a cart
@app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['DELETE'])
def remove_shopping_cart(cart_id):
    shoppingcart = ShoppingCart.query.get_or_404(cart_id)
    db.session.query(Relationship).filter(Relationship.shoppingcart_id == cart_id).delete()
    db.session.delete(shoppingcart)
    db.session.commit()
    return jsonify({'result': True})


# 1. add/remove product(s) to cart, request content: {'action':'add_product', 'products': {123: 1, 345: -1}]}
# 3. purchase all products in cart, request content: {'action':'purchase'}
#    if purchase success, cart should be removed
#    update the inventory of products
# @app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['PUT'])

@app.route('/api/v1.0/shopping_carts/<int:cart_id>', methods=['PUT'])
def add_item_shopping_cart(cart_id):
    shoppingcart = db.session.query(ShoppingCart).with_for_update().get_or_404(cart_id)
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
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'result': False, 'reason': 'Unknown product %d' % product_id}), 409
            if quantity == 0:
                return jsonify({'result': False, 'reason': 'quantity cannot be zero'}), 409
            relationships = [relationship for relationship in shoppingcart.relationships if relationship.product_id == product_id]
            if relationships:
                relationship = relationships[0]
                if relationship.quantity + quantity > 0:
                    relationship.quantity += quantity
                    db.session.add(relationship)
                else:
                    shoppingcart.relationships.remove(relationship)
                    db.session.delete(relationship)
            elif quantity > 0:
                relationship = Relationship(shoppingcart_id=shoppingcart.id, product_id=product_id, quantity=quantity)
                shoppingcart.relationships.append(relationship)
                db.session.add(relationship)

        if not shoppingcart.relationships:
            db.session.delete(shoppingcart)
            db.session.commit()
            return jsonify({'result': True, 'reason': 'shopping_cart deleted'})

        db.session.commit()
        return jsonify({'result': True, 'shopping_cart': shoppingcart.json})

    elif request.json['action'] == 'purchase':
        for relationship in shoppingcart.relationships:
            # lock row
            product = db.session.query(Product).with_for_update().get(relationship.product.id)
            if product.inventory - relationship.quantity < 0:
                return jsonify({'result': False, 'reason': 'out of stock'})
            product.inventory -= relationship.quantity
            db.session.add(product)

        db.session.query(Relationship).filter(Relationship.shoppingcart_id == cart_id).delete()
        db.session.delete(shoppingcart)
        db.session.commit()
        return jsonify({'result': True})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'result': False, 'reason': 'Not found'}), 404


if __name__ == '__main__':
    # test_db()
    app.run(debug=True)
