## ClassDef BaseModel
**BaseModel**: BaseModel 的功能是提供一个数据库模型的基础结构。

**属性**:
- `id`: 主键ID，用于唯一标识每个记录。
- `create_time`: 记录的创建时间。
- `update_time`: 记录的最后更新时间。
- `create_by`: 记录的创建者。
- `update_by`: 记录的最后更新者。

**代码描述**:
BaseModel 类定义了一个数据库模型的基础结构，它包含了几个常见且重要的字段。这些字段包括：
- `id` 字段使用 `Column` 函数定义，其类型为 `Integer`，并且被设置为主键（`primary_key=True`），同时启用索引（`index=True`），以便提高查询效率。此外，该字段还有一个注释（`comment="主键ID"`），用于说明字段的用途。
- `create_time` 字段记录了数据被创建的时间，其类型为 `DateTime`。该字段的默认值通过 `datetime.utcnow` 函数设置，以确保使用的是创建记录时的UTC时间。此字段同样有一个注释（`comment="创建时间"`）。
- `update_time` 字段记录了数据最后一次被更新的时间，类型也是 `DateTime`。不同的是，它的默认值设置为 `None`，并且通过 `onupdate=datetime.utcnow` 参数设置，当记录更新时，此字段会自动更新为当前的UTC时间。该字段也有相应的注释（`comment="更新时间"`）。
- `create_by` 和 `update_by` 字段用于记录数据的创建者和最后更新者的信息，它们的类型都是 `String`。默认值为 `None`，并且各自有对应的注释（`comment="创建者"` 和 `comment="更新者"`），用于说明字段的用途。

**注意**:
- 使用BaseModel时，需要注意`create_time`和`update_time`字段默认使用的是UTC时间，这意味着如果应用程序在不同的时区运行，可能需要进行相应的时区转换。
- `id`字段被设置为主键和索引，这对于数据库性能优化是非常重要的。确保每个模型都有一个唯一的标识符。
- `create_by` 和 `update_by` 字段的默认值为 `None`，在实际应用中，根据业务需求，可能需要在数据创建或更新时，显式地设置这些字段的值。
