# apico
*The easy way to monitor changes in RESTful APIs.*

## Installation
```
$ pip install apico
```
## Example usage 
```py
from apico import Monitor, Response


monitor = Monitor(url='https://api.github.com/users/itsmewulf', rate=10.0, headers={'Authorization': 'GITHUB_TOKEN'})

@monitor.listener()
def on_change(old, new):
    print('Something changed!')
    
@monitor.listener('no_change')
def nothing_changed():
    print('Nothing changed!')
    
@monitor.listener()
def on_request():
    print('This is called before every request.')
```

## Some reference
Below you'll find some insight that might not be instantly apparent.

### Events
The events supported by the `Monitor.listener` decorator are:
- `change`
- `request`
- `no_change`  

As you can see in the example, listeners can be registered by passing the event name straight to the decorator (`monitor.listener('change')`) or inferred from the function name starting with `on_`:
```py
@monitor.listener()
def on_change(...):
```

### Returns
The responses returned by apico are actually instances of [`requests.Response`](https://pypi.org/project/requests/)
_________________
## Reporting Issues
If you find any error/bug/mistake with the package or in the code feel free to create an issue and report
it [here.](https://github.com/itsmewulf/apico/issues)

## Fix/Edit Content
If you wish to contribute to this package, fork the repository, make your changes and then simply create a Pull Request!
