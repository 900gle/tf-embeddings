# import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import kss, numpy
import json

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

def getTextVectors(input):
    vectors = module(input)
    return [vector.numpy().tolist() for vector in vectors]
#
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Vector(Resource):
    def get(self, input):
        return {'vectors': json.dumps(getTextVectors(input)[0], cls=NumpyEncoder)}

    def post(self, input):
        args = parser.parse_args()
        return {'vectors': json.dumps(getTextVectors(input)[0], cls=NumpyEncoder)}

api.add_resource(Vector, '/vectors/<string:input>')

if __name__ == '__main__':
    module = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
    app.run(debug=True)
