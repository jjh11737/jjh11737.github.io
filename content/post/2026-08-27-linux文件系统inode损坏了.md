---
title: "linux文件系统inode损坏了"
date: 2026-08-27T00:00:00+08:00
draft: false
tags: ["Linux", "文件系统"]
aliases: ["/posts/2026-08-27-linux文件系统inode损坏了/"]
---

起因是我正在做ysyx,结果不知道为什么一个目录里面有一个文件`\`，尝试删除：
```bash
$ rm -- $'\\'
rm: 无法删除 '\': 输入/输出错误
$ ls -lai
ls: 无法访问 '\': 输入/输出错误
总计 8
340721 drwxrwxrwx 1 root root 4096  8月27日 14:51  .
713168 drwxrwxrwx 1 root root 4096  8月27日 13:51  ..
     ? -????????? ? ?    ?       ?              ? '\'
```
`?`的inode号、`-?????????`的权限、读它直接EIO，这已经不是权限问题，是这个目录项本身在文件系统层面读不出来了。

查了一下，是inode损坏了，我决定先去windows去修复一下，因为：
```bash
$ df -T .
文件系统       类型       1K的块      已用      可用 已用% 挂载点
/dev/nvme0n1p5 fuseblk 625695740 316251624 309444116   51% /mnt/data1
```
`fuseblk`说明这块盘是走FUSE的NTFS（`ntfs-3g`），不是ext4，所以`fsck.ext4`、`debugfs`那套工具一点用都没有。

## 为什么会这样

我事后想了想，大概是这两件事凑在一起：

- fstab里我写的是`defaults`，没开`ntfs-3g`的`windows_names`。不开这个选项它会允许创建Windows不认的文件名（`\`、`:`、`|`这种），而`\`在Windows文件名里本来就不合法，这个名字多半是某次shell转义写错弄出来的
- NTFS没有干净卸载（双系统来回切、或者直接断电），MFT里容易留下不一致的记录，表现就是某些目录项读出来是垃圾

具体是哪一个把这条记录搞坏的，我没法确定。

## 怎么修

Linux侧先试，都要先卸载这块盘：
```bash
sudo umount /mnt/data1
sudo ntfsfix -n /dev/nvme0n1p5   # -n只检查不改
sudo ntfsfix -d /dev/nvme0n1p5   # -d清dirty标记
```
`ntfsfix`只能解决"上次没干净卸载"这种，它不修目录项，所以清完这个`\`多半还在。真正能修的是Windows里的：
```
chkdsk /f X:
```
`/f`修文件系统错误，怀疑有坏道可以加`/r`（会扫盘，很慢）。这一步只能在Windows里做，因为NTFS的修复工具全在那边。

另外这个目录项在Linux下是删不掉的：`rm`要先在目录里查名字，查名字就EIO了，所以别在那儿跟它较劲。

## 记一下

- 别把要在Linux下干活的工程放NTFS上，编译产物、git、软链接、大小写敏感的文件名都会出问题，ysyx那些工程我现在都放ext4
- 挂NTFS时把`windows_names`加上，能挡掉一部分非法名字：
  ```
  UUID=980E115F0E113828 /mnt/data1 ntfs uid=1000,gid=1000,umask=022,windows_names 0 0
  ```
- 双系统切换的时候先在一边正常关机，别硬断
- 看到`?`的inode加EIO，先`dmesg | tail`看文件系统报了什么，再`df -T .`确认盘的类型，别急着`rm -rf`
