import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def test_generation():
    load_dotenv('.env')
    
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    with open('../prompts/presentation_template.txt', 'r', encoding='utf-8') as f:
        template = f.read()
        
    prompt = template.replace("{target_audience}", "성인").replace("{lesson_title}", "창세기 24-33장 테스트").replace("{lesson_content}", "이삭과 리브가 이야기 테스트 내용")
    
    try:
        print("API 호출 시작...")
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOY_CURRICULUM"),
            messages=[
                {"role": "system", "content": "당신은 아름다운 HTML 프리젠테이션 슬라이드를 만드는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        print("API 호출 성공! 응답 길이:", len(response.choices[0].message.content))
        print(response.choices[0].message.content[:200])
    except Exception as e:
        print(f"API 호출 실패: {e}")

if __name__ == "__main__":
    test_generation()
