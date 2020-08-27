def function(*args):
    print(type(args))  # args is of type tuple
    for i in args:
        print(i)
        
function(1, 2, 3, 4)


def function(**kwargs):
    print(type(kwargs))  # kwargs is of type dict
    for i in kwargs:
        print(i, kwargs[i])
        
function(a=1, b=2, c=3, d=4)
