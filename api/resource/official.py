from flask import Blueprint
from flask import make_response, jsonify
from flask import jsonify
from flask_restful import request
from flask_restful import Resource, Api, reqparse
from flasgger.utils import swag_from
from api.handler.official_handler import official_Handler

from api.common.apidoc_path import static_dirs

official_bp = Blueprint('official', __name__, url_prefix='/official')
official_api = Api(official_bp)

parser = reqparse.RequestParser()


class Official(Resource):

    @swag_from('single_official.yml')
    def get(self, official_id):
        response = {
            'code': '200',
            'data': official_Handler.get_official_by_id(official_id),
            'message': 'big brother is watching u :)'
        }
        make_response(jsonify(response))


parse_officials = parser.copy()
parse_officials.add_argument('query', type=str)


class Officials(Resource):
    def get(self):
        args = parse_officials.parse_args()
        response = {
            'code': '200',
            'data': official_Handler.get_officials_by_query(args['query']),
            'message': ''
        }
        return make_response(jsonify(response))


parse_relationship = parser.copy()
parse_relationship.add_argument('id', type=str)
parse_relationship.add_argument('type', type=str)


class Official_Relationship(Resource):
    def get(self):
        args = parse_relationship.parse_args()
        id = args['id']
        if args['type'] == 'alumnus':
            return make_response(jsonify(official_Handler.get_all_alumnus(id)))

        elif args['type'] == 'colleagues':
            return make_response(jsonify(official_Handler.getAllColleagues(id)))

        elif args['type'] == 'countrymen':
            return make_response(jsonify(official_Handler.getAllCountrymen(id)))


parse_graph = parser.copy()
parse_graph.add_argument('id', type=str)


class Official_Graph(Resource):
    def get(self):
        args = parse_graph.parse_args()
        id = args['id']
        reponse = {
            'code': '200',
            'data': official_Handler.get_graph(id),
            'message': 'officials graph'
        }
        return make_response(jsonify(reponse))


parse_link = parser.copy()
parse_link.add_argument('name1', type=str)
parse_link.add_argument('name2', type=str)


class Officials_Link(Resource):
    def get(self):
        args = parse_link.parse_args()
        name1 = args['name1']
        name2 = args['name2']
        response = {
            'code': '200',
            'data': official_Handler.get_links(name1, name2),
            'message': 'all related paths of the two target officials or nothing.'
        }
        return make_response(jsonify(response))


official_api.add_resource(Official, '/<string:official_id>')
official_api.add_resource(Officials, '/inquiry/')
official_api.add_resource(Official_Relationship, '/relations/')
official_api.add_resource(Officials_Link, '/connection/')
official_api.add_resource(Official_Graph, '/graph/')