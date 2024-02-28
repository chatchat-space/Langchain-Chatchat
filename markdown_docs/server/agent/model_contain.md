## ClassDef ModelContainer
**ModelContainer**: ModelContainer 类的功能是作为模型和数据库的容器。

**属性**:
- MODEL: 用于存储模型实例。初始值为 None，表示在创建 ModelContainer 实例时，并没有预设的模型。
- DATABASE: 用于存储数据库连接实例。初始值同样为 None，表示在创建 ModelContainer 实例时，并没有预设的数据库连接。

**代码描述**:
ModelContainer 类是一个简单的容器类，设计用来存储模型实例和数据库连接实例。这个类通过定义两个属性 `MODEL` 和 `DATABASE` 来实现其功能。这两个属性在类的初始化方法 `__init__` 中被设置为 None，这意味着在创建 ModelContainer 的实例时，这两个属性都不会持有任何值。这种设计允许开发者在创建 ModelContainer 实例后，根据需要将模型实例和数据库连接实例分别赋值给这两个属性。

**注意**:
- 在使用 ModelContainer 类时，开发者需要注意，`MODEL` 和 `DATABASE` 属性在初始状态下是 None。因此，在尝试访问这些属性或其方法之前，需要确保它们已被正确赋值，以避免遇到 `NoneType` 对象没有该方法的错误。
- ModelContainer 类提供了一种灵活的方式来管理模型和数据库连接，但它本身不提供任何方法来初始化 `MODEL` 和 `DATABASE` 属性。开发者需要根据自己的需求，手动为这两个属性赋值。
- 由于 ModelContainer 类的设计相对简单，它可以根据项目的需要进行扩展，例如添加更多的属性或方法来满足更复杂的需求。
### FunctionDef __init__(self)
**__init__**: 此函数用于初始化ModelContainer类的实例。

**参数**: 此函数不接受任何外部参数。

**代码描述**: 在ModelContainer类的实例被创建时，`__init__`函数会被自动调用。此函数主要完成以下几点初始化操作：
- 将`MODEL`属性设置为`None`。这意味着在实例化后，该属性暂时不关联任何模型，需要后续根据具体需求进行赋值。
- 将`DATABASE`属性也设置为`None`。这表明在实例化的初始阶段，该属性不关联任何数据库，同样需要在后续操作中根据需要进行关联。

通过这种方式，`__init__`函数为ModelContainer类的实例提供了一个清晰、干净的初始状态，便于后续的属性赋值和方法调用。

**注意**: 
- 在使用ModelContainer类创建实例后，需要根据实际情况给`MODEL`和`DATABASE`属性赋予具体的模型和数据库实例，以便于进行后续的操作。
- 由于`MODEL`和`DATABASE`在初始化时都被设置为`None`，在对这两个属性进行操作前，建议先检查它们是否已被正确赋值，以避免在使用未初始化的属性时引发错误。
***
