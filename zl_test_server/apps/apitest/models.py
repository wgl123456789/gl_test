from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

HTTP_METHOD_CHOICE = (
    ('POST', 'POST'),
    ('GET', 'GET'),
    ('PUT', 'PUT'),
    ('DELETE', 'DELETE')
)

class Project(models.Model):
    """
    项目表
    """
    ProjectType = (
        ('web', 'web'),
        ('app', 'app')
    )
    name = models.CharField(max_length=50, verbose_name='项目名称')
    type = models.CharField(max_length=50, verbose_name='项目类型', choices=ProjectType)
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    last_update_time = models.DateTimeField(auto_now=True, verbose_name='最近修改时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')

class Host(models.Model):
    """
    host域名
    """
    name = models.CharField(max_length=50, verbose_name='名称')
    host = models.CharField(max_length=1024, verbose_name='Host地址')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目',related_name='host_list')

class Api(models.Model):
    """
    接口信息
    """
    STATUS_CODE_CHOICE = (
        ('200', '200'),
        ('201', '201'),
        ('202', '202'),
        ('203', '203'),
        ('204', '204'),
        ('301', '301'),
        ('302', '302'),
        ('400', '400'),
        ('401', '401'),
        ('403', '403'),
        ('404', '404'),
        ('405', '405'),
        ('406', '406'),
        ('407', '407'),
        ('408', '408'),
        ('500', '500'),
        ('502', '502')
    )
    name = models.CharField(max_length=50, verbose_name='接口名称')
    http_method = models.CharField(max_length=50, verbose_name='请求方式', choices=HTTP_METHOD_CHOICE)
    host = models.ForeignKey(Host,on_delete=models.CASCADE,verbose_name='host')
    path = models.CharField(max_length=1024, verbose_name='接口地址')
    headers = models.TextField(null=True,blank=True,verbose_name='请求头')
    data = models.TextField(null=True,blank=True,verbose_name='提交的数据')
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    expect_code = models.CharField(default=200,max_length=10,verbose_name='期望返回的code',choices=STATUS_CODE_CHOICE)
    expect_content = models.CharField(null=True,max_length=200,verbose_name='期望返回的内容',blank=True)
    project = models.ForeignKey(Project,on_delete=models.CASCADE,verbose_name='项目',related_name='api_list',null=True)

class ApiRunRecord(models.Model):
    """
    API运行记录
    """
    url = models.CharField(max_length=200,verbose_name='请求的url！')
    http_method = models.CharField(max_length=10, verbose_name='请求方式', choices=HTTP_METHOD_CHOICE)
    data = models.TextField(null=True,verbose_name='提交的数据')
    headers = models.TextField(null=True,verbose_name='提交的header')
    create_time = models.DateTimeField(auto_now=True,verbose_name='运行的时间')
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='执行命令的人')
    return_code = models.CharField(max_length=10,verbose_name='返回的code')
    return_content = models.TextField(null=True,verbose_name='返回的内容')
    api = models.ForeignKey(Api,on_delete=models.CASCADE,verbose_name='关联的API',null=True)

    class Meta:
        ordering = ['-create_time']

class Case(models.Model):
    """
    自动化测试用例
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='所属项目',related_name='case_list')
    name = models.CharField(max_length=50, verbose_name='用例名称')
    api_list = models.ManyToManyField(Api,related_name='case_list')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="创建人")
    description = models.CharField(max_length=1024, blank=True, null=True, verbose_name='描述')
    create_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

class CaseArgument(models.Model):
    """
    用例的参数
    """
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name='用例', null=True,related_name='arguments')
    name = models.CharField(max_length=100,verbose_name='参数名字')
    value = models.CharField(max_length=100,verbose_name='参数的值')

class ApiArgument(models.Model):
    """
    用例API的参数
    """
    ARGUMENT_ORIGIN_CHOICE = (
        ('HEADER', 'HEADER'),
        ('BODY', 'BODY'),
        ('COOKIE', 'COOKIE')
    )
    api = models.ForeignKey(Api,on_delete=models.CASCADE,verbose_name='用例API',null=True,related_name='arguments')
    name = models.CharField(max_length=100,verbose_name='参数名字')
    origin = models.CharField(max_length=20,choices=ARGUMENT_ORIGIN_CHOICE,verbose_name='参数来源')
    format = models.CharField(max_length=100,verbose_name='参数获取的格式')


class CaseRunRecord(models.Model):
    """
    用例运行记录
    """
    case = models.ForeignKey(Case,on_delete=models.CASCADE,verbose_name='所属用例')
    create_time = models.DateTimeField(auto_now=True,verbose_name='运行时间')

    class Meta:
        ordering = ['-create_time']

class CaseApiRunRecord(models.Model):
    """
    Case API运行记录
    """
    url = models.CharField(max_length=200, verbose_name='请求的url！')
    http_method = models.CharField(max_length=10, verbose_name='请求方式', choices=HTTP_METHOD_CHOICE)
    headers = models.TextField(null=True,verbose_name='请求头')
    data = models.TextField(null=True, verbose_name='提交的数据')
    create_time = models.DateTimeField(auto_now=True, verbose_name='运行的时间')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='执行命令的人')
    return_code = models.CharField(max_length=10, verbose_name='返回的code')
    return_content = models.TextField(null=True, verbose_name='返回的内容')
    api = models.ForeignKey(Api, on_delete=models.CASCADE, verbose_name='关联的API', null=True)
    case_record = models.ForeignKey(CaseRunRecord,on_delete=models.CASCADE,verbose_name='关联的case_record',related_name='api_records')

CRONTAB_TASK_STATUS = (
    (1,1), # 运行
    (2,2), # 停止
)

class CrontabTask(models.Model):
    """
    定时任务模型
    1. 定时执行API
    2. 定时执行用例
    3. 定时执行测试集

    任务触发方式：date,interval,crontab
    我们用crontab的表达式
    需要用json的格式："{"second":"*/1","hour":"12"}"
    先将这个json load成字典
    dict = json.loads(json_str)
    dict = {"second":"*/1","hour":"12"}
    scheduler.add_job(func,trigger="cron",second="*/1",hour="12")
    scheduler.add_job(func,trigger="cron",**dict)
    """
    name = models.CharField(max_length=100,verbose_name='任务名称')
    project = models.ForeignKey(Project,on_delete=models.CASCADE,verbose_name='所属的项目',related_name='task_list')
    case = models.ForeignKey(Case,on_delete=models.CASCADE,verbose_name='定时执行的用例')
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='任务创建者')
    create_time = models.DateTimeField(auto_now=True,verbose_name='创建时间')
    expr = models.CharField(max_length=200,verbose_name='任务执行表达式')
    status = models.SmallIntegerField(choices=CRONTAB_TASK_STATUS,verbose_name='任务的状态',default=2)


















