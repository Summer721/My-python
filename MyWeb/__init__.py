from webob import Request, Response, exc
from webob.dec import wsgify
import re

class DictObj:
    def __init__(self, d:dict):
        if not isinstance(d, dict):
            self.__dict__['_dict'] = {}
        else:
            self.__dict__['_dict'] = d

    def __getattr__(self, item):
        try:
            return self._dict[item]
        except KeyError:
            raise AttributeError('Attribute {} not fount'.format(item))

    def __setattr__(self, key, value):
        # 不允许设置属性
        raise NotImplementedError

#将dict转换为.形式访问属性
class Context(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('Attribute {} not fount'.format(item))

    def __setattr__(self, key, value):
        self[key] = value


class NestedContext(Context):
    def __init__(self, globalcontext: Context=None):
        super().__init__()
        self.relate(globalcontext)

    def relate(self, globalcontext: Context=None):
        self.globalcontext = globalcontext

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        return self.globalcontext[item]

class _Router:
    # 各个类型的正则表达式表示
    TYPEPATTERNS = {
        'str': r'[^/]+', 'word': r'\w+', 'int': r'[-+]?\d+', 'float': r'[-+]?\d+\.\d+', 'any': r'.+'
    }
    # 对应处理的函数
    TYPECAST = {
        'str': str, 'word': str, 'int': int, 'float': float, 'any': str
    }

    KVPATTERN = re.compile(r'/({[^{}:]+:?[^{}:]*})')

    def _transform(self, kv: str):
        name, _, type = kv.strip('/{}').partition(':')
        return '/(?P<{}>{})'.format(name, self.TYPEPATTERNS.get(type, '\w+')), name, self.TYPECAST.get(type, str)

    def _parse(self, src: str):
        start = 0
        res = ''
        translator = {}
        while True:
            matcher = self.KVPATTERN.search(src, start)
            if matcher:
                res += matcher.string[start:matcher.start()]
                tmp = self._transform(matcher.string[matcher.start():matcher.end()])
                res += tmp[0]
                translator[tmp[1]] = tmp[2]
                start = matcher.end()

            else:
                break
        if res:
            return res, translator
        else:
            return src, translator

    def __init__(self, prefix: str=''):
        self.__prefix = prefix.rstrip('/\\')
        self.__routetable = []

        #拦截器
        self.pre_interceptor = []
        self.post_interceptor = []

        #上下文
        self.ctx = NestedContext()

    def register_preinterceptor(self, fn):
        self.pre_interceptor.append(fn)
        return fn

    def register_postinterceptor(self, fn):
        self.post_interceptor.append(fn)
        return fn

    def route(self, rule, *methods):
        def wrapper(handler):
            pattern, translator= self._parse(rule)
            self.__routetable.append((methods, re.compile(pattern), translator, handler))
            return handler
        return wrapper

    def get(self, pattern):
        return self.route(pattern, 'GET')

    def post(self, pattern):
        return self.route(pattern, 'POST')

    def head(self, pattern):
        return self.route(pattern, 'HEAD')

    def match(self, request: Request):
        # 前缀处理，prefix是一级的
        if not request.path.startswith(self.__prefix):
            return None

        # 依次拦截请求
        for fn in self.pre_interceptor:
            request = fn(self.ctx, request)

        for methods, pattern, translator, handler in self.__routetable:
            if not methods or request.method.upper() in methods:
                matcher = pattern.match(request.path.replace(self.__prefix, '', 1))
                if matcher:
                    newdict = {}
                    for k,v in matcher.groupdict().items():
                        newdict[k] = translator[k](v)
                    request.vars = DictObj(newdict)
                    response = handler(self.ctx, request)

                    #拦截器
                    for  fn in self.post_interceptor:
                        response = fn(self.ctx, request, response)

                    return response
                #匹配不上默认返回None

class MagWeb:
    # 类属性的方式把类暴露出去
    Router = _Router
    Request = Request
    Response = Response

    ctx = Context() #全局上下文对象
    def __init__(self, **kwargs):
        # 创建上下文对象，共享信息
        self.ctx.app = self
        for k, v in kwargs:
            self.ctx[k] = v
    ROUTERS = []

    PRE_INTERCEPTOR = []
    POST_INTERCEPTOR = []

    # 拦截器注册函数
    @classmethod
    def register_preinterceptor(cls, fn):
        cls.PRE_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def register_postinterceptor(cls, fn):
        cls.POST_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def register(cls, router :_Router):
        router.ctx.relate(cls.ctx)
        router.ctx.router = router
        cls.ROUTERS.append(router)

    @wsgify
    def __call__(self, request: Request):
        #全局拦截请求
        for fn in self.PRE_INTERCEPTOR:
            request = fn(self.ctx, request)

        #遍历ROUTERS, 调用Router实例的match方法，看谁匹配
        for router in self.ROUTERS:
            response = router.match(request)

            for fn in self.POST_INTERCEPTOR:
                response = fn(self.ctx, request, response)

            if response:
                return response
        raise exc.HTTPNotFound('Not found')

    @classmethod
    def extend(cls, name, ext):
        cls.ctx[name] = ext

