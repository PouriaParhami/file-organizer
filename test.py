class MyClass:
    def __init__(self, message):
        self.message = message

    def my_decorator(func):  # Corrected: Accept 'self'
        def wrapper(self, *args, **kwargs):
            print(f"Before: {self.message}")
            result = func(self, *args, **kwargs)
            print(f"After: {self.message}")
            return result
        return wrapper

    @my_decorator
    def greet(self):
        print("Hello from greet!")

my_object = MyClass("Custom Message")
my_object.greet()