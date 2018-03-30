from api.model.official_db import official_db
from api.common.neo4j_search import search_paths

def num2rel(num):
    rel = ['其他', '亲属', '联系', '同乡', '同学', '同事', '同行', '关联', '未知']
    if num:
        return rel[int(num)]
    else:
        return rel[-1]

class Official_Handler:
    def get_official_by_id(id):
        official = official_db.search_official_by_id(id)
        if official is not None:
            response = {
                'id_index': official.id_index,
                'name': official.officer_name,
                'gender': official.gender,
                'cur_pos': official.current_position,
                'date_of_birth': official.date_of_birth,
                'place-of_birth': official.place_of_birth,
                'nation': official.nation,
                'time_and_job': official.time_and_job
            }
            return response
        else:
            return []


    def get_officials_by_query(query):
        officials = official_db.search_officials_by_query(query)
        if officials is None:
            return []
        response = []
        for official in officials:
            obj = {
                'id_index': official.id_index,
                'name': official.officer_name,
                'gender': official.gender,
                'cur_pos': official.current_position,
                'date_of_birth': official.date_of_birth,
                'place_of_birth': official.place_of_birth,
                'nation': official.nation,
                'time_and_job': official.time_and_job,
                'img_url': official.head_image_url
            }
            response.append(obj)
        return response

    def get_all_alumnus(id):
        alumnus_list = official_db.getAlumnus(id)
        schools = []
        school_name = set()
        schoolfellows = []
        for relation in alumnus_list:
            alumnus = {
                'id': '',
                'name': '',
                'curpos': '',
                'school_name': relation.school_x,
                'school_id': relation.school_x_id,
                'school_start_time': relation.start_time,
                'school_end_time': relation.end_time,
                'head_image_url': ''
            }
            if relation.id_x == id:
                alumnus['id'] = relation.id_y
                alumnus['name'] = relation.name_y
                alumnus['curpos'] = official_db.search_official_by_id(relation.id_y).current_position
                alumnus['head_image_url'] = official_db.search_official_by_id(relation.id_y).head_image_url
            else:
                alumnus['id'] = relation.id_x
                alumnus['name'] = relation.name_x
                alumnus['curpos'] = official_db.search_official_by_id(relation.id_x).current_position
                alumnus['head_image_url'] = official_db.search_official_by_id(relation.id_x).head_image_url
            schoolfellows.append(alumnus)
            if relation.school_x not in school_name:
                school_name.add(relation.school_x)
        for name in school_name:
            school = {
                'id': '',
                'name': name,
                'time': '',
                'alumnus': []
            }
            schools.append(school)
        for fellow in schoolfellows:
            for school in schools:
                if school['name'] == fellow['school_name']:
                    school['id'] = fellow['school_id']
                    school['time'] = fellow['school_start_time'][0:4] + '-' + fellow['school_end_time'][0:4]
                    fellow.pop('school_id')
                    fellow.pop('school_name')
                    school['alumnus'].append(fellow)
                    break
        return schools

    def get_all_colleagues(id):
        colleagues_list = official_db.getColleagues(id)
        institutions = []
        institiution_names = set()
        colleagues = []
        for relation in colleagues_list:
            colleague = {
                'id': '',
                'name': '',
                'position': '',
                'institution': relation.institution_x,
                'institution_id': relation.institution_x_id,
                'start_time': relation.start_time,
                'end_time': relation.end_time,
                'curpos': '',
                'head_image_url': ''
            }
            if id == relation.id_x:
                colleague['id'] = relation.id_y
                colleague['name'] = relation.name_y
                colleague['position'] = relation.position_y
                colleague['curpos'] = official_db.search_official_by_id(relation.id_y).current_position
                colleague['head_image_url'] = official_db.search_official_by_id(relation.id_y).head_image_url
            else:
                colleague['id'] = relation.id_x
                colleague['name'] = relation.name_x
                colleague['position'] = relation.position_x
                colleague['curpos'] = official_db.search_official_by_id(relation.id_x).current_position
                colleague['head_image_url'] = official_db.search_official_by_id(relation.id_x).head_image_url
            colleagues.append(colleague)
            if relation.institution_x not in institiution_names:
                institiution_names.add(relation.institution_x)
        for name in institiution_names:
            institution = {
                'id': '',
                'name': name,
                'time': '',
                'colleagues': []
            }
            institutions.append(institution)
        for colleague in colleagues:
            for institution in institutions:
                if institution['name'] == colleague['institution']:
                    institution['id'] = colleague['institution_id']
                    institution['time'] = colleague['start_time'][0:4] + '-' + colleague['end_time'][0:4]
                    colleague.pop('institution_id')
                    colleague.pop('institution')
                    institution['colleagues'].append(colleague)
                    break
        return institutions

    def get_all_countrymen(id):
        countrymen_list = official_db.getCountrymen(id)
        countrymen = []
        for relation in countrymen_list:
            countryman = {
                'id': '',
                'name': '',
                'curpos': '',
                'head_image_url': ''
            }
            if id == relation.id_x:
                countryman['id'] = relation.id_y
                countryman['name'] = relation.name_y
                countryman['curpos'] = official_db.search_official_by_id(relation.id_y).current_position
                countryman['head_image_url'] = official_db.search_official_by_id(relation.id_y).head_image_url
            else:
                countryman['id'] = relation.id_x
                countryman['name'] = relation.name_x
                countryman['curpos'] = official_db.search_official_by_id(relation.id_x).current_position
                countryman['head_image_url'] = official_db.search_official_by_id(relation.id_x).head_image_url
            countrymen.append(countryman)
        official = official_db.search_official_by_id(id)
        country = {
            'id': official.place_of_birth_id,
            'place': countrymen_list[0].place_of_birth,
            'countrymen': countrymen
        }
        return country

    def get_graph(id):
        official = official_db.search_official_by_id(id)
        graph = {
            'name': official.officer_name,
            'symbol': official.head_image_url,
            'children': []
        }

        countrymen = {
            'name': '同乡',
            'children': []
        }
        countrymenList = official_db.getCountrymen(id)
        countrymen_graph = []
        for countryman in countrymenList:
            countryman_graph = {
                'name': '',
                'job': ''
            }
            if id == countryman.id_x:
                countryman_graph['name'] = countryman.name_y
                countryman_graph['job'] = official_db.search_official_by_id(countryman.id_y).current_position
            else:
                countryman_graph['name'] = countryman.name_x
                countryman_graph['job'] = official_db.search_official_by_id(countryman.id_x).current_position
            countrymen_graph.append(countryman_graph)
        countrymen['children'] = countrymen_graph
        graph['children'].append(countrymen)

        alumnus_in_graph = {
            'name': '同校',
            'children': []
        }
        alumnusList = official_db.getAlumnus(id)
        alumnus_graph = []
        for alumnus in alumnusList:
            schoolfellow = {
                'name': '',
                'job': ''
            }
            if id == alumnus.id_x:
                schoolfellow['name'] = alumnus.name_y
                schoolfellow['job'] = official_db.search_official_by_id(alumnus.id_y).current_position
            else:
                schoolfellow['name'] = alumnus.name_x
                schoolfellow['job'] = official_db.search_official_by_id(alumnus.id_x).current_position
            alumnus_graph.append(schoolfellow)
        alumnus_in_graph['children'] = alumnus_graph
        graph['children'].append(alumnus_in_graph)

        colleagues = {
            'name': '同事',
            'children': []
        }
        colleaguesList = official_db.getColleagues(id)
        colleagues_graph = []
        for colleague in colleaguesList:
            colleague_graph = {
                'name': '',
                'job': ''
            }
            if id == colleague.id_x:
                colleague_graph['name'] = colleague.name_y
                colleague_graph['job'] = official_db.search_official_by_id(colleague.id_y).current_position
            else:
                colleague_graph['name'] = colleague.name_x
                colleague_graph['job'] = official_db.search_official_by_id(colleague.id_x).current_position
            colleagues_graph.append(colleague_graph)
        colleagues['children'] = colleagues_graph
        graph['children'].append(colleagues)
        return graph


    def get_links(name1, name2):
        official1 = official_db.search_official_by_name(name1)
        official2 = official_db.search_official_by_name(name2)
        if official1 is None or official2 is None:
            return []
        links = {
            'elements': {}
        }
        elements = {
            'nodes': [],
            'edges': []
        }
        start_node_info = {
            'data': {
                'id': official1.id_index,
                'name': official1.officer_name,
                'type': 't',
                'img': official1.head_image_url,
            }
        }
        end_node_info = {
            'data': {
                'id': official2.id_index,
                'name': official2.officer_name,
                'type': 't',
                'img': official2.head_image_url,
            }
        }
        elements['nodes'].append(start_node_info)
        elements['nodes'].append(end_node_info)

        id1 = official1.id_index
        id2 = official2.id_index
        print(id1)
        print(id2)
        paths = official_db.search_officials_link(id1, id2)
        paths_nodes = str()
        relations_edges = str()
        if paths is None:
            paths_graph = search_paths(id1, id2, [3, 4, 5, 6])
            if paths_graph is None:
                return []
            else:
                paths_nodes = paths_graph['paths_nodes_id']
                relations_edges = paths_graph['paths_relationships']
        else:
            paths_nodes = paths.paths_nodes_id
            relations_edges = paths.paths_relationships

        roads = paths_nodes.split(';')

        relations = relations_edges.split(';')

        nodes_id = set()
        edges_id = set()
        nodes_id.add(official1.id_index)
        nodes_id.add(official2.id_index)

        for (road, relation) in zip(roads, relations):
            nodes = road.split(',')
            edges = relation.split(',')

            length = len(nodes)
            for i, node_id in enumerate(nodes):
                if node_id not in nodes_id:
                    print(node_id)
                    official = official_db.search_official_by_id(node_id)
                    node_info = {
                        'data': {
                            'id': node_id,
                            'name': official.officer_name,
                            'job': official.current_position,
                            'type': 'n'
                        }
                    }
                    elements['nodes'].append(node_info)
                    nodes_id.add(node_id)
                if i+1 < length:
                    edge_id = node_id + nodes[i+1]
                    if edge_id not in edges_id:
                        edge_info = {
                            'data': {
                                'rel': num2rel(edges[i]),
                                'source': node_id,
                                'target': nodes[i+1]
                            }
                        }
                        elements['edges'].append(edge_info)
                        edges_id.add(edge_id)
        links['elements'] = elements
        return links

        #     path = {
        #         'nodes': officials,
        #         'edges': relation
        #     }
        #     allpath.append(path)
        # links = {
        #     'start_node_id': id1,
        #     'end_node_id': id2,
        #     'start_node_image': official_db.search_official_by_id(id1).head_image_url,
        #     'end_node_image': official_db.search_official_by_id(id2).head_image_url,
        #     'paths': allpath
        # }

official_Handler = Official_Handler
