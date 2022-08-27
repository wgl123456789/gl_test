from django.shortcuts import render
from rest_framework import viewsets,views,status
from rest_framework.response import Response
from .models import (
    Project,Host,Api,ApiRunRecord,Case,
    CaseArgument,ApiArgument,CaseRunRecord,CaseApiRunRecord,
    CrontabTask
)
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    ProjectSerializer,HostSerializer,
    ApiSerializer,ApiRunRecordSerializer,
    CaseSerializer,CaseArgumentSerializer,
    CaseRunRecordSerializer,CaseApiRunRecordSerializer,
    CrontabTaskSerializer
)
from apps.zlauth.authorizations import JWTAuthentication
from . import zlrequest
from .view_extension import run_case
from . import zlscheduler

class IndexView(views.APIView):
    def get(self,request):
        project_count = Project.objects.count()
        api_count = Api.objects.count()
        case_count = Case.objects.count()
        api_record_count = ApiRunRecord.objects.count()
        case_record_count = CaseRunRecord.objects.count()
        data = {
            'count': {
                'project': project_count,
                'api': api_count,
                'case': case_count,
                'api_record': api_record_count,
                'case_record': case_record_count
            }
        }
        return Response(data)

class ProjectViewSets(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

class HostViewSets(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = HostSerializer

class ApiViewSets(viewsets.ModelViewSet):
    queryset = Api.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ApiSerializer

class RunApiView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request,api_id):
        api = Api.objects.get(pk=api_id)
        resp = zlrequest.request(api)
        record = ApiRunRecord.objects.create(
            url=resp.url,
            http_method=resp.request.method,
            return_code=resp.status_code,
            return_content=resp.text,
            data=resp.request.body,
            headers=api.headers,
            api=api,
            user=request.user
        )
        serializer = ApiRunRecordSerializer(record)
        return Response(serializer.data)

class CaseView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            name = request.data.get('name')
            arguments = request.data.get('arguments')
            api_list = request.data.get('api_list')
            description = request.data.get('description')
            project_id = request.data.get('project_id')

            # 创建用例
            case = Case.objects.create(
                name=name,
                description=description,
                user=request.user,
                project_id=project_id
            )

            # 处理用例参数
            if arguments:
                for argument in arguments:
                    CaseArgument.objects.create(
                        name=argument['name'],
                        value=argument['value'],
                        case=case
                    )

            # 处理API列表
            if api_list:
                api_list = sorted(api_list,key=lambda x:x['index'])
                for api in api_list:
                    api_model = Api.objects.get(pk=api['id'])
                    case.api_list.add(api_model)
                    api_arguments = api['arguments']
                    if api_arguments:
                        for api_argument in api_arguments:
                            ApiArgument.objects.create(
                                name=api_argument['name'],
                                origin=api_argument['origin'],
                                format=api_argument['format'],
                                api=api_model
                            )
            case.save()
            return Response(CaseSerializer(case).data)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,case_id):
        serializer = CaseSerializer(data=request.data)
        if serializer.is_valid():
            name = request.data.get('name')
            arguments = request.data.get('arguments')
            api_list = request.data.get('api_list')
            description = request.data.get('description')

            case = Case.objects.get(pk=case_id)
            case.name = name
            case.description = description

            # 处理用例参数
            if arguments:
                argument_model_list = []
                for argument in arguments:
                    argument_id = argument['id']
                    if argument_id:
                        argument_model = CaseArgument.objects.get(pk=argument_id)
                        argument_model.name = argument['name']
                        argument_model.value = argument['value']
                        argument_model.save()
                    else:
                        argument_model = CaseArgument.objects.create(
                            name=argument['name'],
                            value=argument['value'],
                            case=case
                        )
                    argument_model_list.append(argument_model)
                case.arguments.set(argument_model_list)
            else:
                case.arguments.set([])

            # 处理API及其参数
            if api_list:
                api_model_list = []
                for api in api_list:
                    api_model = Api.objects.get(pk=api['id'])
                    api_arguments = api['arguments']
                    # 处理API参数
                    if api_arguments:
                        argument_model_list = []
                        for api_argment in api_arguments:
                            argument_id = api_argment['id']
                            if argument_id:
                                argument_model = ApiArgument.objects.get(pk=argument_id)
                                argument_model.name = api_argment['name']
                                argument_model.origin = api_argment['origin']
                                argument_model.format = api_argment['format']
                                argument_model.save()
                            else:
                                argument_model = ApiArgument.objects.create(
                                    name=api_argment['name'],
                                    origin=api_argment['origin'],
                                    format=api_argment['format'],
                                    case=case
                                )
                            argument_model_list.append(argument_model)
                        api_model.arguments.set(argument_model_list)
                    else:
                        api_model.arguments.set([])
                    # 处理完API的参数后需要重新保存
                    api_model.save()
                    api_model_list.append(api_model)
                case.api_list.set(api_model_list)
            else:
                case.api_list.set([])

            # 保存用例对象
            case.save()
            return Response(CaseSerializer(case).data)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RunCaseView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self,request,case_id):
        case_record = run_case(case_id,request)
        serializer = CaseRunRecordSerializer(case_record)
        return Response(serializer.data)

class RecordView(views.APIView):
    def get(self,request):
        record_type = request.GET.get('type')
        project_id = request.GET.get('project')
        if record_type == 'api':
            records = ApiRunRecord.objects.filter(api__project_id=project_id)
            serializer = ApiRunRecordSerializer(records,many=True)
            return Response(serializer.data)
        else:
            records = CaseRunRecord.objects.filter(case__project_id=project_id)
            serializer = CaseRunRecordSerializer(records, many=True)
            return Response(serializer.data)


class CrontabTaskView(views.APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = CrontabTaskSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            project_id = serializer.validated_data.get('project_id')
            case_id = serializer.validated_data.get('case_id')
            expr = serializer.validated_data.get('expr')
            task = CrontabTask.objects.create(
                name=name,
                project_id=project_id,
                case_id=case_id,
                expr=expr,
                user=request.user,
                status=2 # 默认情况下是不运行的
            )
            return Response(data=CrontabTaskSerializer(instance=task).data)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,task_id):
        serializer = CrontabTaskSerializer(data=request.data)
        if serializer.is_valid():
            # 可以更新的参数有：name,case_id,expr
            name = serializer.validated_data.get('name')
            case_id = serializer.validated_data.get('case_id')
            expr = serializer.validated_data.get('expr')
            # filter：QuerySet对象，get：返回ORM对象
            # filter：[ORM]，get：ORM
            # queryset.update()
            queryset = CrontabTask.objects.filter(pk=task_id)
            queryset.update(
                name=name,
                case_id=case_id,
                expr=expr
            )
            return Response(data=CrontabTaskSerializer(queryset.first()).data)
        else:
            print(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class StartStopTaskView(views.APIView):
    # 没有加authentication_classes
    # 那么request对象上绑定的就不是ZLUser了，而是匿名用户（An user）

    # 如果这个视图是需要登陆以后才能访问的，一定要把这两句加上去
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request,task_id,target_status):
        task = CrontabTask.objects.get(pk=task_id)
        # 如果是想要运行任务
        if target_status == 1:
            if task.status == 1:
                # 任务正在运行，不需要重复运行
                return Response(status=status.HTTP_400_BAD_REQUEST)
            zlscheduler.add_task(task,request)
            task.status = 1 # 更改当前任务的状态
        elif target_status == 2:
            if task.status == 2:
                # 任务已经停止，不需要重复停止
                return Response(status=status.HTTP_400_BAD_REQUEST)
            zlscheduler.remove_task(task)
            task.status = 2
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        task.save()
        return Response(CrontabTaskSerializer(task).data)






