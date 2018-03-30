from py2neo import Graph, walk, types
import time
import pymysql

# --------------------------------------------------------------------
# 连接Neo4j和MySQL
graph = Graph("http://opsrv.mapout.lan:7474", username="neo4j", password="Neo4j")  # 连接图数据库
mysql = pymysql.connect(db="demo", user="root", passwd="root", host="opsrv.mapout.lan", port=3306, charset="utf8")  # 连接关系型数据库

# --------------------------------------------------------------------
# 数据处理
def period_cmp(start_time1=None, end_time1=None, start_time2=None, end_time2=None):
    """
    函数功能：匹配时间段重叠情况。
    时间格式统一为‘1995-4-16’。
    :param start_time1: 开始时间1
    :param end_time1: 结束时间1
    :param start_time2: 开始时间2
    :param end_time2: 结束时间2
    :return: 重叠时间段
    """
    start_t1 = start_time1.split('-')
    end_t1 = end_time1.split('-')
    start_t2 = start_time2.split('-')
    end_t2 = end_time2.split('-')
    time_int = [365 * (int(start_t1[0]) - 1) + 30 * (int(start_t1[1]) - 1) + int(start_t1[2]),
                365 * (int(end_t1[0]) - 1) + 30 * (int(end_t1[1]) - 1) + int(end_t1[2]),
                365 * (int(start_t2[0]) - 1) + 30 * (int(start_t2[1]) - 1) + int(start_t2[2]),
                365 * (int(end_t2[0]) - 1) + 30 * (int(end_t2[1]) - 1) + int(end_t2[2])]
    if time_int[0] <= time_int[2] <= time_int[1] or time_int[0] <= time_int[3] <=time_int[1]:
        return [start_time1 if time_int[0] >= time_int[2] else start_time2, end_time1 if time_int[3] >= time_int[1] else end_time2]  # 若存在时间重叠，则返回重叠时间段
    else:
        return None  # 若不存在时间重叠，则返回空

def time_now(type_int=0):
    """
    函数功能：匹配时间段重叠情况。
    时间格式统一为‘1995-4-16’。
    :param type_int: 时间类型，0：'1995-4-16'，1：'Sun Apr 16 6:6:6 1995'
    :return: 请求的格式化时间
    """
    if type_int == 0:
        return str(time.localtime(time.time()).tm_year) + '-' + str(time.localtime(time.time()).tm_mon) + '-'\
           + str(time.localtime(time.time()).tm_mday)
    if type_int == 1:
        return time.asctime(time.localtime(time.time()))

# --------------------------------------------------------------------
# 关系查询
def select_countrymen(person_id=None):
    """
    函数功能：在图中查找所有与目的人物具有同乡关系的人物ID。
    :param person_id: 目的人物ID
    :return: 与目的人物具有同乡关系的人物信息列表 person_group[[人物ID，人物姓名]]
    """
    person_group = []  # 用来保存人物信息的列表
    # 查找目标人物节点
    node_x = graph.find_one(label='Person', property_key='id', property_value=person_id)
    # 查找目标人物的所有同乡节点
    get_countrymen = graph.data(f"MATCH (person:Person)-[:is_from]->(:Location)<-[:is_from]-{node_x} "
                                f"RETURN DISTINCT person;")
    for node_y in get_countrymen:  # 保存同乡人物信息
        person_group.append([node_y['person']['id'], node_y['person']['name']])
    return person_group  # 返回同乡人物信息列表

def select_schoolfellow(person_id=None, graph=None):
    """
    函数功能：在图中中查找所有与目的人物具有校友关系的人物ID。
    :param person_id: 目的人物ID
    :return: 与目的人物具有校友关系的人物信息列表 person_group[人物ID，人物姓名]
    """
    person_group = []  # 用来保存人物信息的列表
    # 查找目标人物节点
    node_x = graph.find_one(label='Person', property_key='id', property_value=person_id)
    # 查找目标人物的所有校友节点
    get_schoolfellow = graph.data(f"MATCH (person:Person)-[:schoolfellow_with]-{node_x} RETURN DISTINCT person;")
    for node_y in get_schoolfellow:  # 保存校友人物信息
        person_group.append([node_y['person']['id'], node_y['person']['name']])
    return person_group  # 返回校友人物信息列表

def select_workmate(person_id=None):
    """
    函数功能：在图中中查找所有与目的人物具有同事关系的人物ID。
    :param person_id: 目的人物ID
    :return: 与目的人物具有同事关系的人物信息列表 person_group[[人物ID，人物姓名]]
    """
    person_group = []  # 用来保存人物信息的列表
    # 查找目标人物节点
    node_x = graph.find_one(label='Person', property_key='id', property_value=person_id)
    # 查找目标人物的所有同事节点
    get_workmate = graph.data(f"MATCH (person:Person)-[:workmate_with]-{node_x} RETURN DISTINCT person;")
    for node_y in get_workmate:  # 保存同事人物信息
        person_group.append([node_y['person']['id'], node_y['person']['name']])
    return person_group  # 返回同事人物信息列表

def select_schoolfellow_multi(person_id=None, school_id=None):
    """
    函数功能：通过目标人物ID和目标学校ID，在图中查找该人物在该学校的多种校友关系。
    返回值resume_pair_int中，校友关系类型(1,2,3,4,5)，1：表示同学院且同级，2：表示同学院不同级但时间有重叠，3：表示不同学院但同级，4：表示不同学院不同级但时间有重叠，5：表示同校的其他情况。
    :param person_id: 目的人物ID
    :param school_id: 目的学校ID
    :return: 记录相关工作经历信息的列表 education_pair_int[目标人物ID，相关人物ID，目标教育经历ID，相关教育经历ID，重叠开始时间， 重叠结束时间，关系类型]
    """
    # 目标人物节点
    person = graph.find_one(label='Person', property_key='id', property_value=person_id)
    school = graph.find_one(label='School', property_key='id', property_value=school_id)
    academies = graph.data(f"MATCH {person}-[:study_at]->(academy:Academy)<--{school} RETURN academy;")
    if not person or not school:  #如果没有目标人物节点或目标学校节点，则查找失败
        return None
    education_pair_int = []  #初始化相关教育经历信息列表
    if academies:  # 如果目标人物在学院节点有过教育经历
        for academy in academies:
            academy = academy['academy']
            selece_education = graph.data(f"MATCH {person}-[r:study_at]->{academy} RETURN r;")[0]['r']
            if not selece_education or selece_education['start_time'][0] == '0':  # 如果没有这条教育经历或者教育经历开始时间年份为‘0’，则跳过该学院
                continue
            selece_educationid = selece_education['study_id']  # 保存这条教育经历ID
            start_time = selece_education['start_time']  # 保存这条教育经历开始时间
            # 保存这条教育经历结束时间，如果结束时间年份为‘0’，表示至今，则按格式更改为当前时间
            end_time = selece_education['end_time'] if selece_education['end_time'][0] != '0' else time_now(0)  # 当前日期
            # 查找在当前学院学习过的所有人物
            resume_group = graph.data(f"MATCH {person}-[:study_at]->{academy}<-[r:study_at]-(person:Person) RETURN person, r;")
            for resume in resume_group:  # 匹配教育经历时间
                if person_id == resume['person']['id'] or resume['r']['start_time'][0] == '0':  # 若ID重复或开始时间年份为‘0’(数据不完整)，则忽略该条记录
                    continue
                if resume['r']['end_time'][0] == '0':  # 结束时间年份为‘0’的表示至今，按格式更改为当前时间
                    resume['r']['end_time'] = time_now(0)  # 当前日期
                # 匹配时间段重叠情况
                overlap = period_cmp(start_time, end_time, resume['r']['start_time'], resume['r']['end_time'])
                if overlap:
                    if start_time[0:4] == resume['r']['start_time'][0:4]:  # 添加关系类型1：同学院且同级
                        education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                                   resume['r']['study_id'], overlap[0], overlap[1], 1])
                    else:  # 添加关系类型2：同学院不同级但时间有重叠
                        education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                                   resume['r']['study_id'], overlap[0], overlap[1], 2])
                else:  # 添加关系类型5：同校的其他情况
                    education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                               resume['r']['study_id'], overlap[0], overlap[1], 5])
            # 查找在当前学校的其他学院学习过的所有人物
            resume_group = graph.data(f"MATCH {academy}<-[:include_academy]-(:School)-[:include_academy]->(:Academy)<-[r:study_at]-(person:Person) RETURN person, r;") \
                           + graph.data(f"MATCH {academy}<-[:include_academy]-(:School)<-[r:study_at]-(person:Person) RETURN person, r;")
            for resume in resume_group:  # 匹配教育经历时间
                if person_id == resume['person']['id'] or resume['r']['start_time'][0] == '0':  # 若ID重复或开始时间年份为‘0’(数据不完整)，则忽略该条记录
                    continue
                if resume['r']['end_time'][0] == '0':  # 结束时间年份为‘0’的表示至今，按格式更改为当前时间
                    resume['r']['end_time'] = time_now(0)  # 当前日期
                # 匹配时间段重叠情况
                overlap = period_cmp(start_time, end_time, resume['r']['start_time'], resume['r']['end_time'])
                if overlap:
                    if start_time[0:4] == resume['r']['start_time'][0:4]:  # 添加关系类型3：不同学院但同级
                        education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                                   resume['r']['study_id'], overlap[0], overlap[1], 3])
                    else:  # 添加关系类型4：不同学院不同级但时间有重叠
                        education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                                   resume['r']['study_id'], overlap[0], overlap[1], 4])
                else:  # 添加关系类型5：同校的其他情况
                    education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                               resume['r']['study_id'], overlap[0], overlap[1], 5])
    # 如果目标人物在学校节点有过教育经历
    selece_education = graph.data(f"MATCH {person}-[r:study_at]->{school} RETURN r;")
    if selece_education and not selece_education['start_time'][0] == '0':  # 如果存在这条教育经历并且教育作经历开始时间年份不为‘0’
        selece_education = selece_education[0]['r']
        selece_educationid = selece_education['study_id']  # 保存这条教育经历ID
        start_time = selece_education['start_time']  # 保存这条教育经历开始时间
        # 保存这条教育经历结束时间，如果结束时间年份为‘0’，表示至今，则按格式更改为当前时间
        end_time = selece_education['end_time'] if selece_education['end_time'][0] != '0' else time_now(0)  # 当前日期
        # 查找在当前学校的其他学院学习过的所有人物
        resume_group = graph.data(f"MATCH {school}-[:include_academy]->(:Academy)<-[r:study_at]-(person:Person) RETURN person, r;") \
                       + graph.data(f"MATCH {person}-[:study_at]->{school}<-[r:study_at]-(person:Person) RETURN person, r;")
        for resume in resume_group:  # 匹配教育经历时间
            if person_id == resume['person']['id'] or resume['r']['start_time'][0] == '0':  # 若ID重复或开始时间年份为‘0’(数据不完整)，则忽略该条记录
                continue
            if resume['r']['end_time'][0] == '0':  # 结束时间年份为‘0’的表示至今，按格式更改为当前时间
                resume['r']['end_time'] = time_now(0)  # 当前日期
            # 匹配时间段重叠情况
            overlap = period_cmp(start_time, end_time, resume['r']['start_time'], resume['r']['end_time'])
            if overlap:
                if start_time[0:4] == resume['r']['end_time'][0:4]:  # 添加关系类型3：不同学院但同级
                    education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                               resume['r']['study_id'], overlap[0], overlap[1], 3])
                else:  # 添加关系类型4：不同学院不同级但时间有重叠
                    education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                               resume['r']['study_id'], overlap[0], overlap[1], 4])
            else:  # 添加关系类型5：同校的其他情况
                education_pair_int.append([person_id, resume['person']['id'], selece_educationid,
                                           resume['r']['study_id'], overlap[0], overlap[1], 5])
    return education_pair_int  # 返回相关教育经历信息列表

def select_workmate_multi(person_id=None, position_id=None, max_level=1):
    """
    函数功能：通过目标人物ID和目标职位ID，在图中查找该人物的复杂同事关系。
    返回值resume_pair_int中，同事关系类型[0,10]，n：表示x是y的第n层上级，0：表示x与y是同一级别。双向关系只保存一条记录。
    :param person_id: 目的人物ID
    :param position_id: 目的职位ID
    :param max_level: 最大允许查找上下级的层数，缺省值为1
    :return: 记录相关工作经历信息的列表 resume_pair_int[目标人物ID，相关人物ID，目标工作经历ID，相关工作经历ID，重叠开始时间， 重叠结束时间，关系类型]
    """
    # 目标人物节点
    resume = graph.find_one(label='Person', property_key='id', property_value=person_id)
    # 目标职位节点
    position = graph.find_one(label='Position', property_key='id', property_value=position_id)
    # 目标人物在目标职位的工作经历
    selece_resume = graph.match_one(start_node=resume, end_node=position, rel_type='work_at', bidirectional=True)
    if not selece_resume or selece_resume['start_time'][0] == '0':  # 如果没有这条工作经历或者工作经历开始时间年份为‘0’，则查找失败
        return False
    selece_resumeid = selece_resume['work_id']  # 保存这条工作经历ID
    start_time = selece_resume['start_time']  # 保存这条工作经历开始时间
    # 保存这条工作经历结束时间，如果结束时间年份为‘0’，表示至今，则按格式更改为当前时间
    end_time = selece_resume['end_time'] if selece_resume['end_time'][0] != '0' else time_now(0)  # 当前日期
    resume_pair_int = []  # 初始化：相关工作经历信息列表
    # 查找在当前职位工作的所有人物
    resume_group = graph.data(f"MATCH {resume}-[:work_at]-{position}-[r:work_at]-(person:Person) RETURN person, r;")
    for resume in resume_group:  # 匹配教育经历时间
        if person_id == resume['person']['id'] or resume['r']['start_time'][0] == '0':  # 若ID重复或开始时间年份为‘0’(数据不完整)，则忽略该条记录
            continue
        if resume['r']['end_time'][0] == '0':  # 结束时间年份为‘0’的表示至今，按格式更改为当前时间
            resume['r']['end_time'] = time_now(0)  # 当前日期
        # 匹配时间段重叠情况
        overlap = period_cmp(start_time, end_time, resume['r']['start_time'], resume['r']['end_time'])
        if overlap:  # 添加相关工作经历信息
            resume_pair_int.append([person_id, resume['person']['id'], selece_resumeid, resume['r']['work_id'],
                                    overlap[0], overlap[1], 0])
    rel_level = 0  # 控制查找层级
    while rel_level < max_level:  # 按层次依次查找下级职位节点的工作经历
        rel_level += 1
        persons_down = graph.data(f"MATCH (person:Person)-[r:work_at]->(position:Position)<-"
                                  f"[:include_position*{rel_level}]-{position} RETURN position, r, person;")
        if not persons_down[0]:  # 当没有更低级职位时退出
            break
        for resume in persons_down:
                for i in range(len(persons_down) - 1):
                    if selece_resumeid == resume['r']['work_id'] or resume['r']['start_time'][0] == '0':  # 若ID重复或开始时间年份为‘0’(数据不完整)，则忽略该条记录
                        continue
                    if resume['r']['end_time'][0] == '0':  # 结束时间年份为‘0’的表示至今，按格式更改为当前时间
                        resume['r']['end_time'] = time_now(0)  # 当前日期
                        # 匹配时间段重叠情况
                        overlap = period_cmp(start_time, end_time, resume['r']['start_time'], resume['r']['end_time'])
                        if overlap:  # 添加相关工作经历信息
                            resume_pair_int.append([person_id, resume['person']['id'], selece_resumeid,
                                                    resume['r']['work_id'], overlap[0], overlap[1], rel_level])
    rel_level = 0  # 控制查找层级
    while rel_level < max_level:  # 按层次依次查找上级职位节点的工作经历
        rel_level += 1
        persons_up = graph.data(f"MATCH (person:Person)-[r:work_at]->(position:Position)-"
                                  f"[:include_position*{rel_level}]->{position} RETURN position, r, person;")
        if not persons_up[0]:  # 当没有更高级职位时退出
            break
        for resume in persons_up:
                for i in range(len(persons_up) - 1):
                    if selece_resumeid == resume['r']['work_id'] or resume['r']['start_time'][0] == '0':  # 若ID重复或开始时间年份为‘0’(数据不完整)，则忽略该条记录
                        continue
                    if resume['r']['end_time'][0] == '0':  # 结束时间年份为‘0’的表示至今，按格式更改为当前时间
                        resume['r']['end_time'] = time_now(0)  # 当前日期
                        # 匹配时间段重叠情况
                        overlap = period_cmp(start_time, end_time, resume['r']['start_time'], resume['r']['end_time'])
                        if overlap:  # 添加相关工作经历信息
                            resume_pair_int.append([resume['person']['id'], person_id, resume['r']['work_id'],
                                                    selece_resumeid, overlap[0], overlap[1], rel_level])
    return resume_pair_int  # 返回相关工作经历信息列表

# --------------------------------------------------------------------
# 路径查询
def allShortestPaths(property1_value=None, property2_value=None, node1_label='Person', property1='id',
                     node2_label='Person', property2='id', rel_type=None,  limit=10, n_paths=5):
    """
    函数功能：从图中查找两个目的节点之间的多条最短关系路径。
    返回值中relationship_group[i]表示node_group[i]与node_group[i+1]之间的关系，len(relationship_group)=len(node_group)-1，
    relationship_group中的‘关系方向’取值为1或0，代表'->'或'<-'。
    :param property1_value: 节点1属性值
    :param property2_value: 节点2属性值
    :param node1_label: 节点1标签，缺省值为'Person'
    :param property1: 节点1属性，缺省值为'id'
    :param node2_label: 节点2标签，缺省值为'Person'
    :param property2: 节点2属性，缺省值为'id'
    :param rel_type: 允许搜索的关系类型列表，缺省值为None表示允许搜索所有关系类型
    :param limit: 路径的最大长度，缺省值为10
    :param n_paths: 返回路径的最多条数，缺省值为5
    :return: 所有路径信息：多条路径节点ID列表 node_group，多条路径关系类型列表 relationship_group，多条路径关系方向列表 direction_group
    """
    last_node = None
    node_group = []  # 用来保存所有路径节点的列表
    relationship_group = []  # 用来保存所有路径关系的列表
    direction_group = []  # 用来保存所有路径关系方向的列表
    node1 = graph.find_one(label=node1_label, property_key=property1, property_value=property1_value)  # 查找节点1
    node2 = graph.find_one(label=node2_label, property_key=property2, property_value=property2_value)  # 查找节点2
    get_data = graph.data(f"MATCH path=allShortestPaths({node1}-[{rel_type} *..{limit}]-{node2}) RETURN path;")  # 查找路径
    i = 0
    for result in get_data:  # 拆解路径信息
        i += 1
        # print(time_now(1), i, list(walk(result['path'])))
        nodes, relationships, directions = [], [], []
        for n in walk(result['path']):
            if type(n) is types.Node:
                last_node = n
                nodes.append(n['id'])  # 保存当前路径的一个节点
            if type(n) is types.Relationship:
                relationships.append(n.type())  # 保存当前路径的一个关系名称及方向
                directions.append(1 if n.start_node() == last_node else 0)
        node_group.append(nodes)  # 保存当前路径的所有节点
        relationship_group.append(relationships)  # 保存当前路径的所有关系名称
        direction_group.append(directions)  # 保存当前路径的所有关系方向
    return node_group[0:n_paths], relationship_group[0:n_paths], direction_group[0:n_paths]

def search_paths(node1_id=None, node2_id=None, rel_type_int=[3, 4, 5], limit=10, n_paths=5):
    """
    函数功能：从图中查找两个人物节点之间的多条最短关系路径，并将结果保存在MySQL数据库中。
    保存的数据包括多条路径节点ID列表、多条路径关系类型列表、多条路径关系方向列表，列表中中每条路径用‘；’隔开，每个节点用‘，’隔开。
    关系类型[0,7]，0：其他关系类型，1：亲属关系，2：联系人关系，3：同乡关系，4：同学关系，5：同事关系，6：同行人关系，7：关联关系。
    :param node1_id: 路径起始节点ID
    :param node2_id: 路径终止节点ID
    :param limit: 路径的最大长度，缺省值为10
    :param n_paths: 返回路径的最多条数，缺省值为5
    :param rel_type_int: 允许搜索的关系类型整数列表，缺省允许查找同乡、同学、同事关系，为None时表示允许搜索所有关系类型
    :return: True
    """
    my_cur = mysql.cursor()  # 获取关系型数据库游标
    # MySQL查询语句
    select_sql = f"SELECT * FROM demo.paths WHERE start_node_id={node1_id} AND end_node_id={node2_id} " \
                 f"OR start_node_id={node2_id} AND end_node_id={node1_id};"
    # MuSQL更新语句
    update_sql = "UPDATE demo.paths SET paths_nodes_id='{0}', paths_relationships='{1}', paths_directions='{2}' " \
                 "WHERE start_node_id={3} AND end_node_id={4} OR start_node_id={4} AND end_node_id={3};"
    # MySQL插入语句，保存路径
    insert_sql = "INSERT INTO demo.paths(start_node_id, end_node_id, paths_nodes_id, paths_relationships, paths_directions) " \
                 "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');"
    if rel_type_int:
        rel_define = ':'
        for rel in rel_type_int:
            if rel == 1:
                rel_define += 'kinsfolk_with|'
            if rel == 2:
                rel_define += 'contact_with|'
            if rel == 3:
                rel_define += 'is_from|'
            if rel == 4:
                rel_define += 'schoolfellow_with|'
            if rel == 5:
                rel_define += 'workmate_with|'
            if rel == 6:
                rel_define += 'walk_with|'
            if rel == 7:
                rel_define += 'correlate_with|'
    else:
        rel_define = ''
    rel_define = rel_define[0:-1]
    paths = allShortestPaths(node1_id, node2_id, 'Person', 'id', 'Person', 'id', rel_define, limit, n_paths)
    if not paths[2]:
        return None
    paths_nodes_id = ''
    paths_relationships = ''
    paths_directions = ''
    for i in range(len(paths[2])):
        paths_nodes_id += paths[0][i][0]
        key = trigger = 0
        for j in range(len(paths[2][i])):
            type_rel = '0'
            if paths[1][i][j] == 'kinsfolk_with':
                type_rel = '1'
            if paths[1][i][j] == 'contact_with':
                type_rel = '2'
            if paths[1][i][j] == 'is_from':
                type_rel = '3'
                trigger += 1
            if paths[1][i][j] == 'schoolfellow_with':
                type_rel = '4'
            if paths[1][i][j] == 'workmate_with':
                type_rel = '5'
            if paths[1][i][j] == 'walk_with':
                type_rel = '6'
            if paths[1][i][j] == 'correlate_with':
                type_rel = '7'
            if trigger % 2 == 1:
                continue
            paths_nodes_id += ',' + paths[0][i][j + 1]
            if key == 0:
                paths_relationships += type_rel
                paths_directions += str(paths[2][i][j])
                key = 1
            else:
                paths_relationships += ',' + type_rel
                paths_directions += ',' + str(paths[2][i][j])
        if i < len(paths[2])-1:
            paths_nodes_id += ';'
            paths_relationships += ';'
            paths_directions += ';'
    if my_cur.execute(select_sql):
        try:
            my_cur.execute(update_sql.format(paths_nodes_id, paths_relationships, paths_directions, node1_id, node2_id))
            mysql.commit()
            # print(time_now(1), ':Paths-MySQL Update Successful:', node1_id, node2_id)
        except:
            mysql.rollback()  # 插入失败，执行回滚操作
            # print(time_now(1), ':Paths-MySQL Update Error:', node1_id, node2_id)
    else:
        try:
            my_cur.execute(insert_sql.format(node1_id, node2_id, paths_nodes_id, paths_relationships, paths_directions))
            mysql.commit()
            # print(time_now(1), ':Paths-MySQL Insert Successful:', node1_id, node2_id)
        except:
            mysql.rollback()  # 插入失败，执行回滚操作
            # print(time_now(1), ':Paths-MySQL Insert Error:', node1_id, node2_id)
    my_cur.close()
    paths = {
        'paths_nodes_id': paths_nodes_id,
        'paths_relationships': paths_relationships,
        'paths_directions': paths_directions
    }
    print(paths)
    return paths
