# AItems

Is a KivyMD derived UI widget which brings drag and drop and scrollable 
functionality to MDList.

For now it expects to by only one such an element on a screen.


## Installation

```
pip install git+https://github.com/patrikflorek/aitems
```


## Usage

```
from aitems.dragndrop.list import ScrollableDragNDropListContainer

dragndrop = ScrollableDragNDropListContainer('IconRightWidget')

data = [...]
dragndrop.set_list_data(list_data=data)
```


## Demo app

### When installed using pip

```
cd venv/lib/python3.x/site_packages/aitems

python3 -m demo.dragndrop
```

### When installed manually

```
git clone git@github.com:patrikflorek/aitems.git aitems

cd aitems

python3 -m virtualenv venv

source venv/bin/activate

pip install kivymd

cd aitems

python -m demo.dragndrop
```