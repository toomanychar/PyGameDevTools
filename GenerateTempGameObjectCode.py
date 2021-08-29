import inspect
import pygame
import PyGameDevToolsBlack

instance_object = PyGameDevToolsBlack.GameObject(icon=pygame.image.load('a.png'))
instance_object.update()

object_methods = []
for method_name in dir(instance_object):
    if callable(getattr(instance_object, method_name)) and not method_name.startswith('__') and inspect.ismethod(
            getattr(instance_object, method_name)):
        object_methods.append(method_name)

object_variables = list(vars(instance_object))
new_object_variables = list(object_variables)
for var in object_variables:
    value = getattr(instance_object, var)
    if type(value) in [int, float, tuple, list, bool]:
        new_object_variables.append(var + '_operation')

print(object_methods)
print(new_object_variables)

with open('TempGameObject.py', 'w') as f:
    f.write('class TempGameObject(GameObject):\n')
    f.write('    def __init__(\n')
    f.write('            self,\n')
    for var in new_object_variables:
        f.write('            ' + var + "='")
        if hasattr(instance_object, var):
            f.write("',               # " + str(type(getattr(instance_object, var))).replace("<class '", '').replace("'>", ''))
        else:
            f.write("+',")
        f.write('\n')
    f.write('    ):\n')

    for var in new_object_variables:
        f.write('        self.' + var + ' = ' + var)

        f.write('\n')
    f.write('\n')
    f.write('        self.initialized = False\n')

    f.close()



