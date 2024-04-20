from typing import List

from sqlalchemy import DDL

from core.data_base.orm import CoreOrmTemplate, MAIN_SCHEMA


def trigger_upd_server_time(model: type[CoreOrmTemplate], include_cols: List[str] = None,
                            exclude_cols: List[str] = None) -> DDL:
    """Тригер на update server_time любой строки"""
    all_columns = model.__table__.columns.keys()
    trigger_columns = all_columns
    if exclude_cols:
        trigger_columns = [col for col in all_columns if col not in exclude_cols]

    if include_cols:
        trigger_columns = [col for col in all_columns if col in include_cols]

    ddl = f"CREATE OR REPLACE TRIGGER tr_{model.__tablename__} BEFORE UPDATE "

    if trigger_columns != all_columns:
        ddl += f"OF {', '.join(trigger_columns)} "
    ddl += f"ON {model.__table_args__['schema']}.{model.__tablename__} "\
           f"FOR EACH ROW EXECUTE PROCEDURE {model.__table_args__['schema']}.trf_update_server_time();"
    return DDL(ddl)


def trf_insert_to_hist(origin_model: type[CoreOrmTemplate], history_model: type[CoreOrmTemplate]) -> DDL:
    """
    Функция записывающая строку из оригинальной таблицы в историческую
    """
    origin_schema = origin_model.__table_args__['schema']
    hist_schema = history_model.__table_args__['schema']
    table_columns = origin_model.__table__.columns.keys()
    origin_tb_name = origin_model.__tablename__
    history_tb_name = history_model.__tablename__

    insert_part = '(' + ', '.join([col for col in table_columns]) + ')\n VALUES (' + \
                  ', '.join(['NEW.' + col for col in table_columns]) + ')'

    ddl = f"""
    CREATE OR REPLACE FUNCTION {origin_schema}.trf_{origin_tb_name}__to_hist()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $func$
    BEGIN
        INSERT INTO {hist_schema}.{history_tb_name} {insert_part};
        RETURN OLD;
    END
    $func$;
    """
    return DDL(ddl)


def trigger_to_history(origin_model: type[CoreOrmTemplate], include_cols: List[str] = None, exclude_cols: List[str] = None):
    """
    Тригер, который вызывает запись в историческую таблицу
    """
    all_columns = origin_model.__table__.columns.keys()
    origin_schema = origin_model.__table_args__['schema']
    origin_tb_name = origin_model.__tablename__

    trigger_columns = all_columns
    if exclude_cols:
        trigger_columns = [col for col in all_columns if col not in exclude_cols]

    if include_cols:
        trigger_columns = [col for col in all_columns if col in include_cols]

    ddl = f"CREATE OR REPLACE TRIGGER tr_{origin_model.__tablename__}_history AFTER INSERT OR UPDATE "

    if trigger_columns != all_columns:
        ddl += f"OF {', '.join(trigger_columns)} "

    ddl += f"ON {origin_schema}.{origin_tb_name} " \
           f"FOR EACH ROW EXECUTE PROCEDURE {origin_schema}.trf_{origin_tb_name}__to_hist();"
    return DDL(ddl)


trf_update_server_time = DDL(
    f"CREATE FUNCTION {MAIN_SCHEMA}.trf_update_server_time() "
    "RETURNS TRIGGER AS $$ "
    "BEGIN "
    "NEW.server_time := now(); "
    "RETURN NEW; "
    "END; $$ LANGUAGE PLPGSQL"
)
