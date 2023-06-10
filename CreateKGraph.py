import os
import json
from py2neo import Graph, Node


class MedicalGraph:
    # 连接数据库
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/medical_data.json')
        self.g = Graph(
            host='127.0.0.1',
            user='neo4j',
            password='190915')

    # 读取json文件
    def read_nodes(self):
        # 6类实体
        drugs = []  # 药品
        foods = []  # 食物
        diseases = []  # 疾病
        symptoms = []  # 症状
        departments = []  # 所属科室
        checks = []  # 检查

        # 疾病实体的属性
        disease_infos = []

        # 实体间的关系
        rels_department = []  # 科室——科室
        rels_noteat = []  # 疾病——忌吃食品
        rels_doeat = []  # 疾病——宜吃食品
        rels_drug = []  # 疾病——药物
        rels_check = []  # 疾病——检查
        rels_symptom = []  # 疾病——症状
        rels_accompany = []  # 疾病——相关疾病
        rels_category = []  # 疾病——科室

        count = 0
        for df in open(self.data_path, encoding='utf-8'):
            disease_dict = {}
            count += 1
            print(count)
            data_json = json.loads(df)
            disease = data_json['name']  # 疾病的名称
            # print(disease)
            disease_dict['name'] = disease
            diseases.append(disease)
            disease_dict['desc'] = ''  # 百科介绍
            disease_dict['prevent'] = ''  # 疾病预防
            disease_dict['cause'] = ''  # 病因
            disease_dict['symptom'] = ''  # 疾病
            disease_dict['cure_department'] = ''  # 所属科室

            # 实体间的关系
            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])  # 建立 疾病——症状 关系

            if 'accompany' in data_json:
                for accompany in data_json['accompany']:
                    rels_accompany.append([disease, accompany])  # 建立 疾病——并发症1，2，...，n 关系

            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']  # 预防

            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']  # 病因

            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']
                if len(cure_department) == 1:
                    rels_category.append([disease, cure_department[0]])
                if len(cure_department) == 2:
                    big = cure_department[0]  # 大科室
                    small = cure_department[1]  # 小科室
                    rels_department.append([small, big])  # 建立 科室1——科室2 关系
                    rels_category.append([disease, small])  # 建立 疾病——科室1 关系

                disease_dict['cure_department'] = cure_department
                departments += cure_department

            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']
                for drug in common_drug:
                    rels_drug.append([disease, drug])  # 建立 疾病——药物 关系
                drugs = common_drug

            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']
                for n_eat in not_eat:
                    rels_noteat.append([disease, n_eat])  # 建立 疾病——忌吃食物推荐 关系
                foods += not_eat

                do_eat = data_json['do_eat']
                for d_eat in do_eat:
                    rels_doeat.append([disease, d_eat])  # 建立 疾病——易吃食品推荐 关系
                foods += do_eat

            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    rels_check.append([disease, _check])  # 建立 疾病——检查科项目 关系
                checks += check

            # 疾病实体的属性
            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']


            disease_infos.append(disease_dict)
        return set(drugs), set(foods), set(checks), set(departments), set(symptoms), set(diseases), \
            disease_infos, rels_check, rels_doeat, rels_noteat, rels_drug, rels_category, \
            rels_department, rels_accompany, rels_symptom

    '''建立节点'''

    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))

    '''创建知识图谱的中心（疾病）实体节点'''
    def create_diseases_nodes(self, disease_infos):
        count = 0
        for disease_dict in disease_infos:
            node = Node("Disease", name=disease_dict['name'], dese=disease_dict['desc'],
                        prevent=disease_dict['prevent'], cause=disease_dict['cause'],
                        cure_department=disease_dict['cure_department'])
            self.g.create(node)
            count += 1
            print(count)
        return

    '''创建实体节点类型'''

    def create_graphnodes(self):
        Drugs, Foods, Checks, Departments, Symptoms, Diseases, \
            disease_infos, rels_check, rels_doeat, rels_noteat, \
            rels_drug, rels_category, rels_department, rels_accompany, \
            rels_symptom = self.read_nodes()
        self.create_diseases_nodes(disease_infos)
        self.create_node('Drug', Drugs)
        print(len(Drugs))
        self.create_node('Food', Foods)
        print(len(Foods))
        self.create_node('Check', Checks)
        print(len(Checks))
        self.create_node('Department', Departments)
        print(len(Departments))
        self.create_node('Symptom', Symptoms)
        print(len(Symptoms))
        return

    '''创建实体关系（边）'''

    def create_graphrels(self):
        Drugs, Foods, Checks, Departments, Symptoms, Diseases, \
            disease_infos, rels_check, rels_doeat, rels_noteat, \
            rels_drug, rels_category, rels_department, rels_accompany, \
            rels_symptom = self.read_nodes()
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', rels_drug, 'common_drug', '常用药物')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_accompany, 'accompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')

    '''创建实体关联边'''

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s' and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
            return

    '''导出数据'''
    def export_data(self):
        Drugs, Foods, Checks, Departments, Symptoms, Diseases, \
            disease_infos, rels_check, rels_doeat, rels_noteat, \
            rels_drug, rels_category, rels_department, rels_accompany, \
            rels_symptom = self.read_nodes()
        f_drug = open('./dict/drug.txt', 'w+')
        f_food = open('./dict/food.txt', 'w+')
        f_check = open('./dict/check.txt', 'w+')
        f_department = open('./dict/department.txt', 'w+')
        f_symptom = open('./dict/symptoms.txt', 'w+')
        f_disease = open('./dict/disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_symptom.close()
        f_disease.close()

        return

if __name__ == '__main__':
    handler = MedicalGraph()
    print("step1:开始构建图谱实体节点")
    handler.create_graphnodes()
    print("step1:实体节点构建完成！")
    print("step2:开始构建图谱实体间的关系")
    handler.create_graphrels()
    print("step2:实体间的关系构建完成！")
    handler.export_data()
    print("\n图谱构建完成！")
