from application import app
from application import model


def get_user_by_id(id):
    return model.get_user_with_id(id)


def get_user_by_username(username):
    return model.get_user_with_username(username)


def register_user(username, hashed_password):
    model.register_user(username, hashed_password)


def create_project(user_id, created_on, name, memo):
    model.create_project(user_id, created_on, name, memo)


def get_project(project_id):
    return model.get_project(project_id)


def get_all_projects(user_id):
    return model.get_all_projects(user_id)


def create_company(company_name):
    model.create_company(company_name)


def get_company_id(company_name):
    return model.get_company_id(company_name)


def create_application(project_id, company_id, role, memo, rank, application_status, datetime):
    # TODO: handle error, return response
    model.create_application(project_id, company_id, role, memo, rank)
    application_id = get_application_id(project_id, company_id)
    create_process(application_id, application_status, datetime)


def get_application(project_id, company_id):
    return model.get_application(project_id, company_id)


def get_application_id(project_id, company_id):
    return model.get_application_id(project_id, company_id)


def get_all_applications(project_id):
    return model.get_all_applications(project_id)


def create_process(application_id, status, datetime):
    model.create_process(application_id, status, datetime)