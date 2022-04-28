C/C++读书笔记
1，引用和指针的区别

　　指针有自己的内存空间，是间接访问，别名是直接访问；

　　引用只能指向一块内存空间，而指针可以变化，引用类似于 int* const p，p的指向是不会变化 

　　引用类似于长指针，需要初始化，不能被改变，不能指向NULL

3，一个句柄是指使用的一个唯一的整数值，即一个四字节长的数值，来标志应用程序中的不同对象和同类对象中的不同的实例，句柄是一种指向指针的指针

4，在C/C++的STL模板中，入堆push_heap(big, big + (++ bCount) , myMore);出堆：pop_heap(big, big + bCount-- , myMore);需要包含头文件：#include <algorithm>;

5，在C＋＋中，你可以用extern "C"告知C＋＋编译器去调用一个C的函数。

6，C++为了实现多态，会在编译的时候将函数名称和参数联合起来生成一个新函数，而C就不会，这样C++中使用C函数可能不能链接obj文件，加上extern "C"，告诉编译器，不要给这个函数改名

7，wstring是宽char，Unicode编码，一般情况下一个字符占两个字节大小；string是窄char，AscII编码，一个字符占一个字节大小

8，格式化C++的字符串可以用Boost库，在vs下需要编译，然后加入到vs的path中，下面这段代码就可以使用了
```
#include <iostream> 
#include <boost/format.hpp> 
 
using namespace std; 
using boost::format; 
using boost::io::group; 
  
int main() 
{ 
  cout << format("(x,y) = (%+5d,%+5d) \n") % -23 % 35; 
  cout << format("(x,y) = (%|+5|,%|+5|) \n") % -23 % 35; 
  cout << format("(x,y) = (%1$+5d,%2$+5d) \n") % -23 % 35; 
  cout << format("(x,y) = (%|1$+5|,%|2$+5|) \n") % -23 % 35; 
    
  return 0; 
} 

```

9，vectors在array尾部附加元素或移除元素均非常快速，但是在中部或頭部安插元素就比較費時；deque只不过是两头可以插入删除的vector，支持随机访问和快速插入删除，头和尾插入都非常快；list是双向链表；PriorityQueue（优先队列）实质是用堆来实现的，可能需要重载<号

10，遍历时可能需要以只读的方式遍历，如set<int>::const_iterator it;

11，vector如果超过元素个数限制，将会重新配置内部记忆体，references，pointer，iterator等都会失效，非常影响效率，所以知道capacity很重要

12，list可以使用list.sort([fun])对元素排序，默认以<号排序，也可以使用fun函数排序，同样的还有unique，merge，使用list.reverse()可以反序

13，set是有序的，初始化的时候可以set（fun），其中fun对指导排序顺序，multiset也是一样，set.erase()释放元素，对于set来说返回0或者1

14，typedef set<int,greater<int>> IntSet：创建一个带大于比较器的set，降序排列，默认的是set<int,less<int>>升序排列

15，map增加元素的时候可以用std：：make_pair的方式

16，在map中删除一个元素：使用find寻找，得到迭代器之后，使用erase释放，这是迭代器已经不能用了，指向的空间已经被释放了

17，和所有「以節點為基礎」的容器相似，只要元素還是容器的㆒部分，list 就不會令指向那些元素的迭代器失效。vectors 則不然，㆒旦超過其容量，它的所有iterators 、pointers、references 都會失效；執行安插或移除動作時，也會令一部分iterators、pointers、references失效。至於deque，當它的大小改變，所有iterators 、pointers、references 都會失效。

18，hashtable查找比二叉查找还要快5-10倍

19，unsigned int和int相加之后，int转换成unsigned int

20，#include <**.h>和#include “**.h"前者从系统库搜索，后者从用户库搜索

21，判断一段程序是C编译的还是C++编译的：C++编译的定义了_cplusplus，C定义了_STDC_变量

22，atexit(functionName)是main()函数执行完之后执行的函数

23，效率方面x++>x+=1>x=x+1

24，num[]="123456"，sizeof（num）= 7，需要加上'\0'，需要注意的是，如果num通过参数传递到某一个函数，如fun(char *num)中，再执行sizeof(num)，那么num就相当于一个指针了，对于32位机器，就变成了4，但是strlen(num) = 6，struct中变量类型需要对齐，即使是一个空类，sizeof大小依然是1；

25,()，[]，->是左结合的，运算级别最高，指针运算法*是右结合的，运算级别没有前面四个高

26，位运算右移时，如果是负数，左边是补1的

27，在一个类里面如果有：const T& top(void) const前一个const表示返回的是常量，不可改变；后一个const表示这个函数不会改变这个类的数据成员；

28，位运算
```
　　& 按位与 如果两个相应的二进制位都为1，则该位的结果值为1，否则为0

　　| 按位或 两个相应的二进制位中只要有一个为1，该位的结果值为1

　　^ 按位异或 若参加运算的两个二进制位值相同则为0，否则为1

　　~ 取反 ~是一元运算符，用来对一个二进制数按位取反，即将0变1，将1变0

　　<< 左移 用来将一个数的各二进制位全部左移N位，右补0

　　>> 右移 将一个数的各二进制位右移N位，移到右端的低位被舍弃，对于无符号数，高位补0

 ```

29，char *info = "abcde"; info[3] = 'k';前面的运算运行的时候会出错，可以通过编译链接。我理解的错误的原因：前一句是有一个指针指向了一个常量，然后修改那个常量，后面肯定出错了....正确的做法：char info[strlen("abcde")]; strcpy(info , "abcde");

30，c++文件打开：freopen("in", "r", stdin);freopen("out.txt", "w", stdout);，文件从in里面读取，写出到out.txt中去

31，template的用法
```
template <class T1 , class T2>
int function(T1 a , T2 b) 
{
　　typedef typename vector<T1>::iterator iterator1;
　　typedef typename vector<T2>::iterator iterator2;
}
```
32，new和malloc的区别：new会执行构造函数，自动分配存储空间，不用sizeof制定，自动返回制定类型指针，不用malloc那样强制类型转换，new和delete可以重载，属于运算符，malloc和free属于库函数

33，虚基类是为了防止子类从多个父类中继承到同样的类成员，及环形继承
```
class Son : virtual public Father{
   //..... 
};
``` 
34，保护继承：父类中public和protected的成员在子类中变成protected的，private的依然是不可见的

35，继承默认方式是私有继承

36，如果父类中有构造函数，但是没有默认构造函数，子类中必须显示的调用父类的构造函数

37，多态中，虚函数的使用
```
#include <iostream>
#include <set>
#include <vector>
#include <stack>
#include <deque>
#include <stdio.h> 
#include <list>
#include <algorithm>
#include <assert.h>

using namespace std;

class Father
{
public:
    virtual void say()
    {
        cout << "base" << endl;
    }
};

class Son1: public Father
{
public:
    void say() //virtual可加可不加，只是Father中一定要加
    {
        cout << "son1" << endl;
    }
};

class Son2: public Father
{
public:
    void say() //virtual可加可不加，只是Father中一定要加
    {
        cout << "son2" << endl;
    }
};

int main()
{

    Father *c[3]; //三个指针

    c[0] = new Father();
    c[1] = new Son1();
    c[2] = new Son2();

    (*c[0]).say();
    (*c[1]).say();
    (*c[2]).say();

    system("pause");

    return 0;
}
```
如果Father中没有virtual，输出三个base，如果Father中有virtual，输出base，son1，son2.构造函数，静态成员不能是虚函数，但是析构函数可以是虚函数

38，纯虚函数的写法，拥有纯虚函数的类被称为抽象基类
```
virtual void open() = 0;
``` 

39，C++的多态体现在运行时多态和编译时多态，编译时多态就是指运算符重载和函数重载，而运行时多态通过继承和虚函数实现

40，A是一个什么内容都没有的类，sizeof（A）= 1

41，以下代码分别输出6,4，前面的6指的是字符串的长度，后面的4指的是地址的长度。

```
    char aa[] = "Hello";

    char * p = aa;

    cout << sizeof(aa) << endl;

    cout << sizeof(p) << endl;
```
在数组作为参数传递到函数中时，数组则退化为指针，比如，在下面的输出就是4
```
void fss(char aa[])
{
    cout << sizeof(aa) << endl;
}
 
```
42，隐藏有两种，一种是派生类中函数名一样，但是参数列表不一样，子类把父类的函数隐藏；一种是派生类中函数名一样，参数列表也一样，同样将父类同名方法隐藏，造成不能访问，参加下面的例子：
```
#include <iostream>
#include <set>
#include <vector>
#include <stack>
#include <deque>
#include <stdio.h> 
#include <list>
#include <algorithm>
#include <assert.h>

using namespace std;

class Father
{
public:
    void say(char A)
    {
        cout << "base" << endl;
    }
};

class Son1: public Father
{
public:
    void say() 
    {
        cout << "son1" << endl;
    }
};

int main()
{

    Son1* s1 = new Son1();
    s1->Father::say('D');

    system("pause");

    return 0;
}
``` 
输出是2
```
int main()
{
    int int1 = 1 , int2 = 2;

    const int p = int2;

    int2 = 3;

    cout << p << endl;

    system("pause");

    return 0;
}
```

45，引入头文件或者extern可以使用在别的文件中定义的全局变量，前者在编译时检查，后者在链接时检查

46，全局静态变量和全局变量的存储方式是一样的，但是全局静态变量的作用域只在本原文件中

47，char 1个字节，float 4个字节，double8个字节，long也是8个字节，在vc里面：int 4个字节，在tc里面：int 2个字节。

48，int *a[10]：十个指向int的指针；int (*a)[10]：一个指向int a[10]的指针；int (*a[10])(int):十个函数指针，指向的函数是 int fun(int)型的；（主要是记住*a[10]表示十个指针，[]左结合，一级运算符，*右结合，二级运算符)

49，C++中，static的三个作用：1，加了static的全局变量对其他源文件隐藏；2，保持变量内容的持久，并且只有一份；3，static的变量初始化为0

50，无符号型加有符号型会统一转换成无符号型

51，下面两个式子中，1是指向常量的，堆栈中并没有new出一块新的内存出来，只不过是str1指向静态存储区，这一静态存储区存着“abc”，2中是有在堆栈中申请内存的，并执行了new函数，这一块内存存着“abc”
```
char *str1 = "abc";
char str2[] = "abc";
```