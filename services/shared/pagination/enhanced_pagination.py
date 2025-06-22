"""
ACGS-1 Enhanced Pagination & Filtering Implementation

This module provides standardized pagination, filtering, and sorting functionality
across all ACGS-1 microservices, ensuring consistent query parameter handling,
performance optimization, and client-friendly response formats.

Features:
- Standardized pagination parameters (page, limit, offset)
- Advanced filtering with multiple operators
- Multi-field sorting with direction control
- Performance-optimized database queries
- Cursor-based pagination for large datasets
- Search functionality with full-text search
- Response metadata with navigation links
"""

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from enum import Enum

from fastapi import Query, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.orm import Query as SQLQuery
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class SortDirection(str, Enum):
    """Sort direction options."""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(str, Enum):
    """Filter operators for advanced filtering."""
    EQ = "eq"          # Equal
    NE = "ne"          # Not equal
    GT = "gt"          # Greater than
    GTE = "gte"        # Greater than or equal
    LT = "lt"          # Less than
    LTE = "lte"        # Less than or equal
    LIKE = "like"      # SQL LIKE pattern
    ILIKE = "ilike"    # Case-insensitive LIKE
    IN = "in"          # In list
    NOT_IN = "not_in"  # Not in list
    IS_NULL = "is_null"    # Is null
    IS_NOT_NULL = "is_not_null"  # Is not null
    BETWEEN = "between"    # Between two values
    CONTAINS = "contains"  # Array/JSON contains
    STARTS_WITH = "starts_with"  # String starts with
    ENDS_WITH = "ends_with"      # String ends with


class SortField(BaseModel):
    """Sort field specification."""
    field: str = Field(..., description="Field name to sort by")
    direction: SortDirection = Field(SortDirection.ASC, description="Sort direction")
    
    @validator('field')
    def validate_field_name(cls, v):
        """Validate field name to prevent SQL injection."""
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError("Invalid field name")
        return v


class FilterField(BaseModel):
    """Filter field specification."""
    field: str = Field(..., description="Field name to filter by")
    operator: FilterOperator = Field(FilterOperator.EQ, description="Filter operator")
    value: Union[str, int, float, bool, List[Any], None] = Field(..., description="Filter value")
    
    @validator('field')
    def validate_field_name(cls, v):
        """Validate field name to prevent SQL injection."""
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError("Invalid field name")
        return v


class PaginationParams(BaseModel):
    """Standardized pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    limit: int = Field(50, ge=1, le=1000, description="Items per page")
    offset: Optional[int] = Field(None, ge=0, description="Offset for cursor-based pagination")
    
    @property
    def skip(self) -> int:
        """Calculate skip value for database queries."""
        if self.offset is not None:
            return self.offset
        return (self.page - 1) * self.limit


class SearchParams(BaseModel):
    """Search parameters for full-text search."""
    query: Optional[str] = Field(None, description="Search query string")
    fields: Optional[List[str]] = Field(None, description="Fields to search in")
    fuzzy: bool = Field(False, description="Enable fuzzy search")
    highlight: bool = Field(False, description="Highlight search terms in results")


class PaginationMetadata(BaseModel):
    """Enhanced pagination metadata."""
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number")
    previous_page: Optional[int] = Field(None, description="Previous page number")
    first_page: int = Field(1, description="First page number")
    last_page: int = Field(..., description="Last page number")
    
    # Navigation URLs (to be populated by the service)
    next_url: Optional[str] = Field(None, description="URL for next page")
    previous_url: Optional[str] = Field(None, description="URL for previous page")
    first_url: Optional[str] = Field(None, description="URL for first page")
    last_url: Optional[str] = Field(None, description="URL for last page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    data: List[T] = Field(..., description="Paginated data items")
    pagination: PaginationMetadata = Field(..., description="Pagination metadata")
    filters_applied: Optional[List[FilterField]] = Field(None, description="Applied filters")
    sort_applied: Optional[List[SortField]] = Field(None, description="Applied sorting")
    search_applied: Optional[SearchParams] = Field(None, description="Applied search")
    total_query_time_ms: Optional[float] = Field(None, description="Query execution time")


class EnhancedPaginator:
    """Enhanced paginator with filtering, sorting, and search capabilities."""
    
    def __init__(self, 
                 default_limit: int = 50,
                 max_limit: int = 1000,
                 allowed_sort_fields: Optional[List[str]] = None,
                 allowed_filter_fields: Optional[List[str]] = None,
                 allowed_search_fields: Optional[List[str]] = None):
        """Initialize paginator with configuration."""
        self.default_limit = default_limit
        self.max_limit = max_limit
        self.allowed_sort_fields = allowed_sort_fields or []
        self.allowed_filter_fields = allowed_filter_fields or []
        self.allowed_search_fields = allowed_search_fields or []
    
    def create_pagination_params(self,
                                page: int = Query(1, ge=1, description="Page number"),
                                limit: int = Query(50, ge=1, le=1000, description="Items per page"),
                                offset: Optional[int] = Query(None, ge=0, description="Offset")) -> PaginationParams:
        """Create pagination parameters with validation."""
        if limit > self.max_limit:
            limit = self.max_limit
        
        return PaginationParams(page=page, limit=limit, offset=offset)
    
    def create_sort_params(self,
                          sort: Optional[str] = Query(None, description="Sort fields (field:direction,field2:direction)")) -> List[SortField]:
        """Create sort parameters from query string."""
        if not sort:
            return []
        
        sort_fields = []
        for sort_spec in sort.split(','):
            if ':' in sort_spec:
                field, direction = sort_spec.split(':', 1)
            else:
                field, direction = sort_spec, 'asc'
            
            # Validate field is allowed
            if self.allowed_sort_fields and field not in self.allowed_sort_fields:
                raise HTTPException(status_code=400, detail=f"Sorting by '{field}' is not allowed")
            
            try:
                sort_direction = SortDirection(direction.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid sort direction: {direction}")
            
            sort_fields.append(SortField(field=field, direction=sort_direction))
        
        return sort_fields
    
    def create_filter_params(self,
                           filters: Optional[str] = Query(None, description="Filters (field:operator:value,field2:operator:value)")) -> List[FilterField]:
        """Create filter parameters from query string."""
        if not filters:
            return []
        
        filter_fields = []
        for filter_spec in filters.split(','):
            parts = filter_spec.split(':', 2)
            if len(parts) != 3:
                raise HTTPException(status_code=400, detail=f"Invalid filter format: {filter_spec}")
            
            field, operator, value = parts
            
            # Validate field is allowed
            if self.allowed_filter_fields and field not in self.allowed_filter_fields:
                raise HTTPException(status_code=400, detail=f"Filtering by '{field}' is not allowed")
            
            try:
                filter_operator = FilterOperator(operator)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid filter operator: {operator}")
            
            # Parse value based on operator
            parsed_value = self._parse_filter_value(value, filter_operator)
            
            filter_fields.append(FilterField(field=field, operator=filter_operator, value=parsed_value))
        
        return filter_fields
    
    def create_search_params(self,
                           search: Optional[str] = Query(None, description="Search query"),
                           search_fields: Optional[str] = Query(None, description="Fields to search in"),
                           fuzzy: bool = Query(False, description="Enable fuzzy search")) -> Optional[SearchParams]:
        """Create search parameters."""
        if not search:
            return None
        
        fields = None
        if search_fields:
            fields = search_fields.split(',')
            # Validate search fields
            if self.allowed_search_fields:
                invalid_fields = set(fields) - set(self.allowed_search_fields)
                if invalid_fields:
                    raise HTTPException(status_code=400, detail=f"Search in fields {invalid_fields} is not allowed")
        
        return SearchParams(query=search, fields=fields, fuzzy=fuzzy)
    
    def apply_pagination(self, query: SQLQuery, pagination: PaginationParams) -> SQLQuery:
        """Apply pagination to SQLAlchemy query."""
        return query.offset(pagination.skip).limit(pagination.limit)
    
    def apply_sorting(self, query: SQLQuery, sort_fields: List[SortField], model_class) -> SQLQuery:
        """Apply sorting to SQLAlchemy query."""
        for sort_field in sort_fields:
            if hasattr(model_class, sort_field.field):
                column = getattr(model_class, sort_field.field)
                if sort_field.direction == SortDirection.DESC:
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
        
        return query
    
    def apply_filters(self, query: SQLQuery, filter_fields: List[FilterField], model_class) -> SQLQuery:
        """Apply filters to SQLAlchemy query."""
        for filter_field in filter_fields:
            if hasattr(model_class, filter_field.field):
                column = getattr(model_class, filter_field.field)
                condition = self._build_filter_condition(column, filter_field)
                if condition is not None:
                    query = query.filter(condition)
        
        return query
    
    def create_pagination_metadata(self, 
                                 pagination: PaginationParams, 
                                 total_items: int,
                                 base_url: Optional[str] = None) -> PaginationMetadata:
        """Create pagination metadata with navigation information."""
        total_pages = math.ceil(total_items / pagination.limit) if total_items > 0 else 1
        
        metadata = PaginationMetadata(
            page=pagination.page,
            limit=pagination.limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_previous=pagination.page > 1,
            next_page=pagination.page + 1 if pagination.page < total_pages else None,
            previous_page=pagination.page - 1 if pagination.page > 1 else None,
            first_page=1,
            last_page=total_pages
        )
        
        # Generate navigation URLs if base_url provided
        if base_url:
            metadata.first_url = f"{base_url}?page=1&limit={pagination.limit}"
            metadata.last_url = f"{base_url}?page={total_pages}&limit={pagination.limit}"
            
            if metadata.next_page:
                metadata.next_url = f"{base_url}?page={metadata.next_page}&limit={pagination.limit}"
            
            if metadata.previous_page:
                metadata.previous_url = f"{base_url}?page={metadata.previous_page}&limit={pagination.limit}"
        
        return metadata
    
    def _parse_filter_value(self, value: str, operator: FilterOperator) -> Any:
        """Parse filter value based on operator type."""
        if operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            return None
        
        if operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            return value.split('|')
        
        if operator == FilterOperator.BETWEEN:
            parts = value.split('|')
            if len(parts) != 2:
                raise HTTPException(status_code=400, detail="BETWEEN operator requires two values separated by |")
            return parts
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # Try to parse as boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        return value
    
    def _build_filter_condition(self, column, filter_field: FilterField):
        """Build SQLAlchemy filter condition."""
        operator = filter_field.operator
        value = filter_field.value
        
        if operator == FilterOperator.EQ:
            return column == value
        elif operator == FilterOperator.NE:
            return column != value
        elif operator == FilterOperator.GT:
            return column > value
        elif operator == FilterOperator.GTE:
            return column >= value
        elif operator == FilterOperator.LT:
            return column < value
        elif operator == FilterOperator.LTE:
            return column <= value
        elif operator == FilterOperator.LIKE:
            return column.like(f"%{value}%")
        elif operator == FilterOperator.ILIKE:
            return column.ilike(f"%{value}%")
        elif operator == FilterOperator.IN:
            return column.in_(value)
        elif operator == FilterOperator.NOT_IN:
            return ~column.in_(value)
        elif operator == FilterOperator.IS_NULL:
            return column.is_(None)
        elif operator == FilterOperator.IS_NOT_NULL:
            return column.isnot(None)
        elif operator == FilterOperator.BETWEEN:
            return column.between(value[0], value[1])
        elif operator == FilterOperator.STARTS_WITH:
            return column.like(f"{value}%")
        elif operator == FilterOperator.ENDS_WITH:
            return column.like(f"%{value}")
        
        return None


# Export main classes and functions
__all__ = [
    "EnhancedPaginator",
    "PaginationParams",
    "PaginatedResponse",
    "PaginationMetadata",
    "SortField",
    "FilterField",
    "SearchParams",
    "SortDirection",
    "FilterOperator"
]
