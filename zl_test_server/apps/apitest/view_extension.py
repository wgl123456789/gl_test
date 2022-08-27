from .models import Case,CaseArgument,CaseRunRecord,CaseApiRunRecord
from . import zlrequest
from utils import dictor

def run_case(case_id,request):
    case = Case.objects.get(pk=case_id)
    case_arguments = CaseArgument.objects.filter(case=case)
    case_record = CaseRunRecord.objects.create(case=case)

    global_arguments = {}
    # 添加用例参数
    for case_argument in case_arguments:
        global_arguments[case_argument.name] = case_argument.value

    # 运行API以及添加API参数
    api_model_list = case.api_list.all()
    for api_model in api_model_list:
        resp = zlrequest.request(api_model, global_arguments)
        CaseApiRunRecord.objects.create(
            url=resp.url,
            http_method=resp.request.method,
            data=resp.request.body,
            headers=resp.request.headers,
            user=request.user,
            return_code=resp.status_code,
            return_content=resp.text,
            api=api_model,
            case_record=case_record
        )
        # 运行API后，看下是否还有参数需要提取
        api_arguments = api_model.arguments.all()
        if api_arguments:
            for api_argument in api_arguments:
                dictor_data = {}
                if api_argument.origin == 'HEAD':
                    dictor_data = resp.headers
                elif api_argument.origin == 'COOKIE':
                    dictor_data = resp.cookies
                elif api_argument.origin == 'BODY':
                    dictor_data = resp.json()
                argument_value = dictor.dictor(dictor_data, api_argument.format)
                global_arguments[api_argument.name] = argument_value
                # {"token": "xxxx"} => token
    return case_record