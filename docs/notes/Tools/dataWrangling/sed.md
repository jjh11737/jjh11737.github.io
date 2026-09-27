# sed
> 参考了[这个](https://www.grymoire.com/Unix/Sed.html)
sed - (**S**tream **ED**itor)文本筛选和格式转换的流式编辑器，基本来说就是读取输入文本然后一行行按规则处理

sed当然不只是一个替换工具，它还可以用来：

- 删除：
  ```bash
  sed '3d' file
  ```

  

### 最基础的命令:

##### `s `

```bash
sed s/day/night/ <old >new
# or
sed s/day/night old >new
```
整体来说，一个替换的命令有4个部分：

s           替换指令
/../../     Delimiter也就是划分
day         Regular Expression Pattern Search Pattern(regex)
night       替换字符串 

s后面的就是Delimiter，它往往是一个`/`，就像vi和ed一样，但是如果你要替换一个路径名那么你可以用`\`来转义，就像这样：
```bash
sed 's/\/usr\/local\/bin/\/common\/bin/' <old >new
```
但是这太丑了...而且也不好读，你最好还是用别的比如`_`：
```bash
sed 's_/usr/local/bin_/common/bin_' <old >new
```
> 实际上什么字符都可<以作为Delimiter...

##### `&`：
有时候你想复用你通过regex找到的字符串，此时就可以用`&`代指它：
```bash
sed 's/[a-z]*/(&)/' <old >new 
sed 's/[0-9a-z]*/& &/'          # 重复2遍
```
##### `/g`:

全局替换

##### 保存不被替换`\1`:

使用`\1`保存匹配到的第一个字符串，当然还有`\2` ... `\9`之类的



##### `/w`:


##### `/I`:
加在最后面，让这个pattern变成大小写不敏感的



##### 使用多条指令`-e`：
每条指令之前都要加上`-e`



