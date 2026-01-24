import server.database.schemes.common_schemes as cs
import server.database.models.common_models as cm
import server.database.models.roles as roles


schemes_models = {  # Соответствие моделей и схем
    cm.User: cs.UserSchema(),
    cm.PersonalTask: cs.PersonalTaskSchema(),
    cm.WFTask: cs.WFTaskSchema(),
    cm.Workflow: cs.WorkflowSchema(),
    roles.WFRole: cs.WFRoleSchema(),
}
