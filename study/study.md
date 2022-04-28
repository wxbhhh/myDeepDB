## new操作符
C++中利用==new==操作符在堆区开辟数据
堆区开辟的数据，由程序员手动开辟，手动释放，释放利用操作符delete \
语法： new 数据类型\
利用new创建的数据，会返回该数据对应的类型的指针

示例1： 基本语法
```
int* func()
{
    int* a = new int(10);
    return a;
}
int main() {
    int *p = func();
    cout << *p << endl;
    cout << *p << endl;
    system("pause");
    return 0;
}
```
示例2：开辟数组 \
```
int* func()
{
    int* a = new int(10);
    return a;
}
int main() {
    int *p = func();
    cout << *p << endl;
    cout << *p << endl;
    //利用delete释放堆区数据
    delete p;
    //cout << *p << endl; //报错，释放的空间不可访问
    system("pause");
    return 0;
}
```


## 引用
### 引用的基本使用
作用： 给变量起别名\
语法：  数据类型 &别名 = 原名\
示例：
## 引用注意事项
引用必须初始化\
示例：
```
int main() {
    int a = 10;
    int &b = a;
    cout << "a = " << a << endl;
    cout << "b = " << b << endl;
    b = 100;
    cout << "a = " << a << endl;
    cout << "b = " << b << endl;
    system("pause");
    return 0;
}
```

引用在初始化后，不可以改变
示例
```
int main() {
    int a = 10;
    int b = 20;
    //int &c; //错误，引用必须初始化
    int &c = a; //一旦初始化后，就不可以更改
    c = b; //这是赋值操作，不是更改引用
    cout << "a = " << a << endl;
    cout << "b = " << b << endl;
    cout << "c = " << c << endl;
    system("pause");
    return 0;
    }
```

## 引用做函数参数
作用：函数传参时，可以利用引用的技术让形参修饰实参\
优点：可以简化指针修改实参\
示例：
```
//1. 值传递
void mySwap01(int a, int b) {
    int temp = a;
    a = b;
    b = temp;
}
//2. 地址传递
void mySwap02(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}
//3. 引用传递
void mySwap03(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}
int main() {
    int a = 10;
    int b = 20;
    mySwap01(a, b);
    cout << "a:" << a << " b:" << b << endl;
    mySwap02(&a, &b);
    cout << "a:" << a << " b:" << b << endl;
    angular2html
    mySwap03(a, b);
    cout << "a:" << a << " b:" << b << endl;
    system("pause");
    return 0;
}
```
总结：通过引用参数产生的效果同按地址传递是一样的。引用的语法更清楚简单
## 引用做函数返回值
作用：引用是可以作为函数的返回值存在的\
注意：不要返回局部变量引用\
用法：函数调用作为左值\
示例：
```
//返回局部变量引用
int& test01() {
int a = 10; //局部变量
return a;
}
//返回静态变量引用
int& test02() {
    static int a = 20;
    return a;
}
int main() {
    //不能返回局部变量的引用
    int& ref = test01();
    cout << "ref = " << ref << endl;
    cout << "ref = " << ref << endl;
    //如果函数做左值，那么必须返回引用
    int& ref2 = test02();
    cout << "ref2 = " << ref2 << endl;
    cout << "ref2 = " << ref2 << endl;
    test02() = 1000;
    cout << "ref2 = " << ref2 << endl;
    cout << "ref2 = " << ref2 << endl;
    system("pause");
    return 0;
}
```

## 引用的本质
本质：引用的本质在c++内部实现是一个指针常量.\
讲解示例：
```
//发现是引用，转换为 int* const ref = &a;
void func(int& ref){
    ref = 100; // ref是引用，转换为*ref = 100
}
int main(){
    int a = 10;
    //自动转换为 int* const ref = &a; 指针常量是指针指向不可改，也说明为什么引用不可更改
    int& ref = a;
    ref = 20; //内部发现ref是引用，自动帮我们转换为: *ref = 20;
    cout << "a:" << a << endl;
    cout << "ref:" << ref << endl;
    func(a);
    return 0;
}
```
## 常量引用
作用：常量引用主要用来修饰形参，防止误操作\
在函数形参列表中，可以加const修饰形参，防止形参改变实参\
示例：
```
//引用使用的场景，通常用来修饰形参
void showValue(const int& v) {
    //v += 10;
    cout << v << endl;
}
int main() {
    //int& ref = 10; 引用本身需要一个合法的内存空间，因此这行错误
    //加入const就可以了，编译器优化代码，int temp = 10; const int& ref = temp;
    const int& ref = 10;
    //ref = 100; //加入const后不可以修改变量
    cout << ref << endl;
    //函数中利用常量引用防止误操作修改实参
    int a = 10;
    showValue(a);
    system("pause");
    return 0;
}
```
## 函数默认参数
在C++中，函数的形参列表中的形参是可以有默认值的。\
语法： 返回值类型 函数名 （参数= 默认值）{}\
### 函数占位参数
C++中函数的形参列表里可以有占位参数，用来做占位，调用函数时必须填补该位置
语法：  返回值类型 函数名 (数据类型){}
在现阶段函数的占位参数存在意义不大，但是后面的课程中会用到该技术
示例：
```
int func(int a, int b = 10, int c = 10) {
    return a + b + c;
}

//1. 如果某个位置参数有默认值，那么从这个位置往后，从左向右，必须都要有默认值
//2. 如果函数声明有默认值，函数实现的时候就不能有默认参数
int func2(int a = 10, int b = 10);
int func2(int a, int b) {
    return a + b;
}
int main() {
    cout << "ret = " << func(20, 20) << endl;
    cout << "ret = " << func(100) << endl;
    system("pause");
    return 0;
}

```

## 函数重载
3.3.1 函数重载概述
作用：函数名可以相同，提高复用性
函数重载满足条件：\
++ 同一个作用域下\
++ 函数名称相同\
++ 函数参数类型不同 或者 个数不同 或者 顺序不同\
注意: 函数的返回值不可以作为函数重载的条件
示例：
```
//函数占位参数 ，占位参数也可以有默认参数
void func(int a, int) {
    cout << "this is func" << endl;
}
int main() {
    func(10,10); //占位参数必须填补
    system("pause");
    return 0;
}
//函数重载需要函数都在同一个作用域下
void func()
{
    cout << "func 的调用！" << endl;
}
void func(int a)
{
    cout << "func (int a) 的调用！" << endl;
}
void func(double a)
{
    cout << "func (double a)的调用！" << endl;
}
void func(int a ,double b)
{
    cout << "func (int a ,double b) 的调用！" << endl;
}
void func(double a ,int b)
{
    cout << "func (double a ,int b)的调用！" << endl;
}
```
## 函数重载注意事项
引用作为重载条件
函数重载碰到函数默认参数
示例：
```
//函数返回值不可以作为函数重载条件
//int func(double a, int b)
//{
//  cout << "func (double a ,int b)的调用！" << endl;
//}
int main() {
    func();
    func(10);
    func(3.14);
    func(10,3.14);
    func(3.14 , 10);
    system("pause");
    return 0;
}
```