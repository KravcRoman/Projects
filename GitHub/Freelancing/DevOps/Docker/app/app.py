from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient(host='db', port=27017)
db = client['mydatabase']
collection = db['mycollection']

@app.route('/keyvalue', methods=['GET', 'POST', 'PUT'])
def key_value():
    if request.method == 'POST':
        data = request.json
        collection.insert_one(data)
        return jsonify({'message': 'Key-value pair created successfully'}), 201
    elif request.method == 'PUT':
        data = request.json
        key = data.get('key')
        value = data.get('value')
        collection.update_one({'key': key}, {'$set': {'value': value}}, upsert=True)
        return jsonify({'message': 'Key-value pair updated successfully'}), 200
    elif request.method == 'GET':
        key = request.args.get('key')
        data = collection.find_one({'key': key})
        if data:
            return jsonify({'value': data['value']}), 200
        else:
            return jsonify({'message': 'Key not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)