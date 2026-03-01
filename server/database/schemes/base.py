import server.database.schemes.common_schemes as cs
import server.database.models.common_models as cm
import server.database.models.roles as roles


schemes_models = {  # Соответствие моделей и схем
    cm.Base: cs.BaseSchema(),
    cm.PersonalDailyEvent: cs.PersonalDailyEventSchema(),
    cm.PersonalManyDaysEvent: cs.PersonalManyDaysEventSchema(),
    cm.PersonalTask: cs.PersonalTaskSchema(),
    cm.PersonalWorkDirection: cs.PersonalWorkDirectionSchema(),
    cm.Project: cs.ProjectSchema(),
    cm.User: cs.UserSchema(),
    cm.WSBaseCategory: cs.WSBaseCategorySchema(),
    cm.WSDailyEvent: cs.WSDailyEventSchema(),
    cm.WSDocument: cs.WSDocumentSchema(),
    cm.WSManyDaysEvent: cs.WSManyDaysEventSchema(),
    cm.WSTask: cs.WSTaskSchema(),
    cm.WSWorkDirection: cs.WSWorkDirectionSchema(),
    cm.Workspace: cs.WorkspaceSchema(),
    roles.wsRole: cs.wsRoleSchema(),
}


if __name__ == '__main__':
    for model in dir(cm):
        print(f'cm.{model}: cs.{model}Schema(),')
    for model in dir(roles):
        print(f'roles.{model}: cs.{model}Schema(),')


