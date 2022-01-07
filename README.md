# apico [![Badge](https://img.shields.io/pypi/v/apico?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/apico/)  [![Badge 2](https://img.shields.io/pypi/dm/apico?color=3776AB&logo=python&style=for-the-badge)](https://pypi.org/project/apico/)
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
    

monitor.start()
```

## Some reference
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
### Monitor arguments
The monitor accepts a boatload of arguments, mainly ones that are then passed down to [`requests.Session.request()`](https://docs.python-requests.org/en/latest/api/#requests.Session.request), so, for a detailed insight follow the hyperlink or read the docstring.

### Returns
The responses returned by apico are actually instances of [`requests.Response`](https://pypi.org/project/requests/)

### Rate
The rate at which the Monitor sends requests is controlled via the `rate` parameter, which is either an integer, or a float - `33` is a request every 33 seconds, `0.5` is 2 requests every second.

_________________
## Reporting Issues
If you find any error/bug/mistake with the package or in the code feel free to create an issue and report
it [here.](https://github.com/itsmewulf/apico/issues)

## Fix/Edit Content
If you wish to contribute to this package, fork the repository, make your changes and then simply create a Pull Request!
