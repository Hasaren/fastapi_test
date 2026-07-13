from database import execute_sql, subway_engine, table_count

def create_traffic_station_summary() -> None:
    """
    AVG("인원수")::numeric 
        --> AVG 결과값을 numeric타입으로 변환해라.
            PostgreSQL 문법
            CAST(AVG("인원수") AS numeric)이 표준 SQL문법    
    """
    execute_sql(
        subway_engine,
        '''
        DROP TABLE IF EXISTS traffic_station_summary;

        CREATE TABLE traffic_station_summary AS 
        SELECT
            "역번호" AS station_no,
            "역명" AS station_name,
            COUNT(*) AS row_count,
            SUM("인원수") AS total_passengers,
            ROUND(AVG("인원수")::numeric, 2) AS avg_passengers
        FROM subway_raw
        GROUP BY "역번호", "역명";

        CREATE INDEX idx_traffic_station_summary_total
        ON traffic_station_summary(total_passengers DESC);
        '''
    )
    print('[batch] 지하철 시간대별 집계 완료: traffic_subway_hourly_summary')


if __name__ == '__main__':
    count = table_count(subway_engine,"subway_raw")
    print(count)
    create_traffic_station_summary()
    print('[batch] 배치 처리 완료')