# Vim
> 实际上你完全可以看`:h user-manual`里面的介绍...我这里只是抄了手册
## Vim 到底是什么
只是一个编辑器？





## cheetsheet
- dd: 删除整行
- dw: 删除一个单词
- ci
- J: 把光标所在这行和下一行连在一起
- CTRL-R: redo (和`u`相反)
- O: 光标上面弄出来一行 (和`o`相反)
- 数字 + 操作: 重复对应次数的操作
### 移动
#### 单词移动
- w: move the cursor forward one word (or 9w) 
- b: move the cursor back to the previous word's beginning 
- e: move to the next end of a word 
- ge: move to the previous end of a word
#### 移动到一个字符
- f`<ch>`: 在本行查找一个字符然后把光标移到第一个它出现的地方(这对中文同样有效)，同样可以加上数字在前面决定我们找到的是第几个
#### 括号匹配
- %: 如果光标放在`(`上它就会跳转到与之匹配的`)`上面（这对`{}` / `[]`同样有效）
#### 移动到指定的行
- G: 文件末尾
- `<num>` G: 跳转到`<num>`行的位置 
- gg: 文件开头
#### 我在哪？
- CTRL-G: 告诉你现在在什么文件的何处
- :set number: 展示行号
#### 查找
- /: 查找，不过是从前往后
- ?: 查找，从后往前
- n: 往后找下一个符合的
- N：往前找下一个符合的
> 注意: `.*[]^%/\?~$`往往和regex有关或者是指令相关，你需要转义`\`
- :set ingnorecase: 忽略大小写
- :set noignorecase: 恢复大小写区分


### 寄存器
- ': 查看寄存器
