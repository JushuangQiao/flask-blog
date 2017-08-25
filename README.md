# blog
一个基于flask创建的blog系统
前端界面部分参考了https://github.com/ifwenvlook/blog

## 安装步骤
### 1. 安装 virtualenv
### 2. 安装虚拟环境：virtualenv venv
### 3. 进入虚拟环境路径：cd venv/lib/python2.7/site-packages/
### 4. 拉取代码：git clone git@github.com:JushuangQiao/blog.git
### 5. 进入虚拟环境：source bin/activate
### 6. 安装依赖包: pip install -r requirements.txt
### 7. 配置数据库: setting下的config文件
### 8. 生成数据库，虚拟环境下执行: python manage.py shell,然后输入db.create_all()

### 本地前台运行: python manage.py server
### 本地后台运行: nohup python manage.py server  >/Users/qiaojushuang/codes/MyCodes/blog/running_error.log 2>&1 &

### 部署上线: 暂缺