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
    cm.WFBaseCategory: cs.WFBaseCategorySchema(),
    cm.WFDailyEvent: cs.WFDailyEventSchema(),
    cm.WFDocument: cs.WFDocumentSchema(),
    cm.WFManyDaysEvent: cs.WFManyDaysEventSchema(),
    cm.WFTask: cs.WFTaskSchema(),
    cm.WFWorkDirection: cs.WFWorkDirectionSchema(),
    cm.Workflow: cs.WorkflowSchema(),
    roles.WFRole: cs.WFRoleSchema(),
}


if __name__ == '__main__':
    for model in dir(cm):
        print(f'cm.{model}: cs.{model}Schema(),')
    for model in dir(roles):
        print(f'roles.{model}: cs.{model}Schema(),')


