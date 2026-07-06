import gc


gc.collect()
exec(open("main.py").read(), globals())
