import os
from azure.data.tables import TableServiceClient
from dotenv import load_dotenv

def clear_presentations():
    load_dotenv()
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        print("연결 문자열이 없습니다.")
        return
        
    try:
        service_client = TableServiceClient.from_connection_string(conn_str)
        
        for table_name in ["CurriculumPresentation", "CurriculumMaterials"]:
            try:
                table_client = service_client.get_table_client(table_name)
                entities = list(table_client.query_entities(""))
                print(f"[{table_name}] 총 {len(entities)}개의 캐시를 삭제합니다...")
                
                for e in entities:
                    table_client.delete_entity(e['PartitionKey'], e['RowKey'])
                print(f"[{table_name}] 삭제 완료!")
            except Exception as e:
                print(f"[{table_name}] 에러 발생: {e}")
                
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    clear_presentations()
