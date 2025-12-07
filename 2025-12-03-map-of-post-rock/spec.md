
# 2025-12-07 第一版

## 获取艺术家信息数据

写一个程序执行如下流程

1. 步骤一：根据音乐标签来获取艺术家列表，
    1. 分多次请求，直到返回结果中topartists字段下 artist属性数组的长度小于 limit参数。结果按照原始结果保存到本地，即若干个json文件，每个文件对应一次成功的请求结果。
    2. api为 http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag=post-rock&api_key=API_KEY&format=json&limit=1000&page=1
2. 步骤二：根据艺术家名字来获取艺术家信息 
    1. 对第一步中的所有艺术家名字按照如下api进行请求。保存为json文件，即第一步中的每个艺术家列表文件对应一个艺术家信息列表文件。
    2. http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=Mogwai&api_key=API_KEY&format=json


## 计算相似度

完成如下任务

1. 读取一个json文件（以 artist_details_page_1.json 为例），抽取数据json中的artist对象数组，每个artist对象仅抽取其下的bio.summary字段，然后 使用硅基流动的接口或者sdk来计算summary字段字符串的embedding。 
2. 挑选合适的本地向量数据库来存储embedding数据和 artist数据。
3. 对于每个artist，根据 embedding余弦相似度来获取最近的10个艺术家，并且要求相似度必须大于0.3，将相似结果 存储在一个本地日志文件。


## 画图

参考资料
1. [MiqG/leiden\_clustering: Cluster your data matrix with the Leiden algorithm.](https://github.com/MiqG/leiden_clustering?tab=readme-ov-file)
    1. 聚类获取两层社区聚类数据，其中包括了社区的边界。
2. 利用 ngraph.forcelayout 来画图
    1. 所有图一起进行聚类已经完成，其中定义了不同的距离、弹性系数等。



# 第二版


1. 第一版 的相似度计算结果表现并不好，至今发现的问题
    1. 同名艺术家，一个使用拼音，一个使用中文
    2. 


