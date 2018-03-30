from api.common.database import engine_mysql

conn = engine_mysql.connect()

class Official_db:
    def search_official_by_id(official_id):
        official = conn.execute('select * from demo.person where id_index=\'{id_index}\''
                                   .format(id_index=official_id)).fetchone()
        return official

    def search_official_by_name(official_name):
        official = conn.execute('select * from demo.person where officer_name=\'{official_name}\''
                                .format(official_name=official_name)).fetchone()
        return official

    def search_officials_by_query(query):
        sql = f"select * from demo.person where officer_name like '%%{query}%%'"
        official_list = conn.execute(sql).fetchall()
        return official_list

    def search_officials_link(id1, id2):
        paths = conn.execute('select * from demo.paths where (start_node_id={id1} and end_node_id={id2}) or (start_node_id={id2} and end_node_id={id1})'
                             .format(id1=id1, id2=id2)).fetchone()
        return paths

    def getAlumnus(id):
        sql = f"select * from demo.schoolfellow where id_x={id} or id_y={id}"
        alumnus_list = conn.execute('select * from demo.schoolfellow where id_x={id} or id_y={id}'
                                    .format(id=id)).fetchall()
        return alumnus_list

    def getColleagues(id):
        colleagues_list = conn.execute('select * from demo.workmate where id_x={id} or id_y={id}'
                                       .format(id=id)).fetchall()
        return colleagues_list

    def getCountrymen(id):
        try:
            countrymen_list = conn.execute('select * from demo.countrymen where id_x={id} or id_y={id}'
                                            .format(id=id)).fetchall()
            return countrymen_list
        except Exception as e:
            return e



official_db = Official_db





