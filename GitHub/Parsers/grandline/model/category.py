import time

import grandline_parser_control_module as module
from typing import List
from pydantic import BaseModel
from typing import Union


class Category(BaseModel):
    id: int
    parent_id: int = None
    name: str
    children: List['Category'] = []

    @classmethod
    def from_xml_element(cls, xml_element):
        return cls(
            id=int(xml_element.attrib.get('id')),
            parent_id=xml_element.attrib.get('parentId') or None,
            name=xml_element.text.strip()
        )


# Функция для построения иерархии категорий
def build_category_hierarchy(category_list: List[Category]) -> List[Category]:
    category_dict = {}
    root_categories = []

    # Создание словаря категорий с ссылками на дочерние категории
    for category in category_list:

        # time.sleep(module.PAUSE)

        if category.parent_id is None:
            root_categories.append(category)
        else:
            parent_category = category_dict.get(category.parent_id)
            if parent_category:
                parent_category.children.append(category)
            else:
                root_categories.append(category)
        category_dict[category.id] = category

    return root_categories


# Функция для поиска категории по ID
def find_category_by_id(category_id: int, categories: List[Category]) -> Union[Category, None]:
    for category in categories:

        # time.sleep(module.PAUSE)

        if category.id == category_id:
            return category
        if category.children:
            subcategory = find_category_by_id(category_id, category.children)
            if subcategory:
                return subcategory
    return None


hierarchy_category = []


def find_parent_categories(category_hierarchy, category: Category) -> Union[List, None]:
    if not category:
        return None
    parent_categories = []
    parent_category = find_category_by_id(category.parent_id, category_hierarchy)
    if parent_category:
        parent_categories.append(parent_category.name)
        parent_categories.extend(find_parent_categories(category_hierarchy, parent_category))
    return parent_categories
