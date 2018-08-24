import functools
def logger(duration, func=lambda name, duration: print('{} took {}s'.format(name, duration))):
	def _logger(fn):
		@functools.wraps(fn)
		def wrapper(*args,**kwargs):
			start = datetime.datetime.now()
			ret = fn(*args,**kwargs)
			delta = (datetime.datetime.now() - start).total_seconds()
			if delta > duration:
				func(fn.__name__, duration)
			return ret
		return wrapper
	return _logger
