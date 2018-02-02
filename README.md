# image_search

image_search 是基于image_match的一个网页搜索相似图片的网站。

* 数据库 MongoDB
* 搜索引擎 ElasticSearch
* Web框架 Tornado
* UI框架 AmazeUI
* 上传框架 WebUploader

#### 运行时：

![TIM截图20180112190438.png](https://i.loli.net/2018/01/12/5a58969de2bc5.png)

![TIM截图20180112190450.png](https://i.loli.net/2018/01/12/5a58969e3af23.png)

![TIM截图20180112190457.png](https://i.loli.net/2018/01/12/5a58969e21382.png)

![TIM截图20180112190519.png](https://i.loli.net/2018/01/12/5a58969de2703.png)

#### 使用说明：

1. 安装 MongoDB数据库和ElasticSearch

   * MongoDB 数据库下载地址：https://www.mongodb.com/download-center?_ga=2.179616164.1252573497.1515040350-689724656.1513848255#atlas
   * 下载`*.msi`文件之后安装默认位置，在D盘创建文件夹 `d:/data/db`
   * ElasticSearch 下载后安装到默认位置即可。下载地址：https://www.elastic.co/downloads/elasticsearch
   * Ps: ElasticSearch 需要安装 jre 的支持

2. 安装python和Python依赖

   Python版本使用3.6，安装地址：https://www.python.org/downloads/

   在windows系统中，需要额外安装packages文件夹中的c++ build tools（**注意此项内容必须安装**）。
    
   地址是：http://landinghub.visualstudio.com/visual-cpp-build-tools
   
   项目安装包地址：https://gitee.com/bxtx/image_search/repository/archive/master.zip

   下载解压后，进入目录：

   ```bash
   $ git clone --recursive https://gitee.com/bxtx/image_search.git  # 拉取项目
   $ virtualenv venv # 添加虚拟目录
   $ venv/Scripts/activate  # 运行虚拟目录 
   (venv)$ pip install -r requestments.txt  # 安装依赖
   # 如果此时安装包出现错误，提示scikit-image等错误，
   # 可以先安装packages包内的whl文件，
   (venv)$ pip install packages/scikit_image-0.13.1-cp36-cp36m-win32.whl  # scikit-image包需要单独安装
   # 然后进入image_match文件夹下安装image_match包
   # 然后继续安装requirements.txt内部的包
   (venv)$ pip install -r requirements.txt 
   # 然后进入image_search文件夹下安装web网站自己的包
   (venv)$ pip install -e .
   # 运行Mongod.exe 和 ElastcSearch.exe 来运行数据库和搜索引擎。
   (venv)$ python search_app/app.py  # 运行网站
   # 注意此时代码中，网站地址是 locolhost:9090
   ```

3. 调整image_match的阈值

   修改`venv/Lib/image_match/signature_database_base.py`文件内第144行`distance_cutoff`参数，可以修改相应的搜索范围阈值。
   ​
4. 删除图片index
   
   开启elasticsearch后，访问locolhost:9200/images 则可以看到相关索引。如果需要清空索引，则使用：
   
   ```bash
   $ curl -XDELETE "locolhost:9200/images*'
   $ {"acknowledged":true} 
   # 获得该提示后，就表示已经删除所有的索引。
   ```
   
5. 功能测试
    ```
    (venv)$ py.test tests/test.py
    $ py.test tests\test.py                                                            
      ============================= test session starts =============================   
      platform win32 -- Python 3.6.2, pytest-3.3.2, py-1.5.2, pluggy-0.6.0              
      rootdir: D:\image_search, inifile:                                        
      plugins: tornado-0.4.5                                                            
      collected 5 items                                                                 
                                                                                  
      tests\test.py .....                                                       [100%]   
                                                                                  
      ========================== 5 passed in 1.62 seconds ===========================   
                                                                                  
    ```
6. 压力测试

    在压力测试中使用的是locust包。
    使用方法：
    ```bash
    (venv) $ locust -f test\l_test.py --host=http://localhost:9090
    ```
    之后登陆 localhost:8089 , 进入测试

#### 文档：
1. Tornado文档 http://tornado-zh.readthedocs.io/zh/latest/webframework.html
2. Pipenv文档 https://docs.pipenv.org/
3. Image_match文档 http://image-match.readthedocs.io/en/latest/docs.html
4. Pymongo文档 https://api.mongodb.com/python/current/
5. AmazeUI文档 http://amazeui.org/getting-started
6. Tornado开发 http://demo.pythoner.com/itt2zh/index.html


#### Tornado 参考项目

1. https://gist.github.com/Integralist/abe4a3e377b4114d08564164e9e8b192
2. https://technobeans.com/2012/09/17/tornado-file-uploads/
3. https://github.com/tornadoweb/tornado/blob/master/demos/blog/blog.py
