# 折腾VPS

想弄我就弄了，因为是小白，所以还是挑了最便宜的RackNerd的服务器，512MB / 单核 / 10GB SSD

登录后第一步自然是先配置好工具了，而没想到居然很麻烦... 原因是RackNerd只允许最新的是Debian11的版本，而偏偏官方已经不支持了，一开始apt安装报404，所以折腾了半天最后我换成了archive作为源（虽然这不是很好的方案...）

然后就是限制访问了，先创建了一个普通用户给予sudo权限(`usermod -aG sudo xxx`，不确定的话先登录这个账户看看`sudo whoami`)，给它配置好ssh key，以及别忘了给对应ssh的目录的访问权限，否则根本登录不了... 比如我这里就是忘记了：
```bash
chown -R jjh:jjh /home/jjh/.ssh
chmod 700 /home/jjh/.ssh
chmod 600 /home/jjh/.ssh/authorized_keys
```

然后修改`/etc/sshd_config`，确保禁用`PasswordAuthenticatioin` / `PermitRootLogin`这两个，都设为no