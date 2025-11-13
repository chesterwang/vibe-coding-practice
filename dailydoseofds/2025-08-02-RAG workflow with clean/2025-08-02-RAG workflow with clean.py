
from llama_index.core import Settings
from llama_index.llms.siliconflow import SiliconFlow

llm = SiliconFlow(api_key="sk-euzfmfomtaknocligtpsfvmqtvcljqfodaxizsukudmouzgt",
            model = "Qwen/Qwen3-30B-A3B-Thinking-2507"
            )

Settings.llm = llm


from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.core.query import NLSQLTableQueryEngine

db_path = "city_database.sqlite"
engine = create_engine(f"sqlite:///{db_path}")
sql_database = SQLDatabase(engine)

sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables = ["city_stats"]
)




