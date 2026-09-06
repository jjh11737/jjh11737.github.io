# Makefile一些常用的点
基本的内容可见[makefiletutorial](https://makefiletutorial.com/#getting-started)，相当全面了，因此这里仅仅记录我觉得重要会忘的点
## 通配符
这块确实有点记不清...
当我们使用`*` / `%`这种正则表达匹配的方法是，往往需要用在一个`$(wildcard <regular_exp>)`里面使用

- `*`：就是匹配任意个字符。

  - 可以用在`wildcard` / `目标` / `prerequisites`里面
  - 不可以直接当作一个变量的定义！
  - 如果找不到，它就会被当作`*`这个字符！

- `%`：可以用于模式匹配 / 替换

  - Pattern rules:
    匹配任何非空字符串，如：
  
    ```makefile
    %.c:
    	touch $@
    ```
  
    
  
  - static pattern rule：
  
    比如：
    ```makefile
    objects = foo.o bar.o all.o
    all: $(objects)
    	$(CC) $^ -o all
    
    # Syntax - targets ...: target-pattern: prereq-patterns ...
    $(objects): %.o: %.c
    	$(CC) -c $^ -o $@
    
    all.c:
    	echo "int main() { return 0; }" > all.c
    
    # Note: all.c does not use this rule because Make prioritizes more specific matches when there is more than one match.
    %.c:
    	touch $@
    
    clean:
    	rm -f *.c *.o all
    ```
  
    这里的语法结构本身是：`targets : target-pattern: prereq-patterns`
  
  - 字符串替换：
  
    - `$(patsubst pattern, replacement, text)`
      这里就是从`text`里面找到用分割的符合`pattern`的词汇，然后把它们替换为`replacement`的形式
    - `$(\<xx\>: pattern=replacement)`：这里你甚至可以不需要`%`直接代表替换
  
    ```makefile
    foo	:=	a.o b.o c.o
    one	:=	$(patsubst %.o, %.c, $(foo))
    two := 	$(foo:%.o=%.c)
    three := $(foo:.o=.c)
    all:
    	echo $(one)
    	echo $(two)
    	echo $(three)
    ```
  
    

### 自动变量

- `$@`：目标名
- `$?`：所有比目标更新的prerequisite名
- `$^`：所有prerequisites名
- `$<`：第一个prerequisite名





### 指令

- 不要显示这条指令：
  跑指令时，你可以在前面加上`@`告诉make不要显示这条指令
- 指定SHELL：
  默认是bash，但是你甚至可以自己指定
  `SHELL=/bin/bash`
- 错误处理：
  - 加一个`-k`：运行的时候即使有错误也要继续运行
  - 在命令最前面加上`-`：`suppress the error`压制错误不让它显示
  - 加一个`-i`：对全体都适用


### 包含
你可以包含别的`.mk`文件（这里面存储的是约束和规则，不会继承相关target）
