from neo4j import GraphDatabase, Driver
import config 

_driver : Driver | None = None 

def get_driver() -> Driver:
    global _driver 

    if  _driver is None : 
        _driver = GraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
        )

    return _driver

def close_driver() -> None:
    global _driver 

    if _driver is not None : 
        _driver.close()
        _driver = None