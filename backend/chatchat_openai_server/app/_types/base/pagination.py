from typing import List, Dict, Any


class Pagination:
    def __init__(
            self,
            total: int,
            page: int,
            per_page: int,
            data: List[Any],
            filters: Dict[str, Any] = None
    ):
        self.total = total
        self.page = page
        self.per_page = per_page
        self.data = data
        self.filters = filters or {}

    @property
    def total_pages(self) -> int:
        """计算总页数"""
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_next(self) -> bool:
        """判断是否有下一页"""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """判断是否有上一页"""
        return self.page > 1

    def to_dict(self) -> Dict[str, Any]:
        """将 Pagination 对象转换为字典"""
        return {
            'total': self.total,
            'page': self.page,
            'per_page': self.per_page,
            'total_pages': self.total_pages,
            'has_next': self.has_next,
            'has_prev': self.has_prev,
            'data': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.data],
            'filters': self.filters
        }
