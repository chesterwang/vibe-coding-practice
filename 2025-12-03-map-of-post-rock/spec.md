

## 获取艺术家信息数据

写一个程序执行如下流程

1. 步骤一：根据音乐标签来获取艺术家列表，
    1. 分多次请求，直到返回结果中topartists字段下 artist属性数组的长度小于 limit参数。结果按照原始结果保存到本地，即若干个json文件，每个文件对应一次成功的请求结果。
    2. api为 http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag=post-rock&api_key=API_KEY&format=json&limit=1000&page=1
2. 步骤二：根据艺术家名字来获取艺术家信息 
    1. 对第一步中的所有艺术家名字按照如下api进行请求。保存为json文件，即第一步中的每个艺术家列表文件对应一个艺术家信息列表文件。
    2. http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=Mogwai&api_key=API_KEY&format=json
