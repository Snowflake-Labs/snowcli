from lib2to3.pgen2.pgen import DFAState
import snowflake.connector


class SnowflakeConnector():
    def __init__(self, account, username, password):
        self.ctx = snowflake.connector.connect(
            user=username,
            password=password,
            account=account
        )
        self.cs = self.ctx.cursor()

    def getVersion(self):
        self.cs.execute('SELECT current_version()')
        return self.cs.fetchone()[0]

    def createFunction(self, name: str, inputParameters: str, returnType: str, handler: str, imports: str, database: str, schema: str, role: str, warehouse: str, overwrite: bool, packages: list[str]):
        self.cs.execute(f'use role {role}')
        self.cs.execute(f'use warehouse {warehouse}')
        self.cs.execute(f'use database {database}')
        self.cs.execute(f'''
        CREATE {"OR REPLACE " if overwrite else ""} FUNCTION {schema}.{name}({inputParameters})
         RETURNS {returnType}
         LANGUAGE PYTHON
         RUNTIME_VERSION=3.8
         IMPORTS=('{imports}')
         HANDLER='{handler}'
         PACKAGES=({','.join(["'{}'".format(package)
                   for package in packages]) if packages else ""})
        ''')

        return self.cs.fetchone()[0]

    def uploadFileToStage(self, file_path, destination_stage, path, role, overwrite):
        self.cs.execute(f'use role {role}')
        self.cs.execute(
            f'create stage if not exists {destination_stage} comment="deployments managed by snowcli"')
        self.cs.execute(
            f'PUT file://{file_path} @{destination_stage}{path} auto_compress=false overwrite={"true" if overwrite else "false"}')
        return self.cs.fetchone()[0]

    def executeFunction(self, function, database, schema, role, warehouse):
        self.cs.execute(f'use role {role}')
        self.cs.execute(f'use warehouse {warehouse}')
        self.cs.execute(f'use database {database}')
        self.cs.execute(f'use schema {schema}')
        self.cs.execute(f'select {function}')
        return self.cs.fetchall()

    def describeFunction(self, function, database, schema, role, warehouse) -> list[tuple]:
        self.cs.execute(f'use role {role}')
        self.cs.execute(f'use warehouse {warehouse}')
        self.cs.execute(f'use database {database}')
        self.cs.execute(f'use schema {schema}')
        self.cs.execute(f'desc FUNCTION {function}')
        return self.cs.fetchall()

    def listFunctions(self, database, schema, role, warehouse, like) -> list[tuple]:
        self.cs.execute(f'use role {role}')
        self.cs.execute(f'use warehouse {warehouse}')
        self.cs.execute(f'use database {database}')
        self.cs.execute(f'use schema {schema}')
        self.cs.execute(f'show USER FUNCTIONS LIKE \'{like}\'')
        return self.cs.fetchall()