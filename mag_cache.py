from functools import wraps
import inspect
import datetime

def mag_cache(cache_time=10):
    '''
       this is decorator fucnction, it can cache key and set the cache_time.
       Arguments to the cached function must be hashable.
    '''
    def _cache(fn):

        cache_dict = {}
        @wraps(fn)
        def wrapper(*args, **kwargs):
            def _expire_key():
                expired_keys = []

                for e_key, (_, e_time) in cache_dict.items():
                    if (datetime.datetime.now() - e_time).total_seconds() > cache_time:
                        expired_keys.append(e_key)

                for k in expired_keys:
                    cache_dict.pop(k)
            _expire_key()

            def _make_key():
                #初始化定义参数字典
                local_dict = {}

                #位置参数的处理
                sign = inspect.signature(fn)
                sign_parm = sign.parameters  #签名有序字典
                parm_list = [key for key in sign_parm.keys()]

                for i, v in enumerate(args):
                    k = parm_list[i]
                    local_dict[k] = v

                #关键字参数处理
                local_dict.update(kwargs)

                #默认参数处理
                for k in parm_list:
                    if k not in local_dict.keys():
                        local_dict[k] = sign_parm[k].default

                return tuple(sorted(local_dict.items()))
            key = _make_key()

            if key not in cache_dict.keys():
                ret = fn(*args, **kwargs)
                cache_dict[key] = (ret, datetime.datetime.now())

            return cache_dict[key]
        return wrapper
    return _cache
