from application import app
import json
import sqlite3 as sql
import os


class User(object):
    def __init__(self, id, username, hash):
        self.id = id
        self.username = username
        self.hash = hash

    @classmethod
    def from_json(cls, json_string):
        """
        Convert to python object using JSON
        https://www.youtube.com/watch?v=hJ2HfejqppE
        """
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Project(object):
    def __init__(self, id, user_id, created_on, name, started_on, ended_on,
                 project_memo):
        self.id = id
        self.user_id = user_id
        self.created_on = created_on
        self.name = name
        self.started_on = started_on
        self.ended_on = ended_on
        self.project_memo = project_memo

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Application(object):
    def __init__(self, id, project_id, name, company_id, role,
                 application_memo, rank, company_name, type, date):
        self.id = id
        self.project_id = project_id
        self.project_name = name
        self.company_id = company_id
        self.role = role
        self.application_memo = application_memo
        self.rank = rank
        self.company_name = company_name
        self.stage = type
        self.date = date

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Stage(object):
    def __init__(self, id, application_id, date, type, stage_memo):
        self.id = id
        self.application_id = application_id
        self.date = date
        self.type = type
        self.stage_memo = stage_memo

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Company(object):
    def __init__(self, id, user_id, company_name, company_memo):
        self.id = id
        self.user_id = user_id
        self.company_name = company_name
        self.company_memo = company_memo

    @classmethod
    def from_json(cls, json_string):
        json_dict = json.loads(json_string)
        return cls(**json_dict)


class Database(object):
    def __init__(self):
        self.db_connection = None

    def __enter__(self):
        connection = sql.connect(os.getenv("DATABASE_URL"))
        connection.row_factory = dict_factory
        self.db_connection = connection
        return self.db_connection

    def __exit__(self, type, value, traceback):
        self.db_connection.close()

    @classmethod
    def fetch_one(cls, script, arguments):
        try:
            with Database() as db:
                cursor = db.cursor()
                result = cursor.execute(script, arguments).fetchone()
                cursor.close()
                return result
        except sql.Error as error:
            raise error

    @classmethod
    def fetch_all(cls, script, arguments):
        try:
            with Database() as db:
                cursor = db.cursor()
                result = cursor.execute(script, arguments).fetchall()
                cursor.close()
                return result
        except sql.Error as error:
            raise error

    @classmethod
    def commit(cls, script, arguments):
        """ Insert, update, delete operations """
        try:
            with Database() as db:
                cursor = db.cursor()
                cursor.execute(script, arguments)
                db.commit()
                cursor.close()
        except sql.Error as error:
            raise error


def dict_factory(cursor, row):
    """
    Convert the result to a dictionary including the column names
    https://stackoverflow.com/a/3300514/
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def register_user(username, hashed_password):
    Database().commit("INSERT INTO users(username, hash) VALUES(?, ?)",
                      (username, hashed_password))


def get_user_with_id(id):
    return Database.fetch_one("SELECT * FROM users WHERE id = ?", (id,))


def get_user_with_username(username):
    return Database.fetch_one("SELECT * FROM users WHERE username = ?",
                              (username,))


def create_project(user_id, created_on, name, project_memo):
    Database().commit(
        """INSERT INTO projects(user_id, created_on, name, project_memo) 
        VALUES(?, ?, ?, ?)""",
        (user_id, created_on, name, project_memo))


def edit_project(project_id, name, started_on, ended_on, project_memo):
    Database().commit(
        """UPDATE projects 
        SET name = ?, started_on = ?, ended_on = ?, project_memo = ? 
        WHERE id = ?""",
        (name, started_on, ended_on, project_memo, project_id))


def get_project(project_id):
    return Database.fetch_one(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,))


def get_last_project_datetime(user_id):
    return Database.fetch_one(
        """SELECT created_on FROM projects WHERE user_id = ? 
        ORDER BY created_on DESC""",
        (user_id,))


def get_all_projects(user_id):
    return Database.fetch_all(
        """SELECT * FROM projects WHERE user_id = ? 
        ORDER BY created_on DESC""",
        (user_id,))


def create_company(user_id, company_name):
    Database().commit(
        "INSERT INTO companies(user_id, company_name) VALUES(?, ?)",
        (user_id, company_name))


def search_company(user_id, company_name):
    company_name = "%" + company_name + "%"
    return Database.fetch_all(
        "SELECT * FROM companies WHERE company_name LIKE ? AND user_id = ?",
        (company_name, user_id))


def get_company_id(user_id, company_name):
    return Database.fetch_one(
        "SELECT id FROM companies WHERE company_name = ? AND user_id = ?",
        (company_name, user_id))


def get_company(company_id):
    return Database.fetch_one("SELECT * FROM companies WHERE id = ?",
                              (company_id,))


def create_application(project_id, company_id, role, memo, rank):
    Database().commit(
        """INSERT INTO 
        applications(project_id, company_id, role, application_memo, rank) 
        VALUES(?, ?, ?, ?, ?)""",
        (project_id, company_id, role, memo, rank))


def get_simple_application(application_id):
    return Database.fetch_one(
        """SELECT company_name, role, application_memo FROM applications 
        JOIN companies ON companies.id = applications.company_id 
        WHERE applications.id = ?""",
        (application_id,))


def get_application_id(project_id, company_id):
    return Database.fetch_one(
        "SELECT id FROM applications WHERE project_id = ? AND company_id = ?",
        (project_id, company_id))


def get_application(application_id):
    return Database.fetch_one(
        """SELECT id, project_id, name, company_id, role, 
        application_memo, rank, company_name, type, date 
        FROM (SELECT * FROM applications 
        JOIN companies ON companies.id = applications.company_id 
        JOIN stages ON stages.application_id = applications.id 
        JOIN projects ON projects.id = applications.project_id 
        GROUP BY applications.id) 
        WHERE id = ?""",
        (application_id,))


def get_all_applications(project_id):
    return Database.fetch_all(
        """SELECT id, project_id, name, company_id, role, 
        application_memo, rank, company_name, type, date 
        FROM (SELECT * FROM applications 
        JOIN companies ON companies.id = applications.company_id 
        JOIN stages ON stages.application_id = applications.id 
        JOIN projects ON projects.id = applications.project_id 
        ORDER BY stages.id DESC) 
        WHERE project_id = ? 
        GROUP BY application_id 
        ORDER BY rank""",
        (project_id,))


def get_all_company_ids_from_project(project_id):
    return Database.fetch_all(
        "SELECT company_id FROM applications WHERE project_id = ?",
        (project_id,))


def get_company_history(company_id):
    return Database.fetch_all(
        """SELECT id, project_id, name, company_id, role, 
        application_memo, rank, company_name, type, date 
        FROM (SELECT * FROM applications 
        JOIN companies ON companies.id = applications.company_id 
        JOIN stages ON stages.application_id = applications.id 
        JOIN projects ON projects.id = applications.project_id 
        ORDER BY stages.id DESC) 
        WHERE company_id = ? 
        GROUP BY project_id""",
        (company_id,))


def edit_application(application_id, role, rank, memo):
    Database().commit(
        """UPDATE applications SET role = ?, rank = ?, application_memo = ? 
        WHERE id = ?""",
        (role, rank, memo, application_id))


def create_stage(application_id, status, datetime, stage_memo):
    Database().commit(
        """INSERT INTO stages (application_id, type, date, stage_memo) 
        VALUES(?, ?, ?, ?)""",
        (application_id, status, datetime, stage_memo))


def get_stage(stage_id):
    return Database.fetch_one("SELECT * FROM stages WHERE id = ?", (stage_id,))


def get_process(application_id):
    return Database.fetch_all(
        "SELECT * FROM stages WHERE application_id = ? ORDER BY id DESC",
        (application_id,))


def update_stage(stage_id, type, date, stage_memo):
    Database().commit(
        """UPDATE stages SET type = ?, date = ?, stage_memo = ? 
        WHERE id = ?""",
        (type, date, stage_memo, stage_id))
